from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from exonware.xwapi.server.pipeline.outbox import InMemoryOutboxStore


@pytest.mark.xwapi_unit
def test_outbox_claim_respects_run_after_and_retry_state() -> None:
    store = InMemoryOutboxStore()
    future = datetime.now(timezone.utc) + timedelta(seconds=60)
    job_future = store.enqueue("job.future", {"a": 1}, run_after=future)
    job_now = store.enqueue("job.now", {"a": 2})

    claimed = store.claim_due(limit=10, lease_seconds=30, worker_id="w1")
    ids = [job.job_id for job in claimed]
    assert job_now in ids
    assert job_future not in ids

    store.mark_failed(job_now, "boom", retry_delay_seconds=0)
    reclaimed = store.claim_due(limit=10, lease_seconds=30, worker_id="w1")
    assert any(job.job_id == job_now for job in reclaimed)


@pytest.mark.xwapi_unit
def test_outbox_moves_to_dead_after_max_attempts() -> None:
    store = InMemoryOutboxStore()
    job = store.enqueue("job.fail", {"x": 1}, max_attempts=2)
    claimed = store.claim_due(limit=1, lease_seconds=1, worker_id="w1")
    assert claimed and claimed[0].job_id == job
    store.mark_failed(job, "f1", retry_delay_seconds=0)
    claimed2 = store.claim_due(limit=1, lease_seconds=1, worker_id="w1")
    assert claimed2 and claimed2[0].job_id == job
    store.mark_failed(job, "f2", retry_delay_seconds=0)
    stats = store.stats()
    assert stats["dead"] == 1


@pytest.mark.xwapi_unit
def test_outbox_reclaims_in_progress_after_lease_expiry() -> None:
    store = InMemoryOutboxStore()
    job_id = store.enqueue("job.reclaim", {"x": 1})
    claimed = store.claim_due(limit=1, lease_seconds=30, worker_id="w1")
    assert claimed and claimed[0].job_id == job_id
    # Simulate worker crash / stale lease by expiring the lease timestamp.
    store._jobs[job_id].lease_expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    reclaimed = store.claim_due(limit=1, lease_seconds=30, worker_id="w2")
    assert reclaimed and reclaimed[0].job_id == job_id
