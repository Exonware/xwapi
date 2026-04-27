#exonware/xwapi/src/exonware/xwapi/scrapping/types.py
"""
Domain-neutral scrapping data types.

`RawRecord` is whatever the source emits (JSON-shaped). `NormalizedRecord` is a
flat dict that downstream consumers agree on by convention; the framework does
not enforce a schema — that's the consumer's job (e.g. aqarx defines its own
`Listing` shape and supplies a normalizer that maps RawRecord → that shape).

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


# A raw record is whatever the source decoded into — JSON dict, parsed HTML node, etc.
# Kept opaque on purpose: only the source-specific normalizer reads it.
RawRecord = Mapping[str, Any]

# A normalized record is a flat JSON-friendly dict. Schema is a contract between
# the source's normalizer and the consumer's persistence — not the framework.
NormalizedRecord = dict[str, Any]


@dataclass(frozen=True)
class ScrapeRequest:
    """A single scrape job: which source, what filters, when to stop."""
    source: str
    """Source identifier (e.g. 'aqar.sa', 'bayut'). Echoed back on every record."""
    params: Mapping[str, Any] = field(default_factory=dict)
    """Source-specific filter params (city, type, page range, …)."""
    max_records: int | None = None
    """Optional cap on how many records to ingest. None = run until exhausted."""
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ScrapeResult:
    """Outcome of one ScrapeRequest run."""
    request: ScrapeRequest
    raw_count: int = 0
    """How many raw records were fetched from the source."""
    normalized_count: int = 0
    """How many survived normalization (dropped if normalizer returns None)."""
    persisted_count: int = 0
    """How many were committed by the persistence layer (after dedup)."""
    duplicates_skipped: int = 0
    errors: list[str] = field(default_factory=list)
    finished_at: datetime | None = None

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)

    def mark_finished(self) -> None:
        self.finished_at = datetime.now(timezone.utc)
