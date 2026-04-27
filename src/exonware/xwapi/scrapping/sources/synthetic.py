#exonware/xwapi/src/exonware/xwapi/scrapping/sources/synthetic.py
"""
Synthetic source adapter — generates plausible real-estate listings within
a configurable bounding box. Useful for:

  - Demos / offline development where real upstreams are blocked.
  - Load testing dedup + storage paths without hammering external sites.
  - Filling in coverage gaps while a real adapter is stubbed.

Accepted ScrapeRequest params:
  bbox: 'south,west,north,east' (default = Riyadh)
  count: how many records to emit (default 25)
  seed: deterministic RNG seed (default = wall clock)

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
"""
from __future__ import annotations
import random
from datetime import datetime, timezone
from typing import Iterable

from ..contracts import INormalizer, IScraper
from ..types import NormalizedRecord, RawRecord, ScrapeRequest
from . import register_source

SOURCE_ID = "synthetic"

DEFAULT_BBOX = (24.65, 46.55, 24.90, 46.85)  # Riyadh
TYPES = ("apartment", "villa", "townhouse", "office", "land")
DISTRICTS = (
    "Al-Olaya", "Al-Malqa", "Hittin", "Al-Yasmin", "Al-Sahafa", "KAFD",
    "Al-Aqiq", "Diplomatic Quarter", "Al-Muruj", "Al-Nakheel", "Al-Wadi",
    "Al-Ghadir", "Al-Naseem", "Al-Falah", "Al-Wahah", "Al-Munsiyah",
)


class SyntheticScraper:
    source = SOURCE_ID

    def fetch(self, request: ScrapeRequest) -> Iterable[RawRecord]:
        params = dict(request.params or {})
        bbox_csv = params.get("bbox")
        if bbox_csv:
            try:
                south, west, north, east = (float(x) for x in str(bbox_csv).split(","))
            except Exception:
                south, west, north, east = DEFAULT_BBOX
        else:
            south, west, north, east = DEFAULT_BBOX
        count = int(params.get("count", 25))
        seed = params.get("seed")
        rng = random.Random(seed) if seed is not None else random.Random()

        for i in range(count):
            t = rng.choice(TYPES)
            beds = 0 if t in ("office", "land") else rng.randint(1, 6)
            baths = 0 if t == "land" else rng.randint(1, max(1, beds))
            area = (
                rng.randint(400, 1200) if t == "land"
                else rng.randint(60, 600)
            )
            price = int(area * rng.uniform(4500, 22000))
            yield {
                "id": f"syn-{request.started_at.timestamp():.0f}-{i:04d}",
                "title": f"{t.title()} in {rng.choice(DISTRICTS)}",
                "category": t,
                "price": price,
                "currency": "SAR",
                "lat": rng.uniform(south, north),
                "lng": rng.uniform(west, east),
                "rooms": beds,
                "baths": baths,
                "area": area,
                "district": rng.choice(DISTRICTS),
                "city": "Riyadh",
                "country": "SA",
                "image": f"https://picsum.photos/seed/aqarx-syn-{i:04d}/640/420",
            }


class SyntheticNormalizer:
    def normalize(self, raw: RawRecord, source: str) -> NormalizedRecord | None:
        return {
            "source": source,
            "source_id": str(raw.get("id") or ""),
            "source_url": f"https://aqarx.com/synthetic/{raw.get('id', '')}",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "title": str(raw.get("title") or ""),
            "type": str(raw.get("category") or "unknown"),
            "price": float(raw.get("price") or 0),
            "currency": str(raw.get("currency") or "SAR"),
            "lat": float(raw.get("lat") or 0),
            "lng": float(raw.get("lng") or 0),
            "beds": int(raw.get("rooms") or 0),
            "baths": int(raw.get("baths") or 0),
            "area_sqm": float(raw.get("area") or 0),
            "district": str(raw.get("district") or ""),
            "city": str(raw.get("city") or ""),
            "country": str(raw.get("country") or "SA"),
            "photo": str(raw.get("image") or ""),
            "raw": dict(raw),
        }


@register_source(SOURCE_ID)
def _factory() -> tuple[IScraper, INormalizer]:
    return SyntheticScraper(), SyntheticNormalizer()
