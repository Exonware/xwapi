#!/usr/bin/env python3
"""
Outbox + singleton worker manager used by XWApiServer.
"""

from __future__ import annotations

from datetime import datetime
from threading import RLock
from typing import Any

from collections.abc import Callable

from exonware.xwapi.server.pipeline.outbox import AOutboxStore, InMemoryOutboxStore
from exonware.xwapi.server.pipeline.worker import BackgroundWorker

JobHandler = Callable[[dict[str, Any]], Any]


class ActionPipelineManager:
    """Coordinates durable outbox and singleton background worker."""

    def __init__(self, owner_id: str, *, outbox_store: AOutboxStore | None = None):
        self._owner_id = owner_id
        self._store = outbox_store or InMemoryOutboxStore()
        self._worker = BackgroundWorker(owner_id=owner_id, store=self._store)
        self._lock = RLock()

    def register_handler(self, job_type: str, handler: JobHandler) -> None:
        self._worker.register_handler(job_type, handler)

    def enqueue(
        self,
        job_type: str,
        payload: dict[str, Any],
        *,
        run_after: datetime | None = None,
        max_attempts: int = 5,
    ) -> str:
        return self._store.enqueue(
            job_type=job_type,
            payload=payload,
            run_after=run_after,
            max_attempts=max_attempts,
        )

    def start(self) -> None:
        with self._lock:
            self._worker.start()

    def stop(self) -> None:
        with self._lock:
            self._worker.stop()

    def status(self) -> dict[str, Any]:
        return {
            "worker": self._worker.status(),
            "outbox": self._store.stats(),
        }
