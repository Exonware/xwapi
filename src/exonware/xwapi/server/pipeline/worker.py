#!/usr/bin/env python3
"""
Singleton background worker for outbox job execution.
"""

from __future__ import annotations

import asyncio
import inspect
import threading
import time
from threading import Event, RLock, Thread
from typing import Any

from collections.abc import Callable

from exonware.xwapi.server.pipeline.outbox import AOutboxStore, OutboxJob
from exonware.xwsystem import get_logger

logger = get_logger(__name__)

JobHandler = Callable[[dict[str, Any]], Any]


class BackgroundWorker:
    """Single active worker process-wide for safe serialized execution."""

    _singleton_lock = RLock()
    _active_owner: str | None = None

    def __init__(
        self,
        owner_id: str,
        store: AOutboxStore,
        *,
        poll_interval_seconds: float = 0.25,
        lease_seconds: int = 30,
        batch_size: int = 16,
    ):
        self._owner_id = owner_id
        self._store = store
        self._poll_interval_seconds = max(0.05, float(poll_interval_seconds))
        self._lease_seconds = max(1, int(lease_seconds))
        self._batch_size = max(1, int(batch_size))
        self._handlers: dict[str, JobHandler] = {}
        self._thread: Thread | None = None
        self._stop_event = Event()
        self._local_lock = RLock()

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def register_handler(self, job_type: str, handler: JobHandler) -> None:
        if not job_type:
            raise ValueError("job_type is required")
        if not callable(handler):
            raise TypeError("handler must be callable")
        self._handlers[job_type] = handler

    def start(self) -> None:
        with self._local_lock:
            if self.is_running:
                return
            with BackgroundWorker._singleton_lock:
                if BackgroundWorker._active_owner and BackgroundWorker._active_owner != self._owner_id:
                    raise RuntimeError(
                        f"Background worker singleton already owned by '{BackgroundWorker._active_owner}'"
                    )
                BackgroundWorker._active_owner = self._owner_id
            self._stop_event.clear()
            self._thread = Thread(target=self._run_loop, name=f"xwapi-worker-{self._owner_id}", daemon=True)
            self._thread.start()

    def stop(self, timeout_seconds: float = 3.0) -> None:
        with self._local_lock:
            self._stop_event.set()
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=max(0.1, timeout_seconds))
            if self._thread and self._thread.is_alive():
                logger.error(
                    "Background worker did not stop before timeout; singleton ownership retained",
                    extra={"owner_id": self._owner_id},
                )
                return
            self._thread = None
            with BackgroundWorker._singleton_lock:
                if BackgroundWorker._active_owner == self._owner_id:
                    BackgroundWorker._active_owner = None

    def status(self) -> dict[str, Any]:
        return {
            "running": self.is_running,
            "owner_id": self._owner_id,
            "handlers_count": len(self._handlers),
            "singleton_owner": BackgroundWorker._active_owner,
        }

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                jobs = self._store.claim_due(
                    limit=self._batch_size,
                    lease_seconds=self._lease_seconds,
                    worker_id=self._owner_id,
                )
                if not jobs:
                    time.sleep(self._poll_interval_seconds)
                    continue
                for job in jobs:
                    self._execute_job(job)
            except Exception as exc:
                logger.exception("Background worker loop failure", extra={"owner_id": self._owner_id, "error": str(exc)})
                time.sleep(self._poll_interval_seconds)

    def _execute_job(self, job: OutboxJob) -> None:
        handler = self._handlers.get(job.job_type)
        if handler is None:
            self._store.mark_failed(job.job_id, f"No handler for job_type={job.job_type}", retry_delay_seconds=0)
            return
        try:
            result = handler(job.payload)
            if inspect.isawaitable(result):
                result = asyncio.run(result)
            self._store.mark_done(job.job_id, result=result)
        except Exception as exc:
            retry_delay = min(60, max(1, 2 ** min(job.attempts, 6)))
            self._store.mark_failed(job.job_id, str(exc), retry_delay_seconds=retry_delay)
