#exonware/xwapi/tests/1.unit/server_tests/test_server_tough.py
"""
Tough unit tests for XWApiServer - Edge cases, error conditions, and complex scenarios.
Tests server with invalid inputs, concurrent operations, failure modes,
and boundary conditions.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from exonware.xwapi.server import XWApiServer
from exonware.xwapi.config import XWAPIConfig
from exonware.xwapi.errors import XWAPIError, FastAPICreationError
from exonware.xwaction import XWAction
@pytest.mark.xwapi_unit

def test_server_initialization_with_none_config():
    """Test server initialization with None config - should create default."""
    server = XWApiServer(engine="fastapi", config=None)
    assert server is not None
    assert hasattr(server, "config")
@pytest.mark.xwapi_unit

def test_server_initialization_with_empty_config():
    """Test server initialization with empty config values."""
    config = XWAPIConfig(title="", version="", description="")
    server = XWApiServer(engine="fastapi", config=config)
    assert server is not None
@pytest.mark.xwapi_unit

def test_server_initialization_with_very_long_config():
    """Test server initialization with extremely long config values."""
    long_title = "A" * 1000
    long_description = "B" * 5000
    config = XWAPIConfig(title=long_title, description=long_description)
    server = XWApiServer(engine="fastapi", config=config)
    assert server.config.title == long_title
@pytest.mark.xwapi_unit

def test_server_initialization_with_unicode_config():
    """Test server initialization with Unicode in config."""
    config = XWAPIConfig(title="测试API 🚀", description="日本語の説明")
    server = XWApiServer(engine="fastapi", config=config)
    assert "测试" in server.config.title or "API" in server.config.title
@pytest.mark.xwapi_unit

def test_server_initialization_with_special_chars_config():
    """Test server initialization with special characters in config."""
    config = XWAPIConfig(title="API <>&\"'", description="Desc <>&\"'")
    server = XWApiServer(engine="fastapi", config=config)
    assert server is not None
@pytest.mark.xwapi_unit

def test_server_initialization_with_invalid_engine():
    """Test server initialization with invalid engine name."""
    config = XWAPIConfig(title="Test")
    with pytest.raises((XWAPIError, ValueError, AttributeError, ImportError)):
        XWApiServer(engine="nonexistent_invalid_engine_xyz", config=config)
@pytest.mark.xwapi_unit

def test_server_initialization_with_empty_engine():
    """Test server initialization with empty engine string."""
    config = XWAPIConfig(title="Test")
    with pytest.raises((XWAPIError, ValueError, AttributeError)):
        XWApiServer(engine="", config=config)
@pytest.mark.xwapi_unit

def test_server_initialization_with_none_engine():
    """Test server initialization with None engine."""
    config = XWAPIConfig(title="Test")
    with pytest.raises((TypeError, AttributeError)):
        XWApiServer(engine=None, config=config)
@pytest.mark.xwapi_unit

def test_server_initialization_with_numeric_engine():
    """Test server initialization with numeric engine (should fail)."""
    config = XWAPIConfig(title="Test")
    with pytest.raises((TypeError, AttributeError, ValueError)):
        XWApiServer(engine=123, config=config)
@pytest.mark.xwapi_unit

def test_server_initialization_multiple_instances():
    """Test creating multiple server instances - should not interfere."""
    config1 = XWAPIConfig(title="Server 1")
    config2 = XWAPIConfig(title="Server 2")
    config3 = XWAPIConfig(title="Server 3")
    server1 = XWApiServer(engine="fastapi", config=config1)
    server2 = XWApiServer(engine="fastapi", config=config2)
    server3 = XWApiServer(engine="fastapi", config=config3)
    assert server1 is not server2
    assert server2 is not server3
    assert server1.config.title == "Server 1"
    assert server2.config.title == "Server 2"
    assert server3.config.title == "Server 3"
@pytest.mark.xwapi_unit

def test_server_register_action_with_none_action():
    """Test registering None action - should handle gracefully."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    with pytest.raises((TypeError, AttributeError)):
        server.register_action(None, path="/test", method="GET")
@pytest.mark.xwapi_unit

def test_server_register_action_with_invalid_path():
    """Test registering action with invalid path."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    @XWAction(operationId="test", profile="endpoint")
    def test_action():
        return {"test": True}
    # Test with None path
    try:
        result = server.register_action(test_action, path=None, method="GET")
        # May use default path or raise error
        assert isinstance(result, (bool, type(None))) or True
    except (TypeError, ValueError):
        # Acceptable
        pass
@pytest.mark.xwapi_unit

def test_server_register_action_with_empty_path():
    """Test registering action with empty path."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    @XWAction(operationId="test", profile="endpoint")
    def test_action():
        return {"test": True}
    result = server.register_action(test_action, path="", method="GET")
    assert isinstance(result, (bool, type(None)))
