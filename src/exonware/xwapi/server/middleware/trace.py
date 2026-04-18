#!/usr/bin/env python3
"""
#exonware/xwapi/src/exonware/xwapi/middleware/trace.py
Trace ID Middleware
Injects trace_id into request state and response headers for request correlation
and OpenTelemetry integration.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.12
"""

from collections.abc import Callable
from uuid import uuid4
from starlette.requests import Request
from starlette.responses import Response
async def trace_middleware(request: Request, call_next: Callable) -> Response:
    """
    Trace ID middleware.
    Generates trace_id for each request and injects it into:
    - Request state (request.state.trace_id)
    - Response headers (X-Trace-Id)
    - Logs (via structured logging)
    Supports OpenTelemetry correlation:
    - Checks for existing trace_id in headers (X-Trace-Id)
    - Checks for OpenTelemetry trace context
    - Generates new UUID if not found
    Args:
        request: FastAPI request object
        call_next: Next middleware handler
    Returns:
        Response with X-Trace-Id header
    """
    # Check for existing trace ID in headers
    trace_id = request.headers.get("X-Trace-Id")
    # Check for OpenTelemetry trace context
    if not trace_id:
        try:
            from opentelemetry import trace
            span = trace.get_current_span()
            if span and span.is_recording():
                span_context = span.get_span_context()
                if span_context.is_valid:
                    trace_id = format(span_context.trace_id, "032x")
        except ImportError:
            pass  # OpenTelemetry not available
    # Generate new trace ID if not found
    if not trace_id:
        trace_id = str(uuid4())
    # Store in request state
    request.state.trace_id = trace_id
    # Process request
    response = await call_next(request)
    # Add trace ID to response headers
    response.headers["X-Trace-Id"] = trace_id
    return response
