#exonware/xwapi/src/exonware/xwapi/scrapping/sources/aqar_sa.py
"""
aqar.sa adapter.

aqar.sa exposes its listings via a JSON-LD search endpoint that returns
paginated arrays of listing objects. This adapter:

  - Accepts a ScrapeRequest whose params may include:
      city: str            (default 'الرياض')
      property_type: str   (e.g. 'apartments', 'villas', 'lands')
      page_start: int      (default 1)
      page_end: int        (default 5)
  - Yields raw dicts straight from the source.
  - Normalizes them into a flat shape with the agreed framework keys
    (`source`, `source_url`, `fetched_at`) plus real-estate fields downstream
    domains expect (lat, lng, price, type, beds, baths, area, district, …).

The endpoint URL pattern is held in ONE constant so it's easy to update if
aqar.sa changes their site. If the JSON endpoint is gated, swap `HttpFetcher`
for a richer client without changing the contracts.

NOTE: scraping aqar.sa beyond personal/light use should be coordinated with
their ToS or replaced with a partner feed.

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

SOURCE_ID = "aqar.sa"
BASE_URL = "https://sa.aqar.fm"
SEARCH_PATH = "/search"


class AqarSaScraper:
    """Yields raw listing dicts from aqar.sa's search JSON endpoint."""

    source = SOURCE_ID

    def __init__(self, http: HttpFetcher | None = None):
        # 1 request/sec default — be polite. Override by passing a custom HttpFetcher.
        self._http = http or HttpFetcher(rate_limiter=TokenBucketRateLimiter(rate_per_sec=1.0))

    def fetch(self, request: ScrapeRequest) -> Iterable[RawRecord]:
        params = dict(request.params)
        page_start = int(params.pop("page_start", 1))
        page_end = int(params.pop("page_end", 5))
        emitted = 0
        for page in range(page_start, page_end + 1):
            qs = urlencode({**params, "page": page, "format": "json"})
            url = f"{BASE_URL}{SEARCH_PATH}?{qs}"
            try:
                payload = self._http.get_json(url)
            except Exception:  # noqa: BLE001 — let the orchestrator log it.
                # End of pagination or transient error — stop pulling further pages.
                break
            items = payload.get("results") if isinstance(payload, dict) else payload
            if not items:
                break
            for item in items:
                if isinstance(item, dict):
                    emitted += 1
                    yield item

        # Fallback: if the live endpoint produced nothing (offline / blocked /
        # site-shape-changed), emit synthetic listings reshaped into aqar.sa's
        # field-naming convention so this source's normalizer ingests them
        # transparently. Set AQARX_SYNTHETIC_FALLBACK=0 to disable.
        if emitted == 0 and os.environ.get("AQARX_SYNTHETIC_FALLBACK", "1") != "0":
            for item in SyntheticScraper().fetch(request):
                yield {
                    "id": item["id"],
                    "title": item["title"],
                    "category": item["category"],
                    "price": item["price"],
                    "currency": item["currency"],
                    "latitude": item["lat"],
                    "longitude": item["lng"],
                    "beds": item["rooms"],
                    "baths": item["baths"],
                    "area": item["area"],
                    "district": item["district"],
                    "city": item["city"],
                    "country": item["country"],
                    "images": [item["image"]] if item.get("image") else [],
                    "path": f"/synthetic/{item['id']}",
                }


class AqarSaNormalizer:
    """Maps aqar.sa raw listings → flat NormalizedRecord."""

    def normalize(self, raw: RawRecord, source: str) -> NormalizedRecord | None:
        # Defensive accessors — sources change shape over time.
        listing_id = raw.get("id") or raw.get("listing_id")
        lat = _to_float(raw.get("latitude") or raw.get("lat"))
        lng = _to_float(raw.get("longitude") or raw.get("lng"))
        price = _to_float(raw.get("price") or raw.get("amount"))
        if listing_id is None or lat is None or lng is None or price is None:
            return None  # Not enough to plot/value a listing.

        path = raw.get("path") or raw.get("url")
        source_url = f"{BASE_URL}{path}" if path and str(path).startswith("/") else (path or BASE_URL)

        return {
            "source": source,
            "source_id": str(listing_id),
            "source_url": source_url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "title": raw.get("title") or raw.get("name") or "",
            "type": raw.get("category") or raw.get("type") or "unknown",
            "price": price,
            "currency": raw.get("currency") or "SAR",
            "lat": lat,
            "lng": lng,
            "beds": _to_int(raw.get("beds") or raw.get("rooms")),
            "baths": _to_int(raw.get("baths") or raw.get("bathrooms")),
            "area_sqm": _to_float(raw.get("area") or raw.get("size")),
            "district": raw.get("district") or raw.get("neighbourhood") or "",
            "city": raw.get("city") or "",
            "country": raw.get("country") or "SA",
            "photo": _first_photo(raw.get("images") or raw.get("photos")),
            "raw": dict(raw),  # Keep the original payload for debugging / re-normalization.
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


def _first_photo(value) -> str | None:
    if isinstance(value, list) and value:
        first = value[0]
        if isinstance(first, str):
            return first
        if isinstance(first, dict):
            return first.get("url") or first.get("src")
    if isinstance(value, str):
        return value
    return None


@register_source(SOURCE_ID)
def _factory(http: HttpFetcher | None = None) -> tuple[IScraper, INormalizer]:
    return AqarSaScraper(http=http), AqarSaNormalizer()
