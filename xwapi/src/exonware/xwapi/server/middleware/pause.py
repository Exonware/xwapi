#!/usr/bin/env python3
"""
Pause/resume request admission middleware for XWApiServer.
"""

from __future__ import annotations

from typing import Any, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from exonware.xwapi.errors import ServicePausedError, get_trace_id
from exonware.xwapi.server.http import starlette_json_response_from_xwapi_error
from exonware.xwsystem import get_logger

logger = get_logger(__name__)


class PauseControlMiddleware(BaseHTTPMiddleware):
    """Blocks paused routes with 503 while allowing admin/status paths."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
        server = getattr(request.app.state, "xwapi_server", None)
        if server is not None and server.should_block_request(request.method, request.url.path):
            trace_id = get_trace_id(request)
            request.state.trace_id = trace_id
            error = ServicePausedError(
                message="Endpoint is currently paused",
                code="ServicePaused",
                details={"method": request.method.upper(), "path": request.url.path},
                hint="Resume the endpoint or disable global pause from admin endpoints",
            )
            logger.warning(
                "Blocked paused request",
                extra={
                    "trace_id": trace_id,
                    "path": request.url.path,
                    "method": request.method.upper(),
                },
            )
            return starlette_json_response_from_xwapi_error(
                error,
                request=request,
                extra_headers={"Retry-After": "1"},
            )
        return await call_next(request)