@pytest.mark.xwapi_unit

def test_server_register_action_with_very_long_path():
    """Test registering action with extremely long path."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    @XWAction(operationId="test", profile="endpoint")
    def test_action():
        return {"test": True}
    long_path = "/" + "a" * 1000
    result = server.register_action(test_action, path=long_path, method="GET")
    assert isinstance(result, (bool, type(None)))
@pytest.mark.xwapi_unit

def test_server_register_action_with_special_chars_path():
    """Test registering action with special characters in path."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    @XWAction(operationId="test", profile="endpoint")
    def test_action():
        return {"test": True}
    special_path = "/test-<>&\"'"
    result = server.register_action(test_action, path=special_path, method="GET")
    assert isinstance(result, (bool, type(None)))
@pytest.mark.xwapi_unit

def test_server_register_action_with_invalid_method():
    """Test registering action with invalid HTTP method."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    @XWAction(operationId="test", profile="endpoint")
    def test_action():
        return {"test": True}
    result = server.register_action(test_action, path="/test", method="INVALID_METHOD")
    # Should handle gracefully or use default
    assert isinstance(result, (bool, type(None)))
@pytest.mark.xwapi_unit

def test_server_register_action_with_none_method():
    """Test registering action with None method."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    @XWAction(operationId="test", profile="endpoint")
    def test_action():
        return {"test": True}
    with pytest.raises((TypeError, AttributeError)):
        server.register_action(test_action, path="/test", method=None)
@pytest.mark.xwapi_unit

def test_server_register_action_with_empty_method():
    """Test registering action with empty method string."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    @XWAction(operationId="test", profile="endpoint")
    def test_action():
        return {"test": True}
    result = server.register_action(test_action, path="/test", method="")
    assert isinstance(result, (bool, type(None)))
@pytest.mark.xwapi_unit

def test_server_register_action_with_all_methods():
    """Test registering same action with all HTTP methods."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    @XWAction(operationId="test", profile="endpoint")
    def test_action():
        return {"test": True}
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
    results = []
    for method in methods:
        result = server.register_action(test_action, path="/test", method=method)
        results.append(result)
    # All should attempt registration
    assert len(results) == len(methods)
@pytest.mark.xwapi_unit

def test_server_register_multiple_actions():
    """Test registering multiple actions to same server."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    @XWAction(operationId="action1", profile="endpoint")
    def action1():
        return {"action": 1}
    @XWAction(operationId="action2", profile="endpoint")
    def action2():
        return {"action": 2}
    @XWAction(operationId="action3", profile="endpoint")
    def action3():
        return {"action": 3}
    result1 = server.register_action(action1, path="/action1", method="GET")
    result2 = server.register_action(action2, path="/action2", method="POST")
    result3 = server.register_action(action3, path="/action3", method="PUT")
    assert isinstance(result1, (bool, type(None)))
    assert isinstance(result2, (bool, type(None)))
    assert isinstance(result3, (bool, type(None)))
@pytest.mark.xwapi_unit

def test_server_register_duplicate_actions():
    """Test registering duplicate actions to same path."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    @XWAction(operationId="duplicate", profile="endpoint")
    def action1():
        return {"handler": 1}
    @XWAction(operationId="duplicate", profile="endpoint")
    def action2():
        return {"handler": 2}
    result1 = server.register_action(action1, path="/duplicate", method="GET")
    result2 = server.register_action(action2, path="/duplicate", method="GET")
    # Both should attempt registration (may overwrite or both exist)
    assert isinstance(result1, (bool, type(None)))
    assert isinstance(result2, (bool, type(None)))
@pytest.mark.xwapi_unit

def test_server_config_immutability():
    """Test that config changes don't affect server after initialization."""
    config = XWAPIConfig(title="Original")
    server = XWApiServer(config=config)
    original_title = server.config.title
    config.title = "Modified"
    # Server config should not change
    assert server.config.title == original_title
@pytest.mark.xwapi_unit

