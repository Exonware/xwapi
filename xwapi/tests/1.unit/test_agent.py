#exonware/xwapi/tests/1.unit/test_agent.py
"""
Unit tests for XWApiAgent.
Tests the auto-discovery logic, HTTP helper methods, and authentication management.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""
from __future__ import annotations
import pytest
from unittest.mock import MagicMock, patch, mock_open
import requests
from typing import Optional
from exonware.xwapi import XWApiAgent
from exonware.xwaction import XWAction, ActionProfile
# --- Mocks & Fixtures ---
class MockAgent(XWApiAgent):
    """Test agent subclass with actions."""
    @XWAction(operationId="test_action", profile="endpoint")
    def action_method(self):
        return "action_result"
    @property
    def problematic_property(self):
        """Property that raises error if accessed during discovery."""
        raise RuntimeError("Property accessed!")
    def regular_method(self):
        return "not_an_action"
@pytest.fixture
def agent():
    """Create a basic agent instance."""
    # Patching registry to ensure we test fallback/native logic primarily here
    with patch("exonware.xwapi.client.xwclient.api_agent_engine_registry", None):
        agent = MockAgent(name="test_agent", auto_discover=True)
        return agent
# --- Discovery Tests ---
@pytest.mark.xwapi_unit
def test_auto_discovery_native():
    """Test that actions are discovered using fallback logic."""
    with patch("exonware.xwapi.client.xwclient.api_agent_engine_registry", None):
        agent = MockAgent(name="discovery_agent", auto_discover=True)
        actions = agent.get_actions()
        # Expect 2 actions: action_method (MockAgent) and revive_auths (XWApiAgent)
        assert len(actions) == 2
        action_names = [a.__name__ for a in actions]
        assert "action_method" in action_names
        assert "revive_auths" in action_names
@pytest.mark.xwapi_unit
def test_discovery_ignores_properties():
    """Test that discovery doesn't trigger properties."""
    with patch("exonware.xwapi.client.xwclient.api_agent_engine_registry", None):
        # This should not raise RuntimeError from problematic_property
        agent = MockAgent(name="safe_agent", auto_discover=True)
        assert len(agent.get_actions()) == 2
@pytest.mark.xwapi_unit
def test_manual_action_management(agent):
    """Test adding and removing actions manually."""
    @XWAction(operationId="manual_add")
    def new_func(): pass
    initial_count = len(agent.get_actions())
    assert initial_count == 2
    # Add
    agent.add_action(new_func)
    assert len(agent.get_actions()) == initial_count + 1
    # Remove
    agent.remove_action(new_func)
    assert len(agent.get_actions()) == initial_count
    # Clear
    agent.clear_actions()
    assert len(agent.get_actions()) == 0
# --- HTTP Helper Tests ---
@pytest.mark.xwapi_unit
def test_request_headers_generate(agent):
    """Test HTTP header generation."""
    url = "https://api.example.com/v1/resource?q=1"
    headers = agent.request_headers_generate(
        url, 
        method="POST", 
        authorization="Bearer token",
        cookie="session=123",
        custom_header="value"
    )
    assert headers["authorization"] == "Bearer token"
    assert headers["cookie"] == "session=123"
    assert headers["custom_header"] == "value"
    assert headers["content-type"] == "application/json"
    # Ensure no HTTP/2 pseudo-headers
    assert ":method" not in headers
    assert ":authority" not in headers
@pytest.mark.xwapi_unit
def test_validate_session_valid(agent):
    """Test session validation with valid session."""
    session = requests.Session()
    assert agent._validate_session(session) is session
@pytest.mark.xwapi_unit
def test_validate_session_invalid(agent):
    """Test session validation with invalid session."""
    assert agent._validate_session("not_a_session") is None
    assert agent._validate_session(None) is None
# Mock class to replace requests.Session for isinstance checks
class MockSession:
    def __init__(self):
        self.get = MagicMock()
        self.post = MagicMock()
@pytest.mark.xwapi_unit
@patch("requests.Session", MockSession)
def test_request_get(agent):
    """Test GET request wrapper."""
    mock_session = MockSession()
    mock_response = MagicMock()
    mock_session.get.return_value = mock_response
    url = "https://example.com"
    response = agent.request_get(mock_session, url, params={"q": "test"})
    assert response == mock_response
    mock_session.get.assert_called_once()
    call_args = mock_session.get.call_args
    assert call_args[0][0] == url
    assert "headers" in call_args[1]
    assert call_args[1]["params"] == {"q": "test"}
@pytest.mark.xwapi_unit
@patch("requests.Session", MockSession)
def test_request_post_json(agent):
    """Test POST request wrapper with JSON."""
    mock_session = MockSession()
    url = "https://example.com"
    payload = {"key": "value"}
    agent.request_post(mock_session, url, payload=payload)
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    assert call_args[1]["json"] == payload
@pytest.mark.xwapi_unit
@patch("requests.Session", MockSession)
def test_request_post_data(agent):
    """Test POST request wrapper with form data."""
    mock_session = MockSession()
    url = "https://example.com"
    payload = "data_string"
    agent.request_post(mock_session, url, payload=payload)
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    assert call_args[1]["data"] == payload
# --- Auth Revival Tests ---
@pytest.mark.xwapi_unit
def test_revive_auths(agent):
    """Test auth revival logic with mocked filesystem."""
    mock_config = {"client_id": "123"}
    with patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.is_dir", return_value=True), \
         patch("pathlib.Path.iterdir") as mock_iterdir, \
         patch("exonware.xwsystem.io.serialization.JsonSerializer.load_file", return_value=mock_config):
        # Setup mock directory structure
        platform_dir = MagicMock()
        platform_dir.name = "google"
        platform_dir.is_dir.return_value = True
        auth_dir = MagicMock()
        auth_dir.name = "service_account"
        auth_dir.is_dir.return_value = True
        # platform_dir contains auth_dir
        platform_dir.iterdir.return_value = [auth_dir]
        # base_dir contains platform_dir
        mock_iterdir.return_value = [platform_dir]
        # Bypass XWAction permission check by calling the wrapped function directly
        # The wrapper adds __wrapped__, so we call it with 'self' (agent)
        if hasattr(agent.revive_auths, "__wrapped__"):
            result = agent.revive_auths.__wrapped__(agent, base_path="/test/path")
        else:
            # Fallback (unlikely if functools.wraps is used, but safe)
            result = agent.revive_auths(base_path="/test/path")
        assert result["success"] is True
        assert result["reloaded_count"] == 1
        assert "google" in result["platforms"]
        assert "service_account" in result["auths"]["google"]
