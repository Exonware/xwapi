# exonware/xwapi/src/exonware/xwapi/server/engines/optional_http_engines.py
"""
Optional HTTP server engines (lazy-imported; install the matching extra / framework).

Each engine exposes the same ``IApiServerEngine`` surface: ``create_app``, ``register_action``,
``generate_schema``, ``start_server``. Action binding uses :mod:`http_action_bridge` unless
xwaction adds a first-class engine for that framework later.
"""

from __future__ import annotations

import sys
from typing import Any

from exonware.xwapi.config import XWAPIConfig
from exonware.xwapi.server.engines.contracts import ProtocolType
from exonware.xwapi.server.engines.http_base import AHttpServerEngineBase
from exonware.xwsystem import get_logger

logger = get_logger(__name__)


def _uvicorn_run(app: Any, host: str, port: int, **kwargs: Any) -> None:
    import uvicorn

    uvicorn_kwargs = {"host": host, "port": port, "log_level": kwargs.pop("log_level", "info")}
    if sys.platform == "win32":
        uvicorn_kwargs["loop"] = "asyncio"
    uvicorn_kwargs.update(kwargs)
    uvicorn.run(app, **uvicorn_kwargs)


class StarletteServerEngine(AHttpServerEngineBase):
    """Pure Starlette ASGI app (no FastAPI). Requires ``starlette``."""

    def __init__(self) -> None:
        super().__init__("starlette")
        self._app: Any = None
        self._config: XWAPIConfig | None = None

    def create_app(self, config: XWAPIConfig) -> Any:
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse
        from starlette.routing import Route

        self._config = config
        engine = self

        async def openapi_json(_request: Any) -> Any:
            spec = engine.generate_openapi(engine._app, [], config)
            return JSONResponse(spec)

        routes = [Route("/openapi.json", openapi_json, methods=["GET"])]
        self._app = Starlette(routes=routes)
        return self._app

    def _register_http_action(self, app: Any, action: Any, path: str, method: str) -> bool:
        from starlette.requests import Request
        from starlette.responses import JSONResponse
        from starlette.routing import Route

        from exonware.xwapi.server.engines.http_action_bridge import (
            ActionExecutionError,
            invoke_action_for_http,
            merge_query_and_json,
        )

        methods = [method.upper()]

        async def endpoint(request: Request) -> Any:
            try:
                qp = dict(request.query_params)
                body: dict[str, Any] = {}
                if request.method in ("POST", "PUT", "PATCH") and "application/json" in (
                    request.headers.get("content-type") or ""
                ):
                    try:
                        raw = await request.json()
                        if isinstance(raw, dict):
                            body = raw
                    except Exception:
                        body = {}
                params = merge_query_and_json(qp, body)
                data = await invoke_action_for_http(
                    action, source_engine=self.name, parameters=params
                )
                return JSONResponse(data if isinstance(data, dict) else {"result": data})
            except ActionExecutionError as exc:
                return JSONResponse({"error": str(exc)}, status_code=400)

        app.router.routes.append(Route(path, endpoint=endpoint, methods=methods))  # type: ignore[attr-defined]
        return True

    def generate_openapi(self, app: Any, actions: list[Any], config: Any) -> dict[str, Any]:
        return super().generate_openapi(app, actions, config)

    def start_server(self, app: Any, host: str = "0.0.0.0", port: int = 8000, **kwargs: Any) -> None:
        _uvicorn_run(app, host, port, **kwargs)


class QuartServerEngine(AHttpServerEngineBase):
    """Quart (async Flask-like ASGI). Requires ``quart``."""

    def __init__(self) -> None:
        super().__init__("quart")
        self._app: Any = None

    def create_app(self, config: XWAPIConfig) -> Any:
        from quart import Quart, jsonify

        app = Quart(__name__)
        engine = self

        @app.route("/openapi.json", methods=["GET"])
        async def openapi_json() -> Any:
            spec = engine.generate_openapi(engine._app, [], config)
            return jsonify(spec)

        self._app = app
        return app

    def _register_http_action(self, app: Any, action: Any, path: str, method: str) -> bool:
        from quart import request

        from exonware.xwapi.server.engines.http_action_bridge import (
            ActionExecutionError,
            invoke_action_for_http,
            merge_query_and_json,
        )

        m = method.upper()

        async def handler() -> Any:
            from quart import jsonify

            try:
                qp = dict(request.args)
                body: dict[str, Any] = {}
                if request.method in ("POST", "PUT", "PATCH") and request.is_json:
                    body = await request.get_json() or {}
                params = merge_query_and_json(qp, body if isinstance(body, dict) else {})
                data = await invoke_action_for_http(
                    action, source_engine=self.name, parameters=params
                )
                return jsonify(data if isinstance(data, dict) else {"result": data})
            except ActionExecutionError as exc:
                resp = await jsonify({"error": str(exc)})
                resp.status_code = 400
                return resp

        app.add_url_rule(path, f"xwapi_{id(handler)}", handler, methods=[m])
        return True

    def start_server(self, app: Any, host: str = "0.0.0.0", port: int = 8000, **kwargs: Any) -> None:
        _uvicorn_run(app, host, port, **kwargs)


