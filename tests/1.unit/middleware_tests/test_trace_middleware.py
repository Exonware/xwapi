#exonware/xwapi/tests/1.unit/middleware_tests/test_trace_middleware.py
"""
Unit tests for trace middleware.
Tests trace ID generation and injection.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations
import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from exonware.xwapi.server.middleware.trace import trace_middleware
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_trace_middleware_generates_trace_id():
    """Test that trace middleware generates trace ID if not present."""
    mock_request = MagicMock()
    mock_request.headers = {"X-Trace-Id": None}
    mock_request.state = MagicMock()
    mock_request.state.trace_id = None
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    # Trace ID should be set in request state
    assert hasattr(mock_request.state, "trace_id")
    # Response should have X-Trace-Id header
    assert "X-Trace-Id" in response.headers
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_trace_middleware_uses_existing_trace_id():
    """Test that trace middleware uses existing trace ID from header."""
    existing_trace_id = "existing-trace-123"
    mock_request = MagicMock()
    mock_request.headers = {"X-Trace-Id": existing_trace_id}
    mock_request.state = MagicMock()
    mock_request.state.trace_id = None
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    # Should use existing trace ID
    assert response.headers["X-Trace-Id"] == existing_trace_id
@pytest.mark.xwapi_unit
@pytest.mark.asyncio
async def test_trace_middleware_calls_next():
    """Test that trace middleware calls next middleware."""
    mock_request = MagicMock()
    mock_request.headers = {}
    mock_request.state = MagicMock()
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_call_next = AsyncMock(return_value=mock_response)
    response = await trace_middleware(mock_request, mock_call_next)
    # Should call next middleware
    mock_call_next.assert_called_once_with(mock_request)
    assert response == mock_response
