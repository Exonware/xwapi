#!/usr/bin/env python3
"""
#exonware/xwapi/src/exonware/xwapi/errors.py
Uniform error model for publishers and consumers of exposable actions (HTTP and beyond).

Stable shapes for APIs with trace_id, structured codes, and correlation hooks so servers
and clients agree on failure semantics across engines (FastAPI, Flask, …).

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.5
"""

from __future__ import annotations
from typing import Any, Optional
from uuid import uuid4
# FastAPI imports are moved to function scope where they're actually used
# With __future__ annotations, type hints become strings and aren't evaluated at runtime
# Using string annotations for FastAPI types to avoid any import at module level


class XWAPIError(Exception):
    """Base exception for xwapi library."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict[str, Any] | None = None,
        hint: str | None = None,
    ):
        """
        Initialize API error.
        Args:
            message: Human-readable error message
            code: Machine-readable error code (defaults to class name)
            details: Additional context (dict)
            hint: Optional hint for resolution
        """
        super().__init__(message)
        self._message = message  # Store in private attribute
        # Use class name as default only if code is None, preserve empty string if explicitly provided
        self.code = self.__class__.__name__ if code is None else code
        # Create a copy of details to prevent external modifications
        self.details = dict(details) if details else {}
        self.hint = hint
    @property

    def message(self) -> str:
        """Get error message (immutable after creation)."""
        return self._message
    @message.setter

    def message(self, value: str) -> None:
        """Prevent modification of message after creation."""
        # Silently ignore attempts to modify (maintains immutability)
        pass


class ValidationError(XWAPIError):
    """Request validation errors (400)."""
    pass


class AuthenticationError(XWAPIError):
    """Authentication failures (401)."""
    pass


class AuthorizationError(XWAPIError):
    """Permission denied (403)."""
    pass


class NotFoundError(XWAPIError):
    """Resource not found (404)."""
    pass


class RateLimitError(XWAPIError):
    """Rate limit exceeded (429)."""
    pass


class InternalError(XWAPIError):
    """Server errors (500)."""
    pass


class OpenAPIGenerationError(XWAPIError):
    """Error during OpenAPI generation."""
    pass


class FastAPICreationError(XWAPIError):
    """Error during FastAPI app creation."""
    pass


class EntityMappingError(XWAPIError):
    """Error mapping entity to API endpoint."""
    pass


class OAuth2ConfigurationError(XWAPIError):
    """Error in OAuth 2.0 configuration."""
    pass


class EndpointConfigurationError(XWAPIError):
    """Error in endpoint configuration."""
    pass


class ServerLifecycleError(XWAPIError):
    """Error in API server lifecycle management."""
    pass


class StorageUnavailableError(XWAPIError):
    """Persistence backend unavailable or failed."""
    pass


class ServicePausedError(XWAPIError):
    """Request rejected because endpoint/service is paused."""
    pass
# =============================================================================
# Generic HTTP Status Codes (Engine-Agnostic)
# =============================================================================
# Standard HTTP status codes as integers - works with any framework
# No framework dependencies (FastAPI, Flask, etc.)
# 2xx Success
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_202_ACCEPTED = 202
HTTP_204_NO_CONTENT = 204
# 4xx Client Errors
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_409_CONFLICT = 409
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_429_TOO_MANY_REQUESTS = 429
# 5xx Server Errors
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_501_NOT_IMPLEMENTED = 501
HTTP_502_BAD_GATEWAY = 502
HTTP_503_SERVICE_UNAVAILABLE = 503
HTTP_504_GATEWAY_TIMEOUT = 504


def get_http_status_code(error: XWAPIError) -> int:
    """
    Get HTTP status code for XWAPIError (engine-agnostic).
    Maps error codes to standard HTTP status codes.
    Engine-agnostic: Returns integer status codes usable by any framework.
    Args:
        error: XWAPIError instance
    Returns:
        HTTP status code (integer)
    """
    if isinstance(error, ValidationError):
        return HTTP_400_BAD_REQUEST
    if isinstance(error, AuthenticationError):
        return HTTP_401_UNAUTHORIZED
    if isinstance(error, AuthorizationError):
        return HTTP_403_FORBIDDEN
    if isinstance(error, NotFoundError):
        return HTTP_404_NOT_FOUND
    if isinstance(error, RateLimitError):
        return HTTP_429_TOO_MANY_REQUESTS
    if isinstance(error, StorageUnavailableError):
        return HTTP_503_SERVICE_UNAVAILABLE
    if isinstance(error, ServicePausedError):
        return HTTP_503_SERVICE_UNAVAILABLE

    error_status_map: dict[str, int] = {
        "ValidationError": HTTP_400_BAD_REQUEST,
        "AuthenticationError": HTTP_401_UNAUTHORIZED,
        "AuthorizationError": HTTP_403_FORBIDDEN,
        "NotFoundError": HTTP_404_NOT_FOUND,
        "RateLimitError": HTTP_429_TOO_MANY_REQUESTS,
        "InternalError": HTTP_500_INTERNAL_SERVER_ERROR,
        "OpenAPIGenerationError": HTTP_500_INTERNAL_SERVER_ERROR,
        "FastAPICreationError": HTTP_500_INTERNAL_SERVER_ERROR,
        "EntityMappingError": HTTP_500_INTERNAL_SERVER_ERROR,
        "OAuth2ConfigurationError": HTTP_500_INTERNAL_SERVER_ERROR,
        "EndpointConfigurationError": HTTP_500_INTERNAL_SERVER_ERROR,
        "ServerLifecycleError": HTTP_500_INTERNAL_SERVER_ERROR,
        "StorageUnavailableError": HTTP_503_SERVICE_UNAVAILABLE,
        "ServicePausedError": HTTP_503_SERVICE_UNAVAILABLE,
        "ServicePaused": HTTP_503_SERVICE_UNAVAILABLE,
        "ConnectionError": HTTP_502_BAD_GATEWAY,
    }
    return error_status_map.get(error.code, HTTP_500_INTERNAL_SERVER_ERROR)


def http_status_to_xwapi_error(status_code: int, message: str, *, details: dict[str, Any] | None = None) -> XWAPIError:
    """
    Translate generic HTTP status codes into the canonical XWAPIError hierarchy.
    This adapter is engine/protocol agnostic and can be reused by any HTTP engine.
    """
    error_details = {"status_code": status_code, **(details or {})}
    if status_code == HTTP_404_NOT_FOUND:
        return NotFoundError(message=message, details=error_details)
    if status_code == HTTP_401_UNAUTHORIZED:
        return AuthenticationError(message=message, details=error_details)
    if status_code == HTTP_403_FORBIDDEN:
        return AuthorizationError(message=message, details=error_details)
    if status_code == HTTP_429_TOO_MANY_REQUESTS:
        return RateLimitError(message=message, details=error_details)
    if status_code in (HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY):
        return ValidationError(message=message, details=error_details)
    return XWAPIError(message=message, code=f"HTTP_{status_code}", details=error_details)


def error_to_http_response(
    error: XWAPIError,
    request: Any | None = None,
    include_details: bool = True,
) -> tuple[dict[str, Any], int]:
    """
    Convert XWAPIError to HTTP response format (engine-agnostic).
    Creates uniform error response with HTTP status code.
    Engine-agnostic: Returns tuple of (response_dict, status_code) usable by any framework.
    Args:
        error: XWAPIError instance
        request: Optional request object (for trace_id extraction)
        include_details: Whether to include details field
    Returns:
        Tuple of (error_response_dict, http_status_code)
    """
    trace_id = None
    if request:
        trace_id = get_trace_id(request)
    error_response = create_error_response(
        error,
        trace_id=trace_id,
        include_details=include_details,
    )
    status_code = get_http_status_code(error)
    return error_response, status_code


def xwapi_error_to_http_parts(
    error: XWAPIError,
    request: Any | None = None,
    include_details: bool = True,
    extra_headers: dict[str, str] | None = None,
) -> tuple[dict[str, Any], int, dict[str, str]]:
    """
    Convert an XWAPIError into framework-neutral HTTP response parts.
    Returns body, status code, and headers so engines/adapters can render natively.
    """
    trace_id = None
    if request is not None:
        trace_id = get_trace_id(request)

    body = create_error_response(error, trace_id=trace_id, include_details=include_details)
    status_code = get_http_status_code(error)
    headers = get_error_headers(trace_id=trace_id)
    if extra_headers:
        headers.update(extra_headers)
    return body, status_code, headers


def get_trace_id(request: Any) -> str:
    """
    Get or generate trace_id for request (engine-agnostic).
    Checks for existing trace_id in:
    1. Request headers (X-Trace-Id) - via request.headers.get() or request.headers["X-Trace-Id"]
    2. Request state (set by middleware) - via request.state.trace_id
    3. Generates new UUID if not found
    Engine-agnostic: Works with any request object that has:
    - headers attribute (dict-like with .get() method or [] access)
    - state attribute (optional, with trace_id attribute)
    Args:
        request: Request object (engine-agnostic - FastAPI, Flask, etc.)
    Returns:
        Trace ID string (UUID)
    """
    # Check headers first (engine-agnostic)
    state = getattr(request, "state", None)
    headers = getattr(request, "headers", None)
    if headers:
        # Try dict-like access (.get() method)
        if hasattr(headers, "get"):
            trace_id = headers.get("X-Trace-Id")
            if trace_id:
                if state is not None:
                    setattr(state, "trace_id", trace_id)
                return trace_id
        # Try dict-like access ([] operator)
        elif hasattr(headers, "__getitem__"):
            try:
                trace_id = headers["X-Trace-Id"]
                if trace_id:
                    if state is not None:
                        setattr(state, "trace_id", trace_id)
                    return trace_id
            except (KeyError, TypeError):
                pass
    # Check request state (set by middleware) - engine-agnostic
    if state and hasattr(state, "trace_id"):
        trace_id = getattr(state, "trace_id", None)
        if trace_id is not None:
            return trace_id
    # Generate new trace ID
    trace_id = str(uuid4())
    if state is not None:
        setattr(state, "trace_id", trace_id)
    return trace_id


def create_error_response(
    error: XWAPIError,
    trace_id: str | None = None,
    include_details: bool = True,
) -> dict[str, Any]:
    """
    Create uniform error response shape.
    Error Shape:
    {
        "code": "ERROR_CODE",           # Machine-readable error code
        "message": "Human-readable message",
        "details": {...},                # Additional context
        "trace_id": "uuid",              # Correlation ID
        "hint": "Optional hint for resolution"
    }
    Args:
        error: XWAPIError instance
        trace_id: Optional trace ID (generates if None)
        include_details: Whether to include details field
    Returns:
        Error response dictionary
    """
    response = {
        "code": error.code,
        "message": error.message,
    }
    # Handle trace_id: preserve None if explicitly provided, generate UUID only if not provided
    if trace_id is not None:
        response["trace_id"] = trace_id
    else:
        # Only generate UUID if trace_id was not provided (default None)
        # If explicitly None, preserve it as None
        response["trace_id"] = None
    if include_details and error.details:
        response["details"] = error.details
    if error.hint:
        response["hint"] = error.hint
    return response
# =============================================================================
# Generic HTTP Response Headers (Engine-Agnostic)
# =============================================================================


def get_error_headers(trace_id: str | None = None) -> dict[str, str]:
    """
    Get standard error response headers (engine-agnostic).
    Args:
        trace_id: Optional trace ID to include in headers
    Returns:
        Dictionary of headers
    """
    headers: dict[str, str] = {}
    if trace_id:
        headers["X-Trace-Id"] = trace_id
    return headers
