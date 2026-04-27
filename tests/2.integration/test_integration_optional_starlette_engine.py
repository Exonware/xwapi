# exonware/xwapi/tests/2.integration/test_integration_optional_starlette_engine.py
"""Integration: Starlette optional engine serves registered action + OpenAPI stub."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from exonware.xwapi.config import XWAPIConfig


@pytest.mark.xwapi_integration
@pytest.mark.xwapi_optional_engine
def test_starlette_register_action_get_roundtrip() -> None:
    pytest.importorskip("starlette")
    from starlette.testclient import TestClient

    from exonware.xwapi.server.engines.optional_http_engines import StarletteServerEngine

    cfg = XWAPIConfig(title="Starlette Int", version="1.0.0", description="integration")
    eng = StarletteServerEngine()
    app = eng.create_app(cfg)
    action = SimpleNamespace(func=lambda: {"echo": 42})
    assert eng.register_action(app, action, {"path": "/demo", "method": "GET"})
    client = TestClient(app)
    r = client.get("/demo")
    assert r.status_code == 200
    assert r.json() == {"echo": 42}


@pytest.mark.xwapi_integration
@pytest.mark.xwapi_optional_engine
def test_starlette_openapi_json_integration() -> None:
    pytest.importorskip("starlette")
    from starlette.testclient import TestClient

    from exonware.xwapi.server.engines.optional_http_engines import StarletteServerEngine

    cfg = XWAPIConfig(title="Starlette Int", version="1.0.0", description="integration")
    app = StarletteServerEngine().create_app(cfg)
    r = TestClient(app).get("/openapi.json")
    assert r.status_code == 200
    assert r.json().get("openapi") == "3.1.0"
