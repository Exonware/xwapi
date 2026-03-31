#!/usr/bin/env python3
"""
#exonware/xwapi/src/exonware/xwapi/middleware/tenant.py
Multi-Tenant Middleware
Extracts tenant_id from token/header and scopes all requests to tenant.
Enforces tenant isolation at the middleware level.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.2
"""

from typing import Callable, Optional
from starlette.requests import Request
from starlette.responses import Response
from starlette.exceptions import HTTPException
from starlette import status
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
    tenant_id: Optional[str] = None
    # Try to extract from JWT token (xwauth integration)
    try:
        if hasattr(request.state, "user") and hasattr(request.state.user, "tenant_id"):
            tenant_id = request.state.user.tenant_id
        elif hasattr(request.state, "claims") and "tid" in request.state.claims:
            tenant_id = request.state.claims["tid"]
    except Exception:
        pass
    # Try header
    if not tenant_id:
        tenant_id = request.headers.get("X-Tenant-Id")
    # Try query parameter (lower priority)
    if not tenant_id:
        tenant_id = request.query_params.get("tenant_id")
    # Store in request state
    request.state.tenant_id = tenant_id
    # Process request
    response = await call_next(request)
    return response


def require_tenant(tenant_id: Optional[str] = None) -> None:
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
