#!/usr/bin/env python3
"""
Admin control-plane token authentication middleware for XWApiServer.
"""

from __future__ import annotations

import hmac
from typing import Any, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from exonware.xwapi.errors import AuthenticationError, get_trace_id
from exonware.xwapi.server.http import starlette_json_response_from_xwapi_error


def _extract_admin_token(request: Request) -> str | None:
    """Extract admin token from supported headers."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
        if token:
            return token
    token = request.headers.get("X-Admin-Token", "").strip()
    return token or None


class AdminTokenMiddleware(BaseHTTPMiddleware):
    """Protect mutating admin endpoints with optional shared token."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
        server = getattr(request.app.state, "xwapi_server", None)
        if server is None:
            return await call_next(request)

        configured_token = (getattr(server, "_admin_token", None) or "").strip()
        if not configured_token:
            # Default dev behavior remains unchanged when no token configured.
            return await call_next(request)

        path = request.url.path
        method = request.method.upper()
        prefixes = getattr(server, "_admin_auth_prefixes", {"/server"})
        protect_reads = bool(getattr(server, "_admin_protect_reads", False))

        is_admin_path = any(path == prefix or path.startswith(f"{prefix}/") for prefix in prefixes)
        is_mutation = method in {"POST", "PUT", "PATCH", "DELETE"}
        requires_auth = is_admin_path and (is_mutation or (protect_reads and method == "GET"))
        if not requires_auth:
            return await call_next(request)

        provided_token = _extract_admin_token(request) or ""
        if provided_token and hmac.compare_digest(provided_token, configured_token):
            return await call_next(request)

        trace_id = get_trace_id(request)
        request.state.trace_id = trace_id
        error = AuthenticationError(
            message="Admin authentication required",
            details={"path": path, "method": method},
            hint="Provide Authorization: Bearer <token> or X-Admin-Token header",
        )
        return starlette_json_response_from_xwapi_error(
            error,
            request=request,
            extra_headers={"WWW-Authenticate": "Bearer"},
        )
