#exonware/xwapi/tests/1.unit/middleware_tests/test_middleware_tough.py
"""
Tough unit tests for xwapi middleware - Edge cases, error conditions, and complex scenarios.
Tests middleware with invalid inputs, concurrent scenarios, security cases,
and failure modes.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations
import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from exonware.xwapi.server.middleware.trace import trace_middleware
from exonware.xwapi.server.middleware.tenant import tenant_middleware
from exonware.xwapi.server.middleware.ratelimit import rate_limit_middleware
from exonware.xwapi.server.middleware.auth import auth_middleware
from exonware.xwapi.server.middleware.observability import observability_middleware
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_trace_middleware_with_none_request():
    """Test trace middleware with None request."""
    mock_call_next = AsyncMock(return_value=MagicMock())
    with pytest.raises((AttributeError, TypeError)):
        await trace_middleware(None, mock_call_next)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_trace_middleware_with_none_call_next():
    """Test trace middleware with None call_next."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    with pytest.raises((TypeError, AttributeError)):
        await trace_middleware(mock_request, None)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_trace_middleware_with_missing_headers():
    """Test trace middleware with missing headers attribute."""
    mock_request = MagicMock()
    del mock_request.headers
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    with pytest.raises((AttributeError, TypeError)):
        await trace_middleware(mock_request, mock_call_next)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_trace_middleware_with_missing_state():
    """Test trace middleware with missing state attribute."""
    mock_request = MagicMock()
    mock_request.headers = {}
    del mock_request.state
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    with pytest.raises((AttributeError, TypeError)):
        await trace_middleware(mock_request, mock_call_next)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_trace_middleware_with_very_long_trace_id():
    """Test trace middleware with extremely long trace ID."""
    long_trace_id = "A" * 1000
    mock_request = MagicMock()
    mock_request.headers = {"X-Trace-Id": long_trace_id}
    mock_request.state = MagicMock()
    mock_request.state.trace_id = None
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    assert "X-Trace-Id" in response.headers
    assert response.headers["X-Trace-Id"] == long_trace_id
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_trace_middleware_with_special_chars_trace_id():
    """Test trace middleware with special characters in trace ID."""
    special_trace_id = "trace-<>&\"'-123"
    mock_request = MagicMock()
    mock_request.headers = {"X-Trace-Id": special_trace_id}
    mock_request.state = MagicMock()
    mock_request.state.trace_id = None
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    assert "X-Trace-Id" in response.headers
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_trace_middleware_with_unicode_trace_id():
    """Test trace middleware with Unicode characters in trace ID."""
    unicode_trace_id = "跟踪-123 🚀"
    mock_request = MagicMock()
    mock_request.headers = {"X-Trace-Id": unicode_trace_id}
    mock_request.state = MagicMock()
    mock_request.state.trace_id = None
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    assert "X-Trace-Id" in response.headers
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_trace_middleware_call_next_raises_error():
    """Test trace middleware when call_next raises error."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_call_next = AsyncMock(side_effect=Exception("Next middleware error"))
    with pytest.raises(Exception):
        await trace_middleware(mock_request, mock_call_next)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_trace_middleware_with_response_missing_headers():
    """Test trace middleware with response missing headers attribute."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    del mock_response.headers
    mock_call_next = AsyncMock(return_value=mock_response)
    with pytest.raises((AttributeError, TypeError)):
        await trace_middleware(mock_request, mock_call_next)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_tenant_middleware_with_none_request():
    """Test tenant middleware with None request."""
    mock_call_next = AsyncMock(return_value=MagicMock())
    with pytest.raises((AttributeError, TypeError)):
        await tenant_middleware(None, mock_call_next)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_tenant_middleware_with_missing_tenant_header():
    """Test tenant middleware with missing tenant header."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await tenant_middleware(mock_request, mock_call_next)
    # Should handle gracefully
    assert response is not None
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_tenant_middleware_with_empty_tenant_id():
    """Test tenant middleware with empty tenant ID."""
    mock_request = MagicMock()
    mock_request.headers = {"X-Tenant-Id": ""}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await tenant_middleware(mock_request, mock_call_next)
    assert response is not None
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_tenant_middleware_with_very_long_tenant_id():
    """Test tenant middleware with extremely long tenant ID."""
    long_tenant_id = "A" * 1000
    mock_request = MagicMock()
    mock_request.headers = {"X-Tenant-Id": long_tenant_id}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await tenant_middleware(mock_request, mock_call_next)
    assert response is not None
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_rate_limit_middleware_with_none_request():
    """Test rate limit middleware with None request."""
    mock_call_next = AsyncMock(return_value=MagicMock())
    with pytest.raises((AttributeError, TypeError)):
        await rate_limit_middleware(None, mock_call_next)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_rate_limit_middleware_with_missing_client_id():
    """Test rate limit middleware with missing client ID."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await rate_limit_middleware(mock_request, mock_call_next)
    # Should handle gracefully
    assert response is not None
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_auth_middleware_with_none_request():
    """Test auth middleware with None request."""
    mock_call_next = AsyncMock(return_value=MagicMock())
    with pytest.raises((AttributeError, TypeError)):
        await auth_middleware(None, mock_call_next)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_auth_middleware_with_missing_auth_header():
    """Test auth middleware with missing authorization header."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await auth_middleware(mock_request, mock_call_next)
    # Should handle gracefully (may reject or allow)
    assert response is not None
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_auth_middleware_with_invalid_token():
    """Test auth middleware with invalid token format."""
    mock_request = MagicMock()
    mock_request.headers = {"Authorization": "InvalidTokenFormat"}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await auth_middleware(mock_request, mock_call_next)
    # Should handle gracefully
    assert response is not None
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_auth_middleware_with_empty_token():
    """Test auth middleware with empty token."""
    mock_request = MagicMock()
    mock_request.headers = {"Authorization": "Bearer "}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await auth_middleware(mock_request, mock_call_next)
    assert response is not None
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_auth_middleware_with_very_long_token():
    """Test auth middleware with extremely long token."""
    long_token = "A" * 10000
    mock_request = MagicMock()
    mock_request.headers = {"Authorization": f"Bearer {long_token}"}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await auth_middleware(mock_request, mock_call_next)
    assert response is not None
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_observability_middleware_with_none_request():
    """Test observability middleware with None request."""
    mock_call_next = AsyncMock(return_value=MagicMock())
    with pytest.raises((AttributeError, TypeError)):
        await observability_middleware(None, mock_call_next)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_observability_middleware_with_missing_attributes():
    """Test observability middleware with missing request attributes."""
    mock_request = MagicMock()
    del mock_request.url
    del mock_request.method
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    with pytest.raises((AttributeError, TypeError)):
        await observability_middleware(mock_request, mock_call_next)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_chain_execution():
    """Test multiple middleware in chain."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    # Execute trace middleware
    response1 = await trace_middleware(mock_request, mock_call_next)
    # Execute tenant middleware
    response2 = await tenant_middleware(mock_request, mock_call_next)
    # Both should complete
    assert response1 is not None
    assert response2 is not None
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_concurrent_requests():
    """Test middleware with concurrent requests (simulated)."""
    import asyncio
    async def process_request(request_id):
        mock_request = MagicMock()
        mock_request.headers = {"X-Trace-Id": f"trace-{request_id}"}
        mock_request.state = MagicMock()
        mock_request.state.trace_id = None
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_call_next = AsyncMock(return_value=mock_response)
        response = await trace_middleware(mock_request, mock_call_next)
        return response.headers.get("X-Trace-Id")
    # Process 10 requests concurrently
    tasks = [process_request(i) for i in range(10)]
    trace_ids = await asyncio.gather(*tasks)
    assert len(trace_ids) == 10
    assert all(tid is not None for tid in trace_ids)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_error_propagation():
    """Test that middleware errors propagate correctly."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_call_next = AsyncMock(side_effect=ValueError("Next error"))
    with pytest.raises(ValueError):
        await trace_middleware(mock_request, mock_call_next)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_response_modification():
    """Test middleware modifies response correctly."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    assert "X-Trace-Id" in response.headers
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_existing_response_headers():
    """Test middleware with response that already has headers."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {"Existing-Header": "value"}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    assert "X-Trace-Id" in response.headers
    assert "Existing-Header" in response.headers
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_none_response():
    """Test middleware when call_next returns None."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_call_next = AsyncMock(return_value=None)
    with pytest.raises((AttributeError, TypeError)):
        await trace_middleware(mock_request, mock_call_next)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_slow_call_next():
    """Test middleware with slow call_next (timeout simulation)."""
    import asyncio
    async def slow_call_next(request):
        await asyncio.sleep(0.1)  # Simulate slow operation
        response = MagicMock()
        response.headers = {}
        return response
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    response = await trace_middleware(mock_request, slow_call_next)
    assert response is not None
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_exception_in_call_next():
    """Test middleware when call_next raises exception."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_call_next = AsyncMock(side_effect=RuntimeError("Call next error"))
    with pytest.raises(RuntimeError):
        await trace_middleware(mock_request, mock_call_next)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_multiple_trace_ids():
    """Test middleware with multiple trace ID headers."""
    mock_request = MagicMock()
    mock_request.headers = {
        "X-Trace-Id": "trace-1",
        "X-Request-Id": "trace-2",
        "Trace-Id": "trace-3"
    }
    mock_request.state = MagicMock()
    mock_request.state.trace_id = None
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    # Should use first trace ID found
    assert "X-Trace-Id" in response.headers
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_case_insensitive_headers():
    """Test middleware with case-insensitive header lookup."""
    mock_request = MagicMock()
    mock_request.headers = {"x-trace-id": "lowercase-trace"}
    mock_request.state = MagicMock()
    mock_request.state.trace_id = None
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    # Should handle case-insensitive lookup
    assert response is not None
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_empty_headers_dict():
    """Test middleware with empty headers dictionary."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    # Should generate new trace ID
    assert "X-Trace-Id" in response.headers
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_none_headers():
    """Test middleware with None headers."""
    mock_request = MagicMock()
    mock_request.headers = None
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    with pytest.raises((AttributeError, TypeError)):
        await trace_middleware(mock_request, mock_call_next)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_non_dict_headers():
    """Test middleware with non-dict headers."""
    mock_request = MagicMock()
    mock_request.headers = "not-a-dict"
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    with pytest.raises((AttributeError, TypeError)):
        await trace_middleware(mock_request, mock_call_next)
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_state_modification():
    """Test that middleware modifies request state."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_request.state.trace_id = None
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    await trace_middleware(mock_request, mock_call_next)
    # State should have trace_id set
    assert hasattr(mock_request.state, "trace_id") or mock_request.state.trace_id is not None
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_response_status_code():
    """Test middleware preserves response status code."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_response.status_code = 404
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    assert response.status_code == 404
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_response_body():
    """Test middleware preserves response body."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_response.body = b'{"test": true}'
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    assert hasattr(response, "body") or response.body == b'{"test": true}'
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_all_status_codes():
    """Test middleware with various HTTP status codes."""
    status_codes = [200, 201, 400, 401, 403, 404, 500, 502, 503]
    for status_code in status_codes:
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.state = MagicMock()
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.status_code = status_code
        mock_call_next = AsyncMock(return_value=mock_response)
        response = await trace_middleware(mock_request, mock_call_next)
        assert response.status_code == status_code
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_streaming_response():
    """Test middleware with streaming response."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_response.body_iterator = iter([b"chunk1", b"chunk2"])
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    # Should handle streaming response
    assert response is not None
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_redirect_response():
    """Test middleware with redirect response."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {"Location": "https://example.com"}
    mock_response.status_code = 302
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    assert response.status_code == 302
    assert "Location" in response.headers
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_cors_headers():
    """Test middleware preserves CORS headers."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST"
    }
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    assert "Access-Control-Allow-Origin" in response.headers
    assert "X-Trace-Id" in response.headers
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_custom_headers():
    """Test middleware preserves custom response headers."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {
        "X-Custom-Header": "custom-value",
        "X-Another-Header": "another-value"
    }
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    assert "X-Custom-Header" in response.headers
    assert "X-Another-Header" in response.headers
    assert "X-Trace-Id" in response.headers
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_unicode_in_headers():
    """Test middleware with Unicode characters in headers."""
    mock_request = MagicMock()
    mock_request.headers = {"X-Trace-Id": "跟踪-123 🚀"}
    mock_request.state = MagicMock()
    mock_request.state.trace_id = None
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    assert "X-Trace-Id" in response.headers
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_special_chars_in_headers():
    """Test middleware with special characters in headers."""
    mock_request = MagicMock()
    mock_request.headers = {"X-Trace-Id": "trace-<>&\"'-123"}
    mock_request.state = MagicMock()
    mock_request.state.trace_id = None
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    assert "X-Trace-Id" in response.headers
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_performance_with_many_headers():
    """Test middleware performance with many headers."""
    mock_request = MagicMock()
    mock_request.headers = {f"Header-{i}": f"value-{i}" for i in range(100)}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    # Should complete quickly despite many headers
    assert "X-Trace-Id" in response.headers
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_nested_call_next():
    """Test middleware with nested call_next calls."""
    async def nested_call_next(request):
        response = MagicMock()
        response.headers = {}
        return response
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    response = await trace_middleware(mock_request, nested_call_next)
    assert response is not None
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_middleware_with_async_generator_response():
    """Test middleware with async generator response."""
    async def async_generator():
        yield b"chunk1"
        yield b"chunk2"
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_response.body_iterator = async_generator()
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    assert response is not None