class SanicServerEngine(AHttpServerEngineBase):
    """Sanic HTTP server. Requires ``sanic``."""

    def __init__(self) -> None:
        super().__init__("sanic")
        self._app: Any = None

    def create_app(self, config: XWAPIConfig) -> Any:
        from sanic import Sanic, response

        name = (config.title or "xwapi").replace(" ", "_")[:32] or "xwapi"
        app = Sanic(name)
        engine = self

        @app.get("/openapi.json")
        async def openapi_json(_request: Any) -> Any:
            spec = engine.generate_openapi(engine._app, [], config)
            return response.json(spec)

        self._app = app
        return app

    def _register_http_action(self, app: Any, action: Any, path: str, method: str) -> bool:
        from sanic import response

        from exonware.xwapi.server.engines.http_action_bridge import (
            ActionExecutionError,
            invoke_action_for_http,
            merge_query_and_json,
        )

        m = method.upper()

        async def handler(request: Any) -> Any:
            try:
                qp = dict(request.args)
                body: dict[str, Any] = {}
                if request.method in ("POST", "PUT", "PATCH"):
                    try:
                        raw = request.json
                        if isinstance(raw, dict):
                            body = raw
                    except Exception:
                        body = {}
                params = merge_query_and_json(qp, body)
                data = await invoke_action_for_http(
                    action, source_engine=self.name, parameters=params
                )
                return response.json(data if isinstance(data, dict) else {"result": data})
            except ActionExecutionError as exc:
                return response.json({"error": str(exc)}, status=400)

        app.add_route(handler, path, methods=[m], name=f"xwapi_{id(handler)}")
        return True

    def start_server(self, app: Any, host: str = "0.0.0.0", port: int = 8000, **kwargs: Any) -> None:
        app.run(host=host, port=port, **kwargs)


class AiohttpServerEngine(AHttpServerEngineBase):
    """aiohttp web Application. Requires ``aiohttp``."""

    def __init__(self) -> None:
        super().__init__("aiohttp")
        self._app: Any = None

    def create_app(self, config: XWAPIConfig) -> Any:
        from aiohttp import web

        engine = self

        async def openapi_json(_request: Any) -> Any:
            spec = engine.generate_openapi(engine._app, [], config)
            return web.json_response(spec)

        app = web.Application()
        app.router.add_get("/openapi.json", openapi_json)
        self._app = app
        return app

    def _register_http_action(self, app: Any, action: Any, path: str, method: str) -> bool:
        from aiohttp import web

        from exonware.xwapi.server.engines.http_action_bridge import (
            ActionExecutionError,
            invoke_action_for_http,
            merge_query_and_json,
        )

        m = method.upper()

        async def handler(request: Any) -> Any:
            try:
                qp = dict(request.query)
                body: dict[str, Any] = {}
                if request.method in ("POST", "PUT", "PATCH"):
                    try:
                        raw = await request.json()
                        if isinstance(raw, dict):
                            body = raw
                    except Exception:
                        body = {}
                params = merge_query_and_json(qp, body)
                data = await invoke_action_for_http(
                    action, source_engine=self.name, parameters=params
                )
                return web.json_response(data if isinstance(data, dict) else {"result": data})
            except ActionExecutionError as exc:
                return web.json_response({"error": str(exc)}, status=400)

        app.router.add_route(m, path, handler)
        return True

    def start_server(self, app: Any, host: str = "0.0.0.0", port: int = 8000, **kwargs: Any) -> None:
        from aiohttp import web

        web.run_app(app, host=host, port=port, **kwargs)


