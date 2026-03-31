#!/usr/bin/env python3
"""
#exonware/xwapi/src/exonware/xwapi/middleware/ratelimit.py
Rate Limiting Middleware
Per-IP, per-client, per-tenant rate limiting with configurable limits per endpoint.
Returns standard rate limit headers.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.2
"""

from typing import Callable, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from starlette.requests import Request
from starlette.responses import Response
from starlette.exceptions import HTTPException
from starlette import status
# Simple in-memory rate limiter (production should use Redis)
_rate_limit_storage: dict[str, list[datetime]] = defaultdict(list)


class RateLimiter:
    """Simple rate limiter implementation."""

    def __init__(
        self,
        calls: int = 100,
        period: timedelta = timedelta(minutes=1),
        per_ip: bool = True,
        per_client: bool = False,
        per_tenant: bool = False,
    ):
        """
        Initialize rate limiter.
        Args:
            calls: Number of calls allowed
            period: Time period for rate limit window
            per_ip: Limit per IP address
            per_client: Limit per client (requires client_id in request)
            per_tenant: Limit per tenant (requires tenant_id in request)
        """
        self.calls = calls
        self.period = period
        self.per_ip = per_ip
        self.per_client = per_client
        self.per_tenant = per_tenant

    def get_key(self, request: Request) -> Optional[str]:
        """Get rate limit key for request."""
        parts = []
        if self.per_ip:
            # Get client IP
            client_ip = request.client.host if request.client else "unknown"
            parts.append(f"ip:{client_ip}")
        if self.per_client and hasattr(request.state, "client_id"):
            parts.append(f"client:{request.state.client_id}")
        if self.per_tenant and hasattr(request.state, "tenant_id"):
            tenant_id = request.state.tenant_id
            if tenant_id:
                parts.append(f"tenant:{tenant_id}")
        return ":".join(parts) if parts else None

    def is_allowed(self, key: str) -> tuple[bool, int, datetime]:
        """
        Check if request is allowed.
        Returns:
            Tuple of (allowed, remaining, reset_time)
        """
        now = datetime.now(timezone.utc)
        # Get or create bucket
        if key not in _rate_limit_storage:
            _rate_limit_storage[key] = []
        bucket = _rate_limit_storage[key]
        # Remove old entries
        cutoff = now - self.period
        bucket[:] = [ts for ts in bucket if ts > cutoff]
        # Check limit
        if len(bucket) >= self.calls:
            reset_time = bucket[0] + self.period if bucket else now + self.period
            return False, 0, reset_time
        # Add current request
        bucket.append(now)
        remaining = max(0, self.calls - len(bucket))
        reset_time = bucket[0] + self.period if bucket else now + self.period
        return True, remaining, reset_time
# Default rate limiter
_default_rate_limiter = RateLimiter(
    calls=100,
    period=timedelta(minutes=1),
    per_ip=True,
)
async def rate_limit_middleware(
    request: Request,
    call_next: Callable,
    limiter: Optional[RateLimiter] = None,
) -> Response:
    """
    Rate limiting middleware.
    Applies rate limits based on IP, client, and/or tenant.
    Returns standard rate limit headers:
    - X-RateLimit-Limit: Maximum requests allowed
    - X-RateLimit-Remaining: Remaining requests
    - X-RateLimit-Reset: Reset time (Unix timestamp)
    Args:
        request: FastAPI request object
        call_next: Next middleware handler
        limiter: Optional RateLimiter instance (uses default if None)
    Returns:
        Response with rate limit headers
    Raises:
        HTTPException: If rate limit exceeded (429)
    """
    limiter = limiter or _default_rate_limiter
    key = limiter.get_key(request)
    if key:
        allowed, remaining, reset_time = limiter.is_allowed(key)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(limiter.calls),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_time.timestamp())),
                    "Retry-After": str(
                        max(0, int((reset_time - datetime.now(timezone.utc)).total_seconds()))
                    ),
                }
            )
        # Process request
        response = await call_next(request)
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limiter.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time.timestamp()))
        return response
    # No rate limiting key, proceed normally
    return await call_next(request)
