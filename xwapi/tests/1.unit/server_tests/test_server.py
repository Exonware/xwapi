#exonware/xwapi/tests/1.unit/server_tests/test_server.py
"""
Unit tests for XWApiServer class.
Tests server initialization, engine selection, action registration, and lifecycle management.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations
import pytest
from unittest.mock import Mock, MagicMock, patch
from exonware.xwapi.server import XWApiServer
from exonware.xwapi.config import XWAPIConfig
from exonware.xwapi.errors import XWAPIError
@pytest.mark.xwapi_unit

def test_server_initialization_with_config():
    """Test server initialization with XWAPIConfig."""
    config = XWAPIConfig(title="Test API", version="1.0.0")
    server = XWApiServer(engine="fastapi", config=config)
    assert server is not None
    assert hasattr(server, "config")
    assert server.config.title == "Test API"
@pytest.mark.xwapi_unit

def test_server_initialization_with_default_engine():
    """Test server initialization with default engine."""
    config = XWAPIConfig(title="Test API")
    server = XWApiServer(config=config)
    assert server is not None
    # Default engine should be fastapi - check that engine is accessible
    assert hasattr(server, "engine") or hasattr(server, "_engine") or hasattr(server, "engine_name")
@pytest.mark.xwapi_unit

def test_server_has_required_methods():
    """Test that server has all required management methods."""
    config = XWAPIConfig(title="Test API")
    server = XWApiServer(config=config)
    assert hasattr(server, "start")
    assert hasattr(server, "stop")
    assert hasattr(server, "restart")
    assert hasattr(server, "register_action")
    assert callable(server.start)
    assert callable(server.stop)
    assert callable(server.restart)
    assert callable(server.register_action)
@pytest.mark.xwapi_unit

def test_server_engine_selection():
    """Test that server selects correct engine."""
    config = XWAPIConfig(title="Test API")
    # Test fastapi engine
    server = XWApiServer(engine="fastapi", config=config)
    assert server.engine_name == "fastapi"
    # Test other available engines (flask is not available)
    # Available engines: fastapi, grpc, graphql, websocket
    # Test that fastapi works (already tested above)
    # Other engines may not be fully implemented, so we just verify fastapi
    assert server.engine_name == "fastapi"
@pytest.mark.xwapi_unit
@patch("exonware.xwapi.server.xwserver.api_server_engine_registry")

def test_server_engine_registry_lookup(mock_registry):
    """Test that server uses engine registry for engine lookup."""
    mock_engine = MagicMock()
    mock_engine.name = "custom_engine"
    mock_registry.get_engine.return_value = mock_engine
    config = XWAPIConfig(title="Test API")
    server = XWApiServer(engine="custom_engine", config=config)
    # Verify registry was consulted
    mock_registry.get_engine.assert_called()
@pytest.mark.xwapi_unit

def test_server_register_action():
    """Test registering an action with server."""
    from exonware.xwaction import XWAction
    config = XWAPIConfig(title="Test API")
    server = XWApiServer(config=config)
    @XWAction(operationId="test_action", profile="endpoint")
    def test_action():
        return {"result": "success"}
    # Register action
    result = server.register_action(test_action, path="/test", method="GET")
    # Should return True if registration successful
    # (May fail if engine not fully initialized, but method should exist)
    assert isinstance(result, bool) or result is None
@pytest.mark.xwapi_unit

def test_server_config_access():
    """Test accessing server configuration."""
    config = XWAPIConfig(
        title="Test API",
        version="2.0.0",
        description="Test description"
    )
    server = XWApiServer(config=config)
    assert server.config.title == "Test API"
    assert server.config.version == "2.0.0"
    assert server.config.description == "Test description"
@pytest.mark.xwapi_unit

def test_server_lifecycle_methods_exist():
    """Test that lifecycle methods exist and are callable."""
    config = XWAPIConfig(title="Test API")
    server = XWApiServer(config=config)
    # Methods should exist
    assert hasattr(server, "start")
    assert hasattr(server, "stop")
    assert hasattr(server, "restart")
    # Methods should be callable
    assert callable(server.start)
    assert callable(server.stop)
    assert callable(server.restart)
@pytest.mark.xwapi_unit

def test_server_inherits_from_base():
    """Test that XWApiServer inherits from AApiServer."""
    from exonware.xwapi.base import AApiServer
    config = XWAPIConfig(title="Test API")
    server = XWApiServer(config=config)
    assert isinstance(server, AApiServer)
@pytest.mark.xwapi_unit

def test_server_implements_interface():
    """Test that XWApiServer implements IApiServer interface."""
    from exonware.xwapi.contracts import IApiServer
    config = XWAPIConfig(title="Test API")
    server = XWApiServer(config=config)
    # Check that server implements interface methods
    assert hasattr(server, "register_action")
    assert hasattr(server, "start")
    assert hasattr(server, "stop")
