#!/usr/bin/env python3
"""
Outbox storage abstractions for server-side job scheduling.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class OutboxJob:
    """Canonical outbox record used by background workers."""

    job_id: str
    job_type: str
    payload: dict[str, Any]
    status: str = "queued"
    attempts: int = 0
    max_attempts: int = 5
    created_at: datetime = field(default_factory=_utc_now)
    run_after: datetime = field(default_factory=_utc_now)
    lease_expires_at: datetime | None = None
    last_error: str | None = None
    result: Any | None = None


class AOutboxStore(ABC):
    """Abstract durable outbox API."""

    @abstractmethod
    def enqueue(
        self,
        job_type: str,
        payload: dict[str, Any],
        *,
        run_after: datetime | None = None,
        max_attempts: int = 5,
    ) -> str:
        pass

    @abstractmethod
    def claim_due(self, *, limit: int, lease_seconds: int, worker_id: str) -> list[OutboxJob]:
        pass

    @abstractmethod
    def mark_done(self, job_id: str, result: Any | None = None) -> None:
        pass

    @abstractmethod
    def mark_failed(self, job_id: str, error: str, *, retry_delay_seconds: int) -> None:
        pass

    @abstractmethod
    def stats(self) -> dict[str, int]:
        pass


class InMemoryOutboxStore(AOutboxStore):
    """In-memory outbox implementation for local/runtime usage."""

    def __init__(self):
        self._jobs: dict[str, OutboxJob] = {}
        self._lock = RLock()

    def enqueue(
        self,
        job_type: str,
        payload: dict[str, Any],
        *,
        run_after: datetime | None = None,
        max_attempts: int = 5,
    ) -> str:
        with self._lock:
            job_id = str(uuid4())
            self._jobs[job_id] = OutboxJob(
                job_id=job_id,
                job_type=job_type,
                payload=dict(payload or {}),
                max_attempts=max(1, int(max_attempts)),
                run_after=run_after or _utc_now(),
            )
            return job_id

    def claim_due(self, *, limit: int, lease_seconds: int, worker_id: str) -> list[OutboxJob]:
        now = _utc_now()
        claimed: list[OutboxJob] = []
        lease_deadline = now + timedelta(seconds=max(1, lease_seconds))
        with self._lock:
            for job in self._jobs.values():
                if len(claimed) >= limit:
                    break
                if job.status == "done" or job.status == "dead":
                    continue
                if job.status == "in_progress" and job.lease_expires_at and job.lease_expires_at > now:
                    continue
                if job.run_after > now:
                    continue
                job.status = "in_progress"
                job.lease_expires_at = lease_deadline
                claimed.append(job)
        return claimed

    def mark_done(self, job_id: str, result: Any | None = None) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.status = "done"
            job.result = result
            job.lease_expires_at = None

    def mark_failed(self, job_id: str, error: str, *, retry_delay_seconds: int) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.attempts += 1
            job.last_error = error
            job.lease_expires_at = None
            if job.attempts >= job.max_attempts:
                job.status = "dead"
                return
            job.status = "queued"
            job.run_after = _utc_now() + timedelta(seconds=max(0, retry_delay_seconds))

    def stats(self) -> dict[str, int]:
        with self._lock:
            queued = sum(1 for job in self._jobs.values() if job.status == "queued")
            in_progress = sum(1 for job in self._jobs.values() if job.status == "in_progress")
            done = sum(1 for job in self._jobs.values() if job.status == "done")
            dead = sum(1 for job in self._jobs.values() if job.status == "dead")
        return {
            "queued": queued,
            "in_progress": in_progress,
            "done": done,
            "dead": dead,
            "total": queued + in_progress + done + dead,
        }


class OracleAQOutboxStore(AOutboxStore):
    """
    Oracle AQ-backed outbox adapter.
    Implement this by binding queue operations to Oracle AQ in production.
    """

    def __init__(self, backend: AOutboxStore):
        self._backend = backend

    def enqueue(
        self,
        job_type: str,
        payload: dict[str, Any],
        *,
        run_after: datetime | None = None,
        max_attempts: int = 5,
    ) -> str:
        return self._backend.enqueue(job_type, payload, run_after=run_after, max_attempts=max_attempts)

    def claim_due(self, *, limit: int, lease_seconds: int, worker_id: str) -> list[OutboxJob]:
        return self._backend.claim_due(limit=limit, lease_seconds=lease_seconds, worker_id=worker_id)

    def mark_done(self, job_id: str, result: Any | None = None) -> None:
        self._backend.mark_done(job_id, result=result)

    def mark_failed(self, job_id: str, error: str, *, retry_delay_seconds: int) -> None:
        self._backend.mark_failed(job_id, error=error, retry_delay_seconds=retry_delay_seconds)

    def stats(self) -> dict[str, int]:
        return self._backend.stats()


class OracleSchedulerOutboxStore(AOutboxStore):
    """
    DBMS_SCHEDULER-backed outbox adapter.
    This wrapper keeps the same outbox contract so worker logic is unchanged.
    """

    def __init__(self, backend: AOutboxStore):
        self._backend = backend

    def enqueue(
        self,
        job_type: str,
        payload: dict[str, Any],
        *,
        run_after: datetime | None = None,
        max_attempts: int = 5,
    ) -> str:
        return self._backend.enqueue(job_type, payload, run_after=run_after, max_attempts=max_attempts)

    def claim_due(self, *, limit: int, lease_seconds: int, worker_id: str) -> list[OutboxJob]:
        return self._backend.claim_due(limit=limit, lease_seconds=lease_seconds, worker_id=worker_id)

    def mark_done(self, job_id: str, result: Any | None = None) -> None:
        self._backend.mark_done(job_id, result=result)

    def mark_failed(self, job_id: str, error: str, *, retry_delay_seconds: int) -> None:
        self._backend.mark_failed(job_id, error=error, retry_delay_seconds=retry_delay_seconds)

    def stats(self) -> dict[str, int]:
        return self._backend.stats()
