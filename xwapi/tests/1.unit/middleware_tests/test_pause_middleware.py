from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from exonware.xwapi.server.middleware.pause import PauseControlMiddleware


class _PauseServerStub:
    def __init__(self, should_block: bool):
        self._should_block = should_block

    def should_block_request(self, method: str, path: str) -> bool:
        return self._should_block


@pytest.mark.xwapi_unit
def test_pause_middleware_blocks_with_contract_and_retry_header() -> None:
    """Blocked requests should return uniform pause error with trace + retry headers."""
    app = FastAPI()
    app.state.xwapi_server = _PauseServerStub(should_block=True)
    app.add_middleware(PauseControlMiddleware)

    @app.get("/sample")
    def sample() -> dict[str, str]:
        return {"ok": "yes"}

    client = TestClient(app)
    response = client.get("/sample", headers={"X-Trace-Id": "pause-trace-1"})
    body = response.json()

    assert response.status_code == 503
    assert body["code"] == "ServicePaused"
    assert body["trace_id"] == "pause-trace-1"
    assert body["details"]["method"] == "GET"
    assert body["details"]["path"] == "/sample"
    assert response.headers.get("X-Trace-Id") == "pause-trace-1"
    assert response.headers.get("Retry-After") == "1"


@pytest.mark.xwapi_unit
def test_pause_middleware_allows_request_when_not_blocked() -> None:
    """Requests should pass through when policy does not block them."""
    app = FastAPI()
    app.state.xwapi_server = _PauseServerStub(should_block=False)
    app.add_middleware(PauseControlMiddleware)

    @app.get("/sample")
    def sample() -> dict[str, str]:
        return {"ok": "yes"}

    client = TestClient(app)
    response = client.get("/sample")

    assert response.status_code == 200
    assert response.json()["ok"] == "yes"


@pytest.mark.xwapi_unit
def test_pause_middleware_skips_when_server_state_missing() -> None:
    """Middleware should not block when app.state has no xwapi_server."""
    app = FastAPI()
    app.add_middleware(PauseControlMiddleware)

    @app.get("/sample")
    def sample() -> dict[str, str]:
        return {"ok": "yes"}

    client = TestClient(app)
    response = client.get("/sample")

    assert response.status_code == 200