class BlackSheepServerEngine(AHttpServerEngineBase):
    """BlackSheep ASGI. Requires ``blacksheep``."""

    def __init__(self) -> None:
        super().__init__("blacksheep")
        self._app: Any = None

    def create_app(self, config: XWAPIConfig) -> Any:
        from blacksheep import Application
        from blacksheep.server.responses import json as json_response

        app = Application(show_error_details=True)
        engine = self

        async def openapi_json(_request: Any) -> Any:
            spec = engine.generate_openapi(engine._app, [], config)
            return json_response(spec)

        app.router.add_get("/openapi.json", openapi_json)
        self._app = app
        return app

    def _register_http_action(self, app: Any, action: Any, path: str, method: str) -> bool:
        from blacksheep.server.responses import json as json_response

        from exonware.xwapi.server.engines.http_action_bridge import (
            ActionExecutionError,
            invoke_action_for_http,
            merge_query_and_json,
        )

        m = method.upper()

        async def handler(request: Any) -> Any:
            try:
                qp = {k: request.query.get(k) for k in request.query}
                body: dict[str, Any] = {}
                if request.method in ("POST", "PUT", "PATCH"):
                    try:
                        raw = await request.json()
                        if isinstance(raw, dict):
                            body = raw
                    except Exception:
                        body = {}
                params = merge_query_and_json(qp, body)
                data = await invoke_action_for_http(
                    action, source_engine=self.name, parameters=params
                )
                return json_response(data if isinstance(data, dict) else {"result": data})
            except ActionExecutionError as exc:
                return json_response({"error": str(exc)}, status=400)

        if m == "GET":
            app.router.add_get(path, handler)
        elif m == "POST":
            app.router.add_post(path, handler)
        elif m == "PUT":
            app.router.add_put(path, handler)
        elif m == "PATCH":
            app.router.add_patch(path, handler)
        elif m == "DELETE":
            app.router.add_delete(path, handler)
        else:
            app.router.add_post(path, handler)
        return True

    def start_server(self, app: Any, host: str = "0.0.0.0", port: int = 8000, **kwargs: Any) -> None:
        _uvicorn_run(app, host, port, **kwargs)


class LitestarServerEngine(AHttpServerEngineBase):
    """Litestar ASGI with catch-all dispatch. Requires ``litestar``."""

    def __init__(self) -> None:
        super().__init__("litestar")
        self._app: Any = None
        self._dispatch: dict[tuple[str, str], Any] = {}
        self._litestar_config: XWAPIConfig | None = None

    def create_app(self, config: XWAPIConfig) -> Any:
        from litestar import Litestar, Request, Router, get, route
        from litestar.exceptions import HTTPException

        self._litestar_config = config
        self._dispatch = {}
        engine = self

        @get("/openapi.json")
        async def openapi_json() -> dict[str, Any]:
            return engine.generate_openapi(engine._app, [], config)

        @route(
            http_method=["GET", "POST", "PUT", "PATCH", "DELETE"],
            path="/{rest_path:path}",
        )
        async def catch_all(rest_path: str, request: Request) -> dict[str, Any]:
            from exonware.xwapi.server.engines.http_action_bridge import (
                ActionExecutionError,
                invoke_action_for_http,
                merge_query_and_json,
            )

            path = "/" + rest_path.lstrip("/")
            key = (request.method.upper(), path)
            action = engine._dispatch.get(key)
            if action is None:
                raise HTTPException(status_code=404, detail="not_found")
            try:
                qp = dict(request.query_params)
                body: dict[str, Any] = {}
                if request.method in ("POST", "PUT", "PATCH"):
                    try:
                        raw = await request.json()
                        if isinstance(raw, dict):
                            body = raw
                    except Exception:
                        body = {}
                params = merge_query_and_json(qp, body)
                data = await invoke_action_for_http(
                    action, source_engine=engine.name, parameters=params
                )
                return data if isinstance(data, dict) else {"result": data}
            except ActionExecutionError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

        router = Router(path="/", route_handlers=[openapi_json, catch_all])
        self._app = Litestar(route_handlers=[router], debug=True)
        return self._app

    def _register_http_action(self, app: Any, action: Any, path: str, method: str) -> bool:
        self._dispatch[(method.upper(), path)] = action
        return True

    def start_server(self, app: Any, host: str = "0.0.0.0", port: int = 8000, **kwargs: Any) -> None:
        _uvicorn_run(app, host, port, **kwargs)


