# exonware/xwapi/src/exonware/xwapi/http.py
"""
HTTP surface for *exposable actions*: FastAPI types and small app hooks.

Sibling Exonware API packages should import ``Request``, response classes, and helpers
from here instead of from ``fastapi`` directly so the ASGI stack and versioning stay
owned by ``exonware.xwapi``. FastAPI remains the default HTTP engine; use the server
``engine=`` parameter when constructing apps if you need Flask or another registered engine.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from fastapi import Depends, Form, Header, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response


def register_startup_handler(
    app: Any,
    handler: Callable[..., Awaitable[None]],
) -> None:
    """Register an async startup handler on a FastAPI-compatible ASGI app."""
    app.on_event("startup")(handler)


def add_http_middleware(app: Any, middleware_callable: Callable[..., Any]) -> None:
    """Register HTTP middleware (delegates to FastAPI/Starlette ``app.middleware``)."""
    app.middleware("http")(middleware_callable)
