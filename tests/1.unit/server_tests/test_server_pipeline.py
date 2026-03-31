from __future__ import annotations

import time

import pytest

from exonware.xwaction import XWAction
from exonware.xwapi.errors import ServerLifecycleError
from exonware.xwapi.server import XWApiServer


def _wait_until(predicate, timeout: float = 2.0, interval: float = 0.05) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False


@pytest.mark.xwapi_unit
def test_pipeline_executes_outbox_job() -> None:
    server = XWApiServer(engine="fastapi")
    observed: list[int] = []

    def handler(payload: dict[str, int]) -> dict[str, bool]:
        observed.append(payload["value"])
        return {"ok": True}

    server.register_pipeline_handler("demo.job", handler)
    server.enqueue_pipeline_job("demo.job", {"value": 7})

    try:
        server.start_pipeline_worker()
        assert _wait_until(lambda: observed == [7])
        snapshot = server.status()
        assert "pipeline" in snapshot
        assert snapshot["pipeline"]["worker"]["running"] is True
    finally:
        server.stop_pipeline_worker()


@pytest.mark.xwapi_unit
def test_pipeline_worker_is_singleton_per_process() -> None:
    server_a = XWApiServer(engine="fastapi")
    server_b = XWApiServer(engine="fastapi")

    try:
        server_a.start_pipeline_worker()
        with pytest.raises(ServerLifecycleError):
            server_b.start_pipeline_worker()
    finally:
        server_a.stop_pipeline_worker()
        server_b.stop_pipeline_worker()


@pytest.mark.xwapi_unit
def test_enqueue_action_job_executes_registered_action() -> None:
    server = XWApiServer(engine="fastapi")
    tracker: list[str] = []

    @XWAction(operationId="pipeline_action_test", profile="endpoint")
    def action_job() -> dict[str, str]:
        tracker.append("executed")
        return {"status": "done"}

    assert server.register_action(action_job, path="/pipeline-action", method="GET") is True
    action_name = getattr(action_job.xwaction, "api_name", None) or "pipeline_action_test"

    try:
        server.start_pipeline_worker()
        server.enqueue_action_job(action_name)
        assert _wait_until(lambda: tracker == ["executed"])
    finally:
        server.stop_pipeline_worker()


@pytest.mark.xwapi_unit
def test_pipeline_worker_stop_then_restart_processes_new_jobs() -> None:
    server = XWApiServer(engine="fastapi")
    observed: list[int] = []

    def handler(payload: dict[str, int]) -> dict[str, bool]:
        observed.append(payload["value"])
        return {"ok": True}

    server.register_pipeline_handler("demo.restart", handler)
    try:
        server.start_pipeline_worker()
        server.enqueue_pipeline_job("demo.restart", {"value": 1})
        assert _wait_until(lambda: observed == [1])
        server.stop_pipeline_worker()
        server.enqueue_pipeline_job("demo.restart", {"value": 2})
        server.start_pipeline_worker()
        assert _wait_until(lambda: observed == [1, 2])
    finally:
        server.stop_pipeline_worker()


@pytest.mark.xwapi_unit
def test_pipeline_worker_double_start_is_idempotent() -> None:
    server = XWApiServer(engine="fastapi")
    try:
        server.start_pipeline_worker()
        server.start_pipeline_worker()
        status = server.status()
        assert status["pipeline"]["worker"]["running"] is True
    finally:
        server.stop_pipeline_worker()
