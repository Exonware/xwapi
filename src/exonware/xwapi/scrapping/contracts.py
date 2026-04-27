#exonware/xwapi/src/exonware/xwapi/scrapping/contracts.py
"""
Protocol contracts for the scrapping framework.

The framework uses runtime-checkable Protocols (duck typing) so consumers can
plug in their own implementations without inheriting from a base class. The
four roles:

  - IScraper       — fetches raw records from one site / data source.
  - INormalizer    — converts a raw record into a normalized dict (or None to drop).
  - IPersistence   — stores normalized records (impl decides dedup, batching).
  - IRateLimiter   — gates outbound requests so we behave on the source.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
"""
from __future__ import annotations
from enum import Enum
from typing import Iterable, Protocol, runtime_checkable

from .types import NormalizedRecord, RawRecord, ScrapeRequest


class ScrapeStatus(str, Enum):
    """Outcome status for a single record's persistence attempt."""
    PERSISTED = "persisted"
    DUPLICATE = "duplicate"
    DROPPED = "dropped"
    ERROR = "error"


@runtime_checkable
class IScraper(Protocol):
    """A site-specific scraper. Yields raw records lazily so callers can stop early."""

    source: str
    """Stable identifier for this source (e.g. 'aqar.sa'). Echoed onto every record."""

    def fetch(self, request: ScrapeRequest) -> Iterable[RawRecord]:
        """Yield raw records matching the request. Caller is responsible for limits."""
        ...


@runtime_checkable
class INormalizer(Protocol):
    """Converts a source's raw record into a flat normalized dict."""

    def normalize(self, raw: RawRecord, source: str) -> NormalizedRecord | None:
        """
        Return a normalized record, or None to drop (malformed / not interesting).

        Implementations should always set:
          - record['source']      — echo of the source id
          - record['source_url']  — original URL where this listing lives
          - record['fetched_at']  — ISO 8601 timestamp the record was fetched
        Plus whatever domain-specific fields the consumer's storage agrees on.
        """
        ...


@runtime_checkable
class IPersistence(Protocol):
    """Storage sink for normalized records. Implementation owns dedup + batching."""

    def store(self, record: NormalizedRecord) -> ScrapeStatus:
        """Store one record; return the resulting status."""
        ...

    def flush(self) -> None:
        """Commit any buffered records (no-op for write-through impls)."""
        ...


@runtime_checkable
class IRateLimiter(Protocol):
    """Gate outbound requests to respect the source's tolerance."""

    def acquire(self) -> None:
        """Block (or sleep) until one more request is allowed."""
        ...
