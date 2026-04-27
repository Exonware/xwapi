#exonware/xwapi/src/exonware/xwapi/scrapping/base.py
"""
BaseScraper — orchestrates a single scrape run end-to-end.

Wires together the four protocol roles:
  scraper.fetch(request) → raw records
                         ↓
              normalizer.normalize(raw)
                         ↓
                 persistence.store(record)
                         ↓
              ScrapeStatus aggregated into ScrapeResult

The framework provides this as a convenience; downstream consumers can also
write their own loop if they need custom batching, parallelism, or monitoring.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
"""
from __future__ import annotations
from typing import Iterable

from .contracts import INormalizer, IPersistence, IScraper, ScrapeStatus
from .types import RawRecord, ScrapeRequest, ScrapeResult


class BaseScraper:
    """Run one ScrapeRequest through a scraper / normalizer / persistence trio."""

    def __init__(
        self,
        scraper: IScraper,
        normalizer: INormalizer,
        persistence: IPersistence,
    ):
        self._scraper = scraper
        self._normalizer = normalizer
        self._persistence = persistence

    def run(self, request: ScrapeRequest) -> ScrapeResult:
        result = ScrapeResult(request=request)
        try:
            raw_iter: Iterable[RawRecord] = self._scraper.fetch(request)
            for raw in raw_iter:
                result.raw_count += 1
                if request.max_records is not None and result.raw_count > request.max_records:
                    # Caller asked for an upper bound; stop fetching.
                    break

                try:
                    normalized = self._normalizer.normalize(raw, self._scraper.source)
                except Exception as exc:  # noqa: BLE001 — the normalizer might do anything.
                    result.add_error(f"normalize: {exc}")
                    continue

                if normalized is None:
                    continue
                result.normalized_count += 1

                try:
                    status = self._persistence.store(normalized)
                except Exception as exc:  # noqa: BLE001 — persistence is an external boundary.
                    result.add_error(f"persist: {exc}")
                    continue

                if status is ScrapeStatus.PERSISTED:
                    result.persisted_count += 1
                elif status is ScrapeStatus.DUPLICATE:
                    result.duplicates_skipped += 1
                elif status is ScrapeStatus.ERROR:
                    result.add_error("persistence reported ERROR for one record")

            self._persistence.flush()
        except Exception as exc:  # noqa: BLE001 — top-level safety net.
            result.add_error(f"fatal: {exc}")
        finally:
            result.mark_finished()
        return result