class DjangoServerEngine(AHttpServerEngineBase):
    """
    Minimal embedded Django ASGI app with catch-all dispatch.
    Requires ``django`` (and configures settings if not already configured).
    """

    def __init__(self) -> None:
        super().__init__("django")
        self._app: Any = None
        self._dispatch: dict[tuple[str, str], Any] = {}

    def create_app(self, config: XWAPIConfig) -> Any:
        if self._app is not None:
            return self._app
        import django
        from django.conf import settings
        from django.core.asgi import get_asgi_application
        from django.http import JsonResponse
        from django.urls import path
        from django.views import View

        self._dispatch = {}
        engine = self

        class OpenAPIView(View):
            def get(self, _request: Any) -> Any:
                spec = engine.generate_openapi(None, [], config)
                return JsonResponse(spec)

        class CatchAllView(View):
            async def dispatch(self, request: Any, *args: Any, **kwargs: Any) -> Any:
                from django.http import JsonResponse as DJJsonResponse

                from exonware.xwapi.server.engines.http_action_bridge import (
                    ActionExecutionError,
                    invoke_action_for_http,
                    merge_query_and_json,
                )

                path_key = request.path
                key = (request.method.upper(), path_key)
                action = engine._dispatch.get(key)
                if action is None:
                    return DJJsonResponse({"error": "not_found"}, status=404)
                try:
                    qp = dict(request.GET.items())
                    body: dict[str, Any] = {}
                    if request.method in ("POST", "PUT", "PATCH"):
                        import json as _json

                        try:
                            raw = _json.loads(request.body or b"{}")
                            if isinstance(raw, dict):
                                body = raw
                        except Exception:
                            body = {}
                    params = merge_query_and_json(qp, body)
                    data = await invoke_action_for_http(
                        action, source_engine=engine.name, parameters=params
                    )
                    return DJJsonResponse(
                        data if isinstance(data, dict) else {"result": data}, safe=False
                    )
                except ActionExecutionError as exc:
                    return DJJsonResponse({"error": str(exc)}, status=400)

        urlpatterns = [
            path("openapi.json", OpenAPIView.as_view()),
            path("<path:rest_path>", CatchAllView.as_view()),
        ]

        if not settings.configured:
            globals()["urlpatterns"] = urlpatterns
            settings.configure(
                ROOT_URLCONF=__name__,
                SECRET_KEY="xwapi-django-engine-placeholder",
                ALLOWED_HOSTS=["*"],
                DEBUG=True,
            )
            django.setup()
        else:
            # If Django already configured, user must mount routes manually — still return ASGI app
            logger.warning(
                "Django settings already configured; xwapi Django engine urlpatterns may be ignored."
            )

        self._app = get_asgi_application()
        return self._app

    def _register_http_action(self, app: Any, action: Any, path: str, method: str) -> bool:
        self._dispatch[(method.upper(), path)] = action
        return True

    def start_server(self, app: Any, host: str = "0.0.0.0", port: int = 8000, **kwargs: Any) -> None:
        _uvicorn_run(app, host, port, **kwargs)


class MangumServerEngine(AHttpServerEngineBase):
    """
    AWS Lambda ASGI adapter wrapping an inner FastAPI app.
    Requires ``mangum`` and ``fastapi``. ``start_server`` is a no-op (Lambda invokes the handler).
    """

    def __init__(self) -> None:
        super().__init__("mangum")
        self._inner: Any = None
        self._handler: Any = None
        self._fastapi_engine: Any = None

    def create_app(self, config: XWAPIConfig) -> Any:
        from mangum import Mangum

        from exonware.xwapi.server.engines.fastapi import FastAPIServerEngine

        self._fastapi_engine = FastAPIServerEngine()
        self._inner = self._fastapi_engine.create_app(config)
        self._handler = Mangum(self._inner, lifespan="off")
        setattr(self._handler, "_xwapi_inner_app", self._inner)
        return self._handler

    def _register_http_action(self, app: Any, action: Any, path: str, method: str) -> bool:
        inner = getattr(app, "_xwapi_inner_app", None) or self._inner
        if inner is None or self._fastapi_engine is None:
            return False
        return self._fastapi_engine._register_http_action(inner, action, path, method)

    def generate_openapi(self, app: Any, actions: list[Any], config: Any) -> dict[str, Any]:
        inner = getattr(app, "_xwapi_inner_app", None) or self._inner
        if inner is None or self._fastapi_engine is None:
            return super().generate_openapi(app, actions, config)
        return self._fastapi_engine.generate_openapi(inner, actions, config)

    def start_server(self, app: Any, host: str = "0.0.0.0", port: int = 8000, **kwargs: Any) -> None:
        logger.info(
            "Mangum engine: no in-process HTTP server; deploy the returned handler to AWS Lambda."
        )

    @property
    def supports_admin_endpoints(self) -> bool:
        return True


__all__ = [
    "StarletteServerEngine",
    "QuartServerEngine",
    "SanicServerEngine",
    "AiohttpServerEngine",
    "BlackSheepServerEngine",
    "LitestarServerEngine",
    "DjangoServerEngine",
    "MangumServerEngine",
]
