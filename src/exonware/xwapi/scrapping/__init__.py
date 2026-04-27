#exonware/xwapi/src/exonware/xwapi/scrapping/__init__.py
"""
xwapi.scrapping — generic, source-agnostic web scraping framework.

This module is **domain-neutral**. It defines:
  - Contracts (Protocols) for scrapers, normalizers, rate limiters, and persistence.
  - Reusable building blocks (HTTP session, token-bucket rate limit, dedup hashing).
  - A `BaseScraper` orchestrator that wires the pieces together.
  - A `sources/` package where concrete site adapters live.

It does **not** know about real estate, products, or any specific schema; downstream
packages (e.g. aqarx) supply their own normalizers and persistence callbacks. This is
deliberately framework-not-product so the same machinery can scrape anything.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
"""

from .contracts import (
    IScraper,
    INormalizer,
    IPersistence,
    IRateLimiter,
    ScrapeStatus,
)
from .types import RawRecord, NormalizedRecord, ScrapeResult, ScrapeRequest
from .rate_limit import TokenBucketRateLimiter
from .dedup import compute_dedup_key
from .http import HttpFetcher
from .base import BaseScraper

__all__ = [
    "IScraper",
    "INormalizer",
    "IPersistence",
    "IRateLimiter",
    "ScrapeStatus",
    "RawRecord",
    "NormalizedRecord",
    "ScrapeResult",
    "ScrapeRequest",
    "TokenBucketRateLimiter",
    "compute_dedup_key",
    "HttpFetcher",
    "BaseScraper",
]
