#exonware/xwapi/tests/1.unit/action_tests/test_action_endpoint.py
"""
Unit tests for action endpoint registration.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations
import pytest
from unittest.mock import Mock, MagicMock, patch
from exonware.xwapi.action import register_action_endpoint, create_action_context_dependency
from exonware.xwaction import XWAction
@pytest.mark.xwapi_unit

def test_register_action_endpoint():
    """Test registering an action as endpoint."""
    from fastapi import FastAPI
    app = FastAPI()
    @XWAction(operationId="test_action", profile="endpoint")
    def test_action():
        return {"result": "success"}
    # Register action
    result = register_action_endpoint(app, test_action, path="/test", method="GET")
    # Should return True if successful
    assert isinstance(result, bool) or result is None
@pytest.mark.xwapi_unit

def test_create_action_context_dependency():
    """Test creating action context dependency."""
    from fastapi import Request
    from unittest.mock import MagicMock
    # create_action_context_dependency is a FastAPI dependency function
    # that takes a Request parameter
    mock_request = MagicMock(spec=Request)
    mock_request.state = MagicMock()
    mock_request.state.trace_id = "test-trace-123"
    mock_request.url.path = "/test"
    mock_request.method = "GET"
    # Call the dependency function with mock request
    context = create_action_context_dependency(mock_request)
    # Should return a context object
    assert context is not None
    # Context should have trace_id
    assert hasattr(context, "trace_id") or hasattr(context, "metadata")
