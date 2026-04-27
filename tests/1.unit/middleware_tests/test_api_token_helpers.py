from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from exonware.xwapi.server.middleware.api_token import (
    APITokenMiddleware,
    _extract_bearer_token,
    _segments,
    _template_matches,
)


@pytest.mark.xwapi_unit
def test_api_token_helper_segments_and_template_matching() -> None:
    assert _segments("/") == []
    assert _segments("/a/b/") == ["a", "b"]
    assert _template_matches("/users/{id}", "/users/123") is True
    assert _template_matches("/users/{id}", "/users/123/posts") is False
    assert _template_matches("/users/static", "/users/other") is False


@pytest.mark.xwapi_unit
def test_api_token_extract_bearer_token_from_header() -> None:
    app = FastAPI()

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(app)
    request = client.build_request("GET", "/ping", headers={"Authorization": "Bearer test-token"})
    from starlette.requests import Request

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/ping",
        "headers": [(b"authorization", b"Bearer test-token")],
        "query_string": b"",
        "scheme": "http",
        "server": ("testserver", 80),
        "client": ("testclient", 50000),
    }
    starlette_request = Request(scope)
    assert _extract_bearer_token(starlette_request) == "test-token"
    _ = request


@pytest.mark.xwapi_unit
def test_api_token_middleware_passes_without_server_state() -> None:
    app = FastAPI()
    app.add_middleware(APITokenMiddleware)

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(app)
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
