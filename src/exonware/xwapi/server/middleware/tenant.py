#!/usr/bin/env python3
"""
#exonware/xwapi/src/exonware/xwapi/middleware/tenant.py
Multi-Tenant Middleware
Extracts tenant_id from token/header and scopes all requests to tenant.
Enforces tenant isolation at the middleware level.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.12
"""

from collections.abc import Callable
from starlette.requests import Request
from starlette.responses import Response
from starlette.exceptions import HTTPException
from starlette import status
from exonware.xwapi.errors import AuthorizationError
from exonware.xwapi.server.http import starlette_json_response_from_xwapi_error
from exonware.xwsystem.security.normalization import resolve_tenant_id_layered

def _flag_enabled(server: object, name: str, default: bool) -> bool:
    """Read a boolean server flag; ignore non-bools (e.g. MagicMock auto-attrs in tests)."""
    v = getattr(server, name, default)
    return default if not isinstance(v, bool) else v

def _conflicts(candidate: str | None, principal_tenant: str | None) -> bool:
    if not candidate or not principal_tenant:
        return False
    return str(candidate) != str(principal_tenant)

def _tenant_conflict_response(
    request: Request,
    *,
    principal_tenant: str | None,
    header_tenant: str | None,
    query_tenant: str | None,
) -> Response:
    error = AuthorizationError(
        message="Tenant override does not match authenticated tenant",
        details={
            "principal_tenant": principal_tenant,
            "header_tenant": header_tenant,
            "query_tenant": query_tenant,
        },
        hint="Use the authenticated tenant context or disable override headers/params.",
    )
    return starlette_json_response_from_xwapi_error(error, request=request)
async def tenant_middleware(request: Request, call_next: Callable) -> Response:
    """
    Multi-tenant middleware.
    Extracts tenant_id from:
    1. JWT token (tid claim)
    2. Request header (X-Tenant-Id)
    3. Query parameter (tenant_id)
    Stores tenant_id in request.state.tenant_id for use in route handlers.
    Enforces tenant isolation - all database queries should filter by tenant_id.
    Args:
        request: FastAPI request object
        call_next: Next middleware handler
    Returns:
        Response
    Raises:
        HTTPException: If tenant_id is required but not found
    """
    server = getattr(getattr(request, "app", None), "state", None)
    xwapi_server = getattr(server, "xwapi_server", None) if server is not None else None
    reject_conflicting_override = _flag_enabled(
        xwapi_server,
        "_tenant_reject_conflicting_override",
        False,
    )
    require_authenticated_source = _flag_enabled(
        xwapi_server,
        "_tenant_require_authenticated_source",
        False,
    )

    header_tenant = request.headers.get("X-Tenant-Id")
    query_tenant = request.query_params.get("tenant_id")
    principal_tenant = resolve_tenant_id_layered(
        principal=getattr(request.state, "user", None),
        request_claims=getattr(request.state, "claims", None),
        header_tenant_id=None,
        query_tenant_id=None,
    )

    if principal_tenant and reject_conflicting_override:
        if _conflicts(header_tenant, principal_tenant) or _conflicts(query_tenant, principal_tenant):
            return _tenant_conflict_response(
                request,
                principal_tenant=principal_tenant,
                header_tenant=header_tenant,
                query_tenant=query_tenant,
            )

    if principal_tenant:
        tenant_id: str | None = principal_tenant
    elif require_authenticated_source:
        tenant_id = None
    else:
        tenant_id = resolve_tenant_id_layered(
            principal=None,
            request_claims=None,
            header_tenant_id=header_tenant,
            query_tenant_id=query_tenant,
        )
    # Store in request state
    request.state.tenant_id = tenant_id
    # Process request
    response = await call_next(request)
    return response

def require_tenant(tenant_id: str | None = None) -> None:
    """
    Require tenant_id to be present.
    This is a helper that can be used in route handlers or as a dependency.
    Args:
        tenant_id: Optional tenant_id to check (if None, checks request.state.tenant_id)
    Raises:
        HTTPException: If tenant_id is missing
    """
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id is required"
        )
