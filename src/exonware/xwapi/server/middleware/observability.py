#!/usr/bin/env python3
"""
#exonware/xwapi/src/exonware/xwapi/middleware/observability.py
Observability Middleware
Structured logging, metrics collection, and OpenTelemetry integration.
Tracks request count, latency, error rate, and tenant usage.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.2
"""

from typing import Callable
from time import time
from starlette.requests import Request
from starlette.responses import Response
async def observability_middleware(request: Request, call_next: Callable) -> Response:
    """
    Observability middleware.
    Tracks:
    - Request count
    - Latency (p50, p95, p99)
    - Error rate
    - Tenant usage
    Integrates with OpenTelemetry for distributed tracing.
    Emits structured logs with trace_id correlation.
    Args:
        request: FastAPI request object
        call_next: Next middleware handler
    Returns:
        Response
    """
    # Get trace ID (should be set by trace middleware)
    trace_id = getattr(request.state, "trace_id", None)
    # Start timer
    start_time = time()
    # Process request
    try:
        response = await call_next(request)
        status_code = response.status_code
        error = status_code >= 400
    except Exception as e:
        status_code = 500
        error = True
        raise
    finally:
        # Calculate latency
        latency_ms = (time() - start_time) * 1000
        # Structured logging
        try:
            from exonware.xwsystem import get_logger
            logger = get_logger(__name__)
            log_data = {
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "trace_id": trace_id,
                "error": error,
            }
            # Add tenant_id if available
            if hasattr(request.state, "tenant_id"):
                log_data["tenant_id"] = request.state.tenant_id
            # Add client IP
            if request.client:
                log_data["client_ip"] = request.client.host
            # Log based on status
            if error:
                logger.warning(f"Request failed: {request.method} {request.url.path}", extra=log_data)
            else:
                logger.info(f"Request: {request.method} {request.url.path}", extra=log_data)
        except ImportError:
            pass  # xwsystem not available
        # OpenTelemetry metrics
        try:
            from opentelemetry import metrics
            from opentelemetry.metrics import get_meter
            meter = get_meter(__name__)
            request_counter = meter.create_counter(
                "http_requests_total",
                description="Total HTTP requests"
            )
            latency_histogram = meter.create_histogram(
                "http_request_duration_ms",
                description="HTTP request latency in milliseconds"
            )
            # Record metrics
            request_counter.add(1, {
                "method": request.method,
                "status_code": str(status_code),
                "path": request.url.path,
            })
            latency_histogram.record(latency_ms, {
                "method": request.method,
                "status_code": str(status_code),
                "path": request.url.path,
            })
        except ImportError:
            pass  # OpenTelemetry not available
    return response
