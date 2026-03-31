#!/usr/bin/env python3
"""
API token bearer authentication + optional usage metering middleware.
"""

from __future__ import annotations

import hmac
from typing import Any, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from exonware.xwapi.errors import AuthenticationError, AuthorizationError, get_trace_id
from exonware.xwapi.server.http import starlette_json_response_from_xwapi_error
from exonware.xwsystem import get_logger

logger = get_logger(__name__)


def _extract_bearer_token(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
        if token:
            return token
    return None


def _segments(path: str) -> list[str]:
    normalized = path.strip().strip("/")
    if not normalized:
        return []
    return [segment for segment in normalized.split("/") if segment]


def _template_matches(template: str, path: str) -> bool:
    template_segments = _segments(template)
    path_segments = _segments(path)
    if len(template_segments) != len(path_segments):
        return False
    for t_segment, p_segment in zip(template_segments, path_segments):
        if t_segment.startswith("{") and t_segment.endswith("}"):
            continue
        if t_segment != p_segment:
            return False
    return True


def _literal_specificity(template: str) -> tuple[int, int]:
    segs = _segments(template)
    literal_count = sum(1 for s in segs if not (s.startswith("{") and s.endswith("}")))
    return literal_count, len(segs)


def _resolve_required_scopes(server: Any, *, method: str, path: str) -> set[str] | None:
    rules = list(getattr(server, "_api_token_scope_rules", []) or [])
    candidates: list[dict[str, Any]] = []
    for rule in rules:
        if str(rule.get("method") or "").upper() != method.upper():
            continue
        template = str(rule.get("path") or "/")
        if _template_matches(template, path):
            candidates.append(rule)
    if not candidates:
        return None
    candidates.sort(key=lambda r: _literal_specificity(str(r.get("path") or "/")), reverse=True)
    top = candidates[0]
    return set(top.get("scopes") or set())


class APITokenMiddleware(BaseHTTPMiddleware):
    """
    Validate API bearer token and optionally meter usage through APITokenManager.

    Behavior is controlled by XWApiServer runtime flags:
    - _api_token_middleware_enabled
    - _api_token_require_bearer
    - _api_token_usage_amount
    - _api_token_exempt_paths
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
        server = getattr(request.app.state, "xwapi_server", None)
        if server is None or not bool(getattr(server, "_api_token_middleware_enabled", False)):
            return await call_next(request)

        path = request.url.path
        method = request.method.upper()
        normalized = path.rstrip("/") or "/"
        exempt_paths = set(getattr(server, "_api_token_exempt_paths", set()) or set())
        admin_prefixes = set(getattr(server, "_admin_auth_prefixes", set()) or set())
        if (
            method == "OPTIONS"
            or normalized in exempt_paths
            or any(normalized == p or normalized.startswith(f"{p}/") for p in exempt_paths)
            or any(normalized == p or normalized.startswith(f"{p}/") for p in admin_prefixes)
        ):
            return await call_next(request)

        bearer = _extract_bearer_token(request)
        require_bearer = bool(getattr(server, "_api_token_require_bearer", False))
        if not bearer:
            if not require_bearer:
                return await call_next(request)
            trace_id = get_trace_id(request)
            request.state.trace_id = trace_id
            error = AuthenticationError(
                message="API bearer token required",
                details={"path": path, "method": method},
                hint="Provide Authorization: Bearer <api_token>",
            )
            return starlette_json_response_from_xwapi_error(
                error,
                request=request,
                extra_headers={"WWW-Authenticate": "Bearer"},
            )

        configured_admin_token = (getattr(server, "_admin_token", None) or "").strip()
        if configured_admin_token and hmac.compare_digest(bearer, configured_admin_token):
            # Let admin middleware own admin-token semantics.
            return await call_next(request)

        claims = await server._token_manager.verify_token(bearer)
        if not isinstance(claims, dict):
            trace_id = get_trace_id(request)
            request.state.trace_id = trace_id
            error = AuthenticationError(
                message="Invalid API token",
                details={"path": path, "method": method},
                hint="Use a valid issued API token",
            )
            return starlette_json_response_from_xwapi_error(
                error,
                request=request,
                extra_headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.api_token_claims = claims
        request.state.api_token_id = str(claims.get("token_id") or "")
        request.state.api_subject_id = str(claims.get("subject_id") or "")
        token_scopes = {
            str(scope).strip()
            for scope in (claims.get("scopes") if isinstance(claims.get("scopes"), list) else [])
            if str(scope).strip()
        }

        if bool(getattr(server, "_api_token_enforce_scopes", False)):
            required_scopes = _resolve_required_scopes(server, method=method, path=normalized)
            if required_scopes is None:
                if bool(getattr(server, "_api_token_scope_deny_unmapped", False)):
                    trace_id = get_trace_id(request)
                    request.state.trace_id = trace_id
                    error = AuthorizationError(
                        message="No scope policy mapped for route",
                        details={"path": normalized, "method": method},
                    )
                    return starlette_json_response_from_xwapi_error(error, request=request)
            elif required_scopes and not required_scopes.issubset(token_scopes):
                trace_id = get_trace_id(request)
                request.state.trace_id = trace_id
                error = AuthorizationError(
                    message="Token lacks required scopes",
                    details={
                        "path": normalized,
                        "method": method,
                        "required_scopes": sorted(required_scopes),
                        "token_scopes": sorted(token_scopes),
                    },
                    hint="Issue a token with the required scopes",
                )
                return starlette_json_response_from_xwapi_error(error, request=request)

        response = await call_next(request)

        usage_amount = float(getattr(server, "_api_token_usage_amount", 0.0) or 0.0)
        token_id = str(claims.get("token_id") or "")
        idempotency_key = request.headers.get("Idempotency-Key", "").strip() or None
        if usage_amount > 0 and token_id and 200 <= int(getattr(response, "status_code", 500)) < 400:
            try:
                await server.record_api_token_usage(
                    token_id=token_id,
                    amount=usage_amount,
                    operation=f"{method} {normalized}",
                    metadata={"path": normalized, "method": method},
                    idempotency_key=idempotency_key,
                )
            except ValueError as exc:
                logger.warning(
                    "API token usage debit rejected",
                    extra={"token_id": token_id, "path": normalized, "error": str(exc)},
                )
                error = AuthorizationError(
                    message=str(exc),
                    details={"token_id": token_id, "path": normalized},
                    hint="Recharge credits or adjust usage policy",
                )
                return starlette_json_response_from_xwapi_error(error, request=request)
            except Exception as exc:
                logger.error(
                    "API token usage metering failed",
                    extra={"token_id": token_id, "path": normalized, "error": str(exc)},
                )
                error = AuthorizationError(
                    message="Unable to meter API token usage",
                    details={"token_id": token_id, "path": normalized},
                )
                return starlette_json_response_from_xwapi_error(error, request=request)
        return response