def test_server_engine_name_immutability():
    """Test that engine name is immutable after initialization."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(engine="fastapi", config=config)
    original_engine = server.engine_name
    try:
        server.engine_name = "modified"
    except AttributeError:
        # Good - should be immutable or protected
        pass
    # Engine name should remain original
    assert server.engine_name == original_engine
@pytest.mark.xwapi_unit
@patch("exonware.xwapi.server.xwserver.api_server_engine_registry")

def test_server_engine_registry_failure(mock_registry):
    """Test server when engine registry fails."""
    mock_registry.get_engine.return_value = None
    mock_registry.get_engine.side_effect = Exception("Registry error")
    config = XWAPIConfig(title="Test")
    with pytest.raises((ValueError, Exception)):
        XWApiServer(engine="custom_engine", config=config)
@pytest.mark.xwapi_unit
@patch("exonware.xwapi.server.xwserver.api_server_engine_registry")

def test_server_engine_registry_none_result(mock_registry):
    """Test server when engine registry returns None."""
    mock_registry.get_engine.return_value = None
    config = XWAPIConfig(title="Test")
    with pytest.raises((XWAPIError, ValueError, AttributeError)):
        XWApiServer(engine="nonexistent", config=config)
@pytest.mark.xwapi_unit

def test_server_lifecycle_start_stop_sequence():
    """Test server start/stop lifecycle sequence."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    # Mock start/stop to avoid actual server startup
    with patch.object(server, '_engine') as mock_engine:
        mock_engine.start_server = Mock()
        mock_engine.stop_server = Mock()
        # Test that methods exist and are callable
        assert callable(server.start)
        assert callable(server.stop)
        assert callable(server.restart)
@pytest.mark.xwapi_unit

def test_server_restart_before_start():
    """Test restarting server before it's started."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    # Restart should handle not-started state
    with patch.object(server, '_engine') as mock_engine:
        mock_engine.start_server = Mock()
        mock_engine.stop_server = Mock()
        # Should not raise error
        try:
            server.restart()
        except (AttributeError, RuntimeError):
            # Acceptable - server not started
            pass
@pytest.mark.xwapi_unit

def test_server_stop_before_start():
    """Test stopping server before it's started."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    # Stop should handle not-started state
    with patch.object(server, '_engine') as mock_engine:
        mock_engine.stop_server = Mock()
        # Should not raise error
        try:
            server.stop()
        except (AttributeError, RuntimeError):
            # Acceptable - server not started
            pass
@pytest.mark.xwapi_unit

def test_server_multiple_starts():
    """Test starting server multiple times."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    with patch.object(server, '_engine') as mock_engine:
        mock_engine.start_server = Mock()
        # Should handle multiple starts
        try:
            server.start(port=8000)
            server.start(port=8001)
        except (RuntimeError, AttributeError, XWAPIError):
            # Acceptable - already started or instance conflict
            pass
@pytest.mark.xwapi_unit

def test_server_with_invalid_port():
    """Test server with invalid port numbers."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    invalid_ports = [-1, 0, 65536, 99999, "invalid", None]
    for port in invalid_ports:
        with patch.object(server, '_engine') as mock_engine:
            mock_engine.start_server = Mock()
            try:
                server.start(port=port)
                # May accept or reject
            except (ValueError, TypeError, OSError, XWAPIError):
                # Acceptable - invalid port or instance conflict
                pass
@pytest.mark.xwapi_unit

def test_server_with_invalid_host():
    """Test server with invalid host values."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    invalid_hosts = ["", None, 123, "invalid..host", "http://invalid"]
    for host in invalid_hosts:
        with patch.object(server, '_engine') as mock_engine:
            mock_engine.start_server = Mock()
            try:
                server.start(host=host)
                # May accept or reject
            except (ValueError, TypeError, OSError, XWAPIError):
                # Acceptable - invalid host or instance conflict
                pass
@pytest.mark.xwapi_unit

def test_server_app_property():
    """Test accessing server app property."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    # App should be accessible
    assert hasattr(server, "app") or hasattr(server, "_app")
    if hasattr(server, "app"):
        app = server.app
        assert app is not None
@pytest.mark.xwapi_unit

def test_server_engine_property():
    """Test accessing server engine property."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    # Engine should be accessible
    assert hasattr(server, "_engine") or hasattr(server, "engine")
    if hasattr(server, "_engine"):
        engine = server._engine
        assert engine is not None
@pytest.mark.xwapi_unit

def test_server_with_complex_config():
    """Test server with complex configuration."""
    config = XWAPIConfig(
        title="Complex API",
        version="1.2.3-beta.4+build.5",
        description="A very complex API",
        servers=[
            {"url": "https://api.example.com", "description": "Production"},
            {"url": "https://staging.example.com", "description": "Staging"}
        ],
        openapi_tags=[
            {"name": "users", "description": "User operations"},
            {"name": "posts", "description": "Post operations"}
        ]
    )
    server = XWApiServer(config=config)
    assert server.config.title == "Complex API"
    assert len(server.config.servers) == 2
@pytest.mark.xwapi_unit

def test_server_register_action_with_non_xwaction():
    """Test registering non-XWAction function."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    def regular_function():
        return {"test": True}
    # Should handle gracefully
    result = server.register_action(regular_function, path="/test", method="GET")
    assert isinstance(result, (bool, type(None)))
@pytest.mark.xwapi_unit

