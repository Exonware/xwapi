#exonware/xwapi/tests/1.unit/serialization_tests/test_serialization.py
"""
Unit tests for serialization utilities.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations
import pytest
from exonware.xwapi.serialization import (
    get_content_type,
    create_custom_format_response
)
@pytest.mark.xwapi_unit

def test_get_content_type():
    """Test getting content type from request."""
    from fastapi import Request
    from unittest.mock import MagicMock
    # Mock request with Content-Type header
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {"content-type": "application/json"}
    content_type = get_content_type(mock_request)
    assert content_type == "application/json" or "json" in content_type.lower()
@pytest.mark.xwapi_unit

def test_create_custom_format_response():
    """Test creating custom format response."""
    data = {"key": "value"}
    response = create_custom_format_response(data, "application/json")
    assert response is not None
    # Should return a response object
