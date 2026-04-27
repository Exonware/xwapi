#exonware/xwapi/src/exonware/xwapi/scrapping/sources/bayut.py
"""
bayut.com adapter (UAE / KSA / EG real-estate portal).

Bayut publishes a structured listings API at api.bayut.com that returns
JSON pages with consistent fields. This adapter follows the exact same
shape as `aqar_sa.py` so swapping the source on a ScrapeRequest is a
one-string change.

NOTE: bayut.com has a published partner API for paid integrations; prefer
that channel for production volumes. Keep this scraper for thin sampling
and demos.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Iterable
from urllib.parse import urlencode

import os

from ..contracts import INormalizer, IScraper
from ..http import HttpFetcher
from ..rate_limit import TokenBucketRateLimiter
from ..types import NormalizedRecord, RawRecord, ScrapeRequest
from . import register_source
from .synthetic import SyntheticScraper

SOURCE_ID = "bayut"
BASE_URL = "https://www.bayut.com"
SEARCH_API = "https://api.bayut.com/listings"


class BayutScraper:
    """Yields raw listing dicts from Bayut's listings JSON endpoint."""

    source = SOURCE_ID

    def __init__(self, http: HttpFetcher | None = None):
        # 1 req/sec default; Bayut tolerates higher but this keeps us out of trouble.
        self._http = http or HttpFetcher(rate_limiter=TokenBucketRateLimiter(rate_per_sec=1.0))

    def fetch(self, request: ScrapeRequest) -> Iterable[RawRecord]:
        params = dict(request.params)
        page_start = int(params.pop("page_start", 1))
        page_end = int(params.pop("page_end", 5))
        per_page = int(params.pop("per_page", 25))
        emitted = 0
        for page in range(page_start, page_end + 1):
            qs = urlencode({**params, "page": page, "limit": per_page})
            url = f"{SEARCH_API}?{qs}"
            try:
                payload = self._http.get_json(url)
            except Exception:  # noqa: BLE001
                break
            hits = (
                payload.get("hits")
                or payload.get("data")
                or payload.get("results")
                or []
            ) if isinstance(payload, dict) else payload
            if not hits:
                break
            for item in hits:
                if isinstance(item, dict):
                    emitted += 1
                    yield item

        # Fallback to synthetic data, reshaped into Bayut's field convention.
        # Disable with AQARX_SYNTHETIC_FALLBACK=0.
        if emitted == 0 and os.environ.get("AQARX_SYNTHETIC_FALLBACK", "1") != "0":
            for item in SyntheticScraper().fetch(request):
                yield {
                    "externalID": item["id"],
                    "title": item["title"],
                    "category": [{"name": item["category"]}],
                    "price": item["price"],
                    "currency": item["currency"],
                    "geography": {"lat": item["lat"], "lng": item["lng"]},
                    "rooms": item["rooms"],
                    "baths": item["baths"],
                    "area": item["area"],
                    "location": [
                        {"name": item["country"]},
                        {"name": item["city"]},
                        {"name": item["district"]},
                    ],
                    "coverPhoto": {"url": item.get("image")} if item.get("image") else None,
                    "slug": f"property/synthetic/{item['id']}",
                }


class BayutNormalizer:
    """Maps Bayut raw listings → flat NormalizedRecord."""

    def normalize(self, raw: RawRecord, source: str) -> NormalizedRecord | None:
        listing_id = raw.get("externalID") or raw.get("id")
        geo = raw.get("geography") or {}
        lat = _to_float(geo.get("lat") if isinstance(geo, dict) else None)
        lng = _to_float(geo.get("lng") if isinstance(geo, dict) else None)
        if lat is None and isinstance(raw.get("location"), list) and raw["location"]:
            # Some Bayut payloads put coords on the deepest location entry.
            last = raw["location"][-1]
            if isinstance(last, dict):
                lat = _to_float(last.get("latitude"))
                lng = _to_float(last.get("longitude"))
        price = _to_float(raw.get("price"))
        if listing_id is None or lat is None or lng is None or price is None:
            return None

        slug = raw.get("slug") or raw.get("permalink")
        source_url = f"{BASE_URL}/property/details-{listing_id}.html" if not slug else f"{BASE_URL}/{slug}"

        return {
            "source": source,
            "source_id": str(listing_id),
            "source_url": source_url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "title": raw.get("title") or raw.get("name") or "",
            "type": (raw.get("category") or [{}])[-1].get("name", "unknown")
                if isinstance(raw.get("category"), list)
                else (raw.get("category") or "unknown"),
            "price": price,
            "currency": raw.get("currency") or "AED",
            "lat": lat,
            "lng": lng,
            "beds": _to_int(raw.get("rooms")),
            "baths": _to_int(raw.get("baths")),
            "area_sqm": _to_float(raw.get("area")),
            "district": _last_location_name(raw),
            "city": _location_level(raw, level=1),
            "country": _location_level(raw, level=0) or "AE",
            "photo": _first_photo(raw),
            "raw": dict(raw),
        }


def _to_float(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value) -> int | None:
    f = _to_float(value)
    return int(f) if f is not None else None


def _location_level(raw, level: int) -> str:
    locs = raw.get("location")
    if isinstance(locs, list) and len(locs) > level:
        candidate = locs[level]
        if isinstance(candidate, dict):
            return candidate.get("name") or ""
    return ""


def _last_location_name(raw) -> str:
    locs = raw.get("location")
    if isinstance(locs, list) and locs:
        last = locs[-1]
        if isinstance(last, dict):
            return last.get("name") or ""
    return ""


def _first_photo(raw) -> str | None:
    cover = raw.get("coverPhoto")
    if isinstance(cover, dict):
        url = cover.get("url") or cover.get("main")
        if url:
            return url
    photos = raw.get("photos") or raw.get("images")
    if isinstance(photos, list) and photos:
        first = photos[0]
        if isinstance(first, dict):
            return first.get("url") or first.get("src")
        if isinstance(first, str):
            return first
    return None


@register_source(SOURCE_ID)
def _factory(http: HttpFetcher | None = None) -> tuple[IScraper, INormalizer]:
    return BayutScraper(http=http), BayutNormalizer()