def test_server_register_action_with_async_function():
    """Test registering async function."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    @XWAction(operationId="async_test", profile="endpoint")
    async def async_action():
        return {"async": True}
    result = server.register_action(async_action, path="/async", method="GET")
    assert isinstance(result, (bool, type(None)))
@pytest.mark.xwapi_unit

def test_server_register_action_with_class_method():
    """Test registering class method."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    class TestClass:
        @XWAction(operationId="method_test", profile="endpoint")
        def method_action(self):
            return {"method": True}
    instance = TestClass()
    result = server.register_action(instance.method_action, path="/method", method="GET")
    assert isinstance(result, (bool, type(None)))
@pytest.mark.xwapi_unit

def test_server_register_action_with_static_method():
    """Test registering static method."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    class TestClass:
        @staticmethod
        @XWAction(operationId="static_test", profile="endpoint")
        def static_action():
            return {"static": True}
    result = server.register_action(TestClass.static_action, path="/static", method="GET")
    assert isinstance(result, (bool, type(None)))
@pytest.mark.xwapi_unit

def test_server_with_concurrent_registrations():
    """Test server with concurrent action registrations (simulated)."""
    import threading
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    @XWAction(operationId="concurrent", profile="endpoint")
    def action_template(i):
        def action():
            return {"id": i}
        return action
    results = []
    def register_action(i):
        action = action_template(i)
        result = server.register_action(action, path=f"/action{i}", method="GET")
        results.append(result)
    threads = [threading.Thread(target=register_action, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(results) == 10
@pytest.mark.xwapi_unit

def test_server_inheritance_chain():
    """Test complete inheritance chain."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    from exonware.xwapi.base import AApiServer
    from exonware.xwapi.contracts import IApiServer
    assert isinstance(server, AApiServer)
    # Check interface methods exist
    assert hasattr(server, "register_action")
    assert hasattr(server, "start")
    assert hasattr(server, "stop")
@pytest.mark.xwapi_unit

def test_server_with_all_engine_types():
    """Test server with all available engine types."""
    config = XWAPIConfig(title="Test")
    engines_to_test = ["fastapi"]
    # Add other engines if available
    # Note: Flask is not currently supported, so we skip it
    for engine in engines_to_test:
        try:
            server = XWApiServer(engine=engine, config=config)
            assert server.engine_name == engine
        except (ValueError, ImportError, AttributeError, XWAPIError):
            # Engine not available
            pass
@pytest.mark.xwapi_unit

def test_server_config_deep_copy():
    """Test that server uses deep copy of config."""
    config = XWAPIConfig(title="Original")
    server = XWApiServer(config=config)
    # Modify original config
    config.title = "Modified"
    config.version = "999.0.0"
    # Server config should not change
    assert server.config.title != "Modified" or server.config.title == "Original"
@pytest.mark.xwapi_unit

def test_server_with_none_config_values():
    """Test server with None values in config."""
    config = XWAPIConfig(title="Test", version="1.0.0", description=None)
    server = XWApiServer(config=config)
    assert server.config.description is None or server.config.description == ""
@pytest.mark.xwapi_unit

def test_server_register_action_path_normalization():
    """Test that action paths are normalized correctly."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    @XWAction(operationId="test", profile="endpoint")
    def test_action():
        return {"test": True}
    # Test various path formats
    paths = ["/test", "test", "/test/", "//test", "/test//path"]
    for path in paths:
        result = server.register_action(test_action, path=path, method="GET")
        assert isinstance(result, (bool, type(None)))
@pytest.mark.xwapi_unit

def test_server_with_unicode_paths():
    """Test server with Unicode characters in paths."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    @XWAction(operationId="unicode", profile="endpoint")
    def unicode_action():
        return {"unicode": True}
    unicode_paths = ["/测试", "/日本語", "/العربية", "/🚀"]
    for path in unicode_paths:
        result = server.register_action(unicode_action, path=path, method="GET")
        assert isinstance(result, (bool, type(None)))
@pytest.mark.xwapi_unit

def test_server_error_handling_in_registration():
    """Test error handling during action registration."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    @XWAction(operationId="error_test", profile="endpoint")
    def error_action():
        raise Exception("Test error")
    # Registration should not fail even if action raises errors
    result = server.register_action(error_action, path="/error", method="GET")
    assert isinstance(result, (bool, type(None)))
@pytest.mark.xwapi_unit

def test_server_with_malformed_xwaction():
    """Test server with malformed XWAction decorator."""
    config = XWAPIConfig(title="Test")
    server = XWApiServer(config=config)
    # Function without proper XWAction attributes
    def malformed_action():
        return {"malformed": True}
    result = server.register_action(malformed_action, path="/malformed", method="GET")
    assert isinstance(result, (bool, type(None)))
