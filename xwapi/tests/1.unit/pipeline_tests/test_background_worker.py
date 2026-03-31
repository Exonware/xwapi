from __future__ import annotations

import time

import pytest

from exonware.xwapi.server.pipeline.outbox import InMemoryOutboxStore
from exonware.xwapi.server.pipeline.worker import BackgroundWorker


def _wait_until(predicate, timeout: float = 2.0, interval: float = 0.05) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False


@pytest.mark.xwapi_unit
def test_background_worker_async_handler_supported() -> None:
    store = InMemoryOutboxStore()
    worker = BackgroundWorker(owner_id="worker-test-async", store=store, poll_interval_seconds=0.05)
    observed: list[int] = []

    async def handler(payload: dict[str, int]) -> dict[str, bool]:
        observed.append(payload["value"])
        return {"ok": True}

    worker.register_handler("job.async", handler)
    store.enqueue("job.async", {"value": 42})
    try:
        worker.start()
        assert _wait_until(lambda: observed == [42])
    finally:
        worker.stop()


@pytest.mark.xwapi_unit
def test_background_worker_unknown_handler_marks_failed() -> None:
    store = InMemoryOutboxStore()
    worker = BackgroundWorker(owner_id="worker-test-fail", store=store, poll_interval_seconds=0.05)
    store.enqueue("job.unknown", {"value": 1}, max_attempts=1)

    try:
        worker.start()
        assert _wait_until(lambda: store.stats()["dead"] == 1)
    finally:
        worker.stop()
