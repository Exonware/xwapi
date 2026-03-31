#!/usr/bin/env python3
"""
#exonware/xwapi/src/exonware/xwapi/middleware/auth.py
Authentication Middleware
Pluggable authentication middleware with xwauth integration.
Validates tokens and injects user context into request state.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.2
"""

from typing import Callable, Optional, Any
from starlette.requests import Request
from starlette.responses import Response
from starlette.exceptions import HTTPException
from starlette import status
async def auth_middleware(
    request: Request,
    call_next: Callable,
    require_auth: bool = False,
    auth_provider: Optional[Any] = None,
) -> Response:
    """
    Authentication middleware.
    Validates authentication tokens and injects user context.
    Supports pluggable authentication providers (xwauth).
    Extracts token from:
    1. Authorization header (Bearer token)
    2. Cookie (session token)
    Stores in request.state:
    - user: User object (if authenticated)
    - claims: JWT claims (if token is JWT)
    - tenant_id: Tenant ID from token
    Args:
        request: FastAPI request object
        call_next: Next middleware handler
        require_auth: Whether authentication is required (raises 401 if missing)
        auth_provider: Optional xwauth provider instance
    Returns:
        Response
    Raises:
        HTTPException: If require_auth=True and authentication fails
    """
    # Try to get token from Authorization header
    token: Optional[str] = None
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]  # Remove "Bearer " prefix
    # Try to get token from cookie
    if not token:
        token = request.cookies.get("session_token") or request.cookies.get("access_token")
    # Validate token if present
    if token and auth_provider:
        try:
            # Use xwauth to validate token
            user = await auth_provider.validate_token(token)
            if user:
                request.state.user = user
                request.state.authenticated = True
                # Extract tenant_id if available
                if hasattr(user, "tenant_id"):
                    request.state.tenant_id = user.tenant_id
                elif hasattr(user, "claims") and "tid" in user.claims:
                    request.state.tenant_id = user.claims["tid"]
                # Store claims if JWT
                if hasattr(user, "claims"):
                    request.state.claims = user.claims
        except Exception:
            # Token validation failed, but we continue if require_auth=False
            if require_auth:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
    elif not token:
        request.state.authenticated = False
        if require_auth:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
    # Process request
    response = await call_next(request)
    return response


def require_auth_dependency(auth_provider: Optional[Any] = None):
    """
    Dependency function for route-level authentication.
    Usage:
        @app.get("/protected")
        async def protected_route(user = Depends(require_auth_dependency())):
            return {"user_id": user.id}
    Args:
        auth_provider: Optional xwauth provider instance
    Returns:
        Dependency function
    """
    try:
        from fastapi import Depends
        from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    except ImportError as exc:
        raise RuntimeError(
            "require_auth_dependency requires FastAPI. "
            "Install the fastapi engine extras to use route-level dependency auth."
        ) from exc

    security = HTTPBearer(auto_error=False)

    async def get_current_user(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Any:
        """Get current authenticated user."""
        token: Optional[str] = None
        if credentials:
            token = credentials.credentials
        else:
            # Try cookie
            token = request.cookies.get("session_token") or request.cookies.get("access_token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        if auth_provider:
            try:
                user = await auth_provider.validate_token(token)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired token"
                    )
                return user
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Authentication failed: {str(e)}"
                )
        else:
            # No auth provider, return mock user from request state
            if hasattr(request.state, "user"):
                return request.state.user
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
    return get_current_user
