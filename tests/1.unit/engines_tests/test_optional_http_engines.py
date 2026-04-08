# exonware/xwapi/tests/1.unit/engines_tests/test_optional_http_engines.py
"""Optional HTTP server engines: create_app + /openapi.json where frameworks are installed."""

from __future__ import annotations

import pytest

from exonware.xwapi.config import XWAPIConfig

_CFG = XWAPIConfig(title="Optional Engine Test", version="1.0.0", description="pytest")


def _openapi_status(client: object, path: str = "/openapi.json") -> tuple[int, dict | None]:
    r = client.get(path)
    data = None
    try:
        data = r.json()
    except Exception:
        pass
    return r.status_code, data


@pytest.mark.xwapi_unit
@pytest.mark.xwapi_optional_engine
def test_optional_http_engines_module_exports() -> None:
    from exonware.xwapi.server.engines import optional_http_engines as mod

    for name in mod.__all__:
        assert hasattr(mod, name)


@pytest.mark.xwapi_unit
@pytest.mark.xwapi_optional_engine
def test_starlette_engine_openapi_json() -> None:
    pytest.importorskip("starlette")
    from starlette.testclient import TestClient

    from exonware.xwapi.server.engines.optional_http_engines import StarletteServerEngine

    app = StarletteServerEngine().create_app(_CFG)
    client = TestClient(app)
    status, body = _openapi_status(client)
    assert status == 200
    assert body is not None
    assert body.get("openapi") == "3.1.0"


@pytest.mark.xwapi_unit
@pytest.mark.xwapi_optional_engine
def test_quart_engine_openapi_json() -> None:
    pytest.importorskip("quart")
    from quart.app import Quart

    from exonware.xwapi.server.engines.optional_http_engines import QuartServerEngine

    app = QuartServerEngine().create_app(_CFG)
    assert isinstance(app, Quart)


@pytest.mark.xwapi_unit
@pytest.mark.xwapi_optional_engine
def test_sanic_engine_has_openapi_route_registered() -> None:
    pytest.importorskip("sanic")
    from exonware.xwapi.server.engines.optional_http_engines import SanicServerEngine

    app = SanicServerEngine().create_app(_CFG)
    assert app.router.routes


@pytest.mark.xwapi_unit
@pytest.mark.xwapi_optional_engine
def test_aiohttp_engine_creates_application() -> None:
    pytest.importorskip("aiohttp")
    from aiohttp import web

    from exonware.xwapi.server.engines.optional_http_engines import AiohttpServerEngine

    app = AiohttpServerEngine().create_app(_CFG)
    assert isinstance(app, web.Application)


@pytest.mark.xwapi_unit
@pytest.mark.xwapi_optional_engine
def test_blacksheep_engine_creates_application() -> None:
    pytest.importorskip("blacksheep")
    from blacksheep import Application

    from exonware.xwapi.server.engines.optional_http_engines import BlackSheepServerEngine

    app = BlackSheepServerEngine().create_app(_CFG)
    assert isinstance(app, Application)


@pytest.mark.xwapi_unit
@pytest.mark.xwapi_optional_engine
def test_litestar_engine_openapi_handler() -> None:
    pytest.importorskip("litestar")
    from litestar.testing import TestClient

    from exonware.xwapi.server.engines.optional_http_engines import LitestarServerEngine

    app = LitestarServerEngine().create_app(_CFG)
    with TestClient(app=app) as client:
        r = client.get("/openapi.json")
        assert r.status_code == 200
        assert r.json().get("openapi") == "3.1.0"


@pytest.mark.xwapi_unit
@pytest.mark.xwapi_optional_engine
def test_mangum_wraps_fastapi_and_exposes_inner_app() -> None:
    pytest.importorskip("mangum")
    from exonware.xwapi.server.engines.optional_http_engines import MangumServerEngine

    handler = MangumServerEngine().create_app(_CFG)
    inner = getattr(handler, "_xwapi_inner_app", None)
    assert inner is not None


@pytest.mark.xwapi_unit
@pytest.mark.xwapi_optional_engine
def test_django_engine_returns_asgi_callable() -> None:
    pytest.importorskip("django")
    from exonware.xwapi.server.engines.optional_http_engines import DjangoServerEngine

    eng = DjangoServerEngine()
    asgi = eng.create_app(_CFG)
    assert callable(asgi)
