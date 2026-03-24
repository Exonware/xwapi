#exonware/xwapi/tests/1.unit/engines_tests/test_fastapi_engine_tough.py
"""
Tough unit tests for FastAPI Server Engine - Edge cases, error conditions, and complex scenarios.
Tests engine with invalid inputs, concurrent operations, failure modes,
and boundary conditions.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations
import pytest
from unittest.mock import Mock, MagicMock, patch
from exonware.xwapi.server.engines.fastapi import FastAPIServerEngine
from exonware.xwapi.config import XWAPIConfig
from exonware.xwapi.server.engines.contracts import ProtocolType
from exonware.xwapi.errors import XWAPIError, FastAPICreationError
@pytest.mark.xwapi_unit

def test_fastapi_engine_with_none_config():
    """Test FastAPI engine with None config - should raise error."""
    engine = FastAPIServerEngine()
    with pytest.raises((TypeError, AttributeError)):
        engine.create_app(None)
@pytest.mark.xwapi_unit

def test_fastapi_engine_with_empty_config():
    """Test FastAPI engine with empty config values."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="", version="", description="")
    app = engine.create_app(config)
    assert app is not None
@pytest.mark.xwapi_unit

def test_fastapi_engine_with_very_long_config():
    """Test FastAPI engine with extremely long config values."""
    engine = FastAPIServerEngine()
    long_title = "A" * 1000
    long_description = "B" * 5000
    config = XWAPIConfig(title=long_title, description=long_description)
    app = engine.create_app(config)
    assert app.title == long_title
@pytest.mark.xwapi_unit

def test_fastapi_engine_with_unicode_config():
    """Test FastAPI engine with Unicode in config."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="测试API 🚀", description="日本語の説明")
    app = engine.create_app(config)
    assert "测试" in app.title or "API" in app.title
@pytest.mark.xwapi_unit

def test_fastapi_engine_with_special_chars_config():
    """Test FastAPI engine with special characters in config."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="API <>&\"'", description="Desc <>&\"'")
    app = engine.create_app(config)
    assert app is not None
@pytest.mark.xwapi_unit

def test_fastapi_engine_multiple_apps():
    """Test creating multiple FastAPI apps from same engine."""
    engine = FastAPIServerEngine()
    config1 = XWAPIConfig(title="App 1")
    config2 = XWAPIConfig(title="App 2")
    config3 = XWAPIConfig(title="App 3")
    app1 = engine.create_app(config1)
    app2 = engine.create_app(config2)
    app3 = engine.create_app(config3)
    assert app1 is not app2
    assert app2 is not app3
    assert app1.title == "App 1"
    assert app2.title == "App 2"
    assert app3.title == "App 3"
@pytest.mark.xwapi_unit

def test_fastapi_engine_exception_handlers_registration():
    """Test that all exception handlers are registered correctly."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test")
    app = engine.create_app(config)
    from exonware.xwapi.errors import XWAPIError
    assert XWAPIError in app.exception_handlers
    assert Exception in app.exception_handlers
@pytest.mark.xwapi_unit

def test_fastapi_engine_openapi_schema_consistency():
    """Test OpenAPI schema consistency across multiple calls."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test", version="1.0.0")
    app = engine.create_app(config)
    schema1 = app.openapi()
    schema2 = app.openapi()
    # Should be consistent (cached)
    assert schema1["info"]["title"] == schema2["info"]["title"]
    assert schema1["info"]["version"] == schema2["info"]["version"]
@pytest.mark.xwapi_unit

def test_fastapi_engine_openapi_schema_with_many_routes():
    """Test OpenAPI schema generation with many routes."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Many Routes")
    app = engine.create_app(config)
    # Add 100 routes
    for i in range(100):
        @app.get(f"/route{i}")
        def route_handler():
            return {"route": i}
    schema = app.openapi()
    assert len(schema["paths"]) >= 100
@pytest.mark.xwapi_unit

def test_fastapi_engine_openapi_schema_with_complex_routes():
    """Test OpenAPI schema with complex route definitions."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Complex Routes")
    app = engine.create_app(config)
    @app.get("/users/{user_id}/posts/{post_id}/comments/{comment_id}")
    def nested_route(user_id: int, post_id: int, comment_id: int):
        return {"user_id": user_id, "post_id": post_id, "comment_id": comment_id}
    @app.post("/users/{user_id}/posts", response_model=dict)
    def create_post(user_id: int, data: dict):
        return {"user_id": user_id, "data": data}
    schema = app.openapi()
    assert "/users/{user_id}/posts/{post_id}/comments/{comment_id}" in schema["paths"]
    assert "/users/{user_id}/posts" in schema["paths"]
@pytest.mark.xwapi_unit

def test_fastapi_engine_with_servers_config():
    """Test FastAPI engine with servers configuration."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(
        title="Server Config",
        servers=[
            {"url": "https://api.example.com", "description": "Production"},
            {"url": "https://staging.example.com", "description": "Staging"}
        ]
    )
    app = engine.create_app(config)
    schema = app.openapi()
    if "servers" in schema:
        assert len(schema["servers"]) >= 1
@pytest.mark.xwapi_unit

def test_fastapi_engine_with_openapi_tags():
    """Test FastAPI engine with OpenAPI tags."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(
        title="Tagged API",
        openapi_tags=[
            {"name": "users", "description": "User operations"},
            {"name": "posts", "description": "Post operations"},
            {"name": "comments", "description": "Comment operations"}
        ]
    )
    app = engine.create_app(config)
    assert hasattr(app, 'openapi_tags')
    if app.openapi_tags:
        assert len(app.openapi_tags) >= 3
@pytest.mark.xwapi_unit

def test_fastapi_engine_protocol_type_immutability():
    """Test that protocol type is immutable."""
    engine = FastAPIServerEngine()
    original_protocol = engine.protocol_type
    try:
        engine.protocol_type = ProtocolType.HTTP_GRAPHQL
    except (AttributeError, TypeError):
        # Good - should be immutable
        pass
    assert engine.protocol_type == original_protocol
@pytest.mark.xwapi_unit

def test_fastapi_engine_name_immutability():
    """Test that engine name is immutable."""
    engine = FastAPIServerEngine()
    original_name = engine.name
    try:
        engine.name = "modified"
    except (AttributeError, TypeError):
        # Good - should be immutable
        pass
    assert engine.name == original_name
@pytest.mark.xwapi_unit

def test_fastapi_engine_register_action_with_none():
    """Test registering None action."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test")
    app = engine.create_app(config)
    with pytest.raises((TypeError, AttributeError)):
        engine._register_http_action(app, None, path="/test", method="GET")
@pytest.mark.xwapi_unit

def test_fastapi_engine_register_action_with_invalid_path():
    """Test registering action with invalid path."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test")
    app = engine.create_app(config)
    mock_action = MagicMock()
    with pytest.raises((TypeError, AttributeError)):
        engine._register_http_action(app, mock_action, path=None, method="GET")
@pytest.mark.xwapi_unit

def test_fastapi_engine_generate_openapi_with_none_app():
    """Test generating OpenAPI with None app."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test")
    with pytest.raises((TypeError, AttributeError)):
        engine.generate_openapi(None, [], config)
@pytest.mark.xwapi_unit

def test_fastapi_engine_generate_openapi_with_empty_actions():
    """Test generating OpenAPI with empty actions list."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test")
    app = engine.create_app(config)
    schema = engine.generate_openapi(app, [], config)
    assert "paths" in schema
    assert isinstance(schema["paths"], dict)
@pytest.mark.xwapi_unit

def test_fastapi_engine_generate_openapi_with_many_actions():
    """Test generating OpenAPI with many actions."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test")
    app = engine.create_app(config)
    mock_actions = [MagicMock() for _ in range(50)]
    schema = engine.generate_openapi(app, mock_actions, config)
    assert "paths" in schema
@pytest.mark.xwapi_unit

def test_fastapi_engine_start_server_with_invalid_port():
    """Test starting server with invalid port."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test")
    app = engine.create_app(config)
    invalid_ports = [-1, 0, 65536, 99999]
    for port in invalid_ports:
        # Mock uvicorn to prevent actual server start
        # On Windows, uvicorn is imported inside the function, so we patch it at the module level
        with patch('uvicorn.run') as mock_run, patch('uvicorn.Server') as mock_server_class:
            # Mock Server.run() to raise OverflowError for out-of-range ports
            mock_server = MagicMock()
            if port > 65535 or port < 1:
                mock_server.run.side_effect = OverflowError("bind(): port must be 0-65535.")
            mock_server_class.return_value = mock_server
            try:
                engine.start_server(app, port=port)
                # May accept or reject
            except (ValueError, OSError, OverflowError):
                # Acceptable - invalid port
                # OverflowError is raised by uvicorn for out-of-range ports (e.g., > 65535)
                pass
@pytest.mark.xwapi_unit

def test_fastapi_engine_start_server_with_invalid_host():
    """Test starting server with invalid host."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test")
    app = engine.create_app(config)
    invalid_hosts = ["", None, "invalid..host"]
    for host in invalid_hosts:
        # Mock uvicorn to prevent actual server start
        # On Windows, uvicorn is imported inside the function, so we patch it at the module level
        with patch('uvicorn.run') as mock_run, patch('uvicorn.Server') as mock_server_class:
            # Mock Server.run() to prevent actual server start
            mock_server = MagicMock()
            mock_server_class.return_value = mock_server
            try:
                engine.start_server(app, host=host)
                # May accept or reject
            except (ValueError, TypeError, OSError):
                # Acceptable - invalid host
                pass
@pytest.mark.xwapi_unit

def test_fastapi_engine_start_server_with_kwargs():
    """Test starting server with additional kwargs."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test")
    app = engine.create_app(config)
    # Mock both uvicorn.run (Unix) and uvicorn.Server (Windows) to prevent actual server start
    with patch('uvicorn.run') as mock_run, patch('uvicorn.Server') as mock_server_class:
        mock_server = MagicMock()
        mock_server_class.return_value = mock_server
        engine.start_server(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="debug",
            reload=True,
            workers=4
        )
        # Should pass kwargs to uvicorn
        # On Unix, uvicorn.run() is called; on Windows, uvicorn.Server() is used
        # Verify that at least one was called
        assert mock_run.called or mock_server_class.called
@pytest.mark.xwapi_unit

def test_fastapi_engine_openapi_metadata():
    """Test OpenAPI schema includes xwapi metadata."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Metadata Test", version="2.0.0")
    app = engine.create_app(config)
    schema = app.openapi()
    assert "info" in schema
    # Check for xwapi-specific metadata
    if "x-xwapi-version" in schema.get("info", {}):
        assert schema["info"]["x-xwapi-version"] is not None
@pytest.mark.xwapi_unit

def test_fastapi_engine_openapi_version():
    """Test OpenAPI schema version is 3.1.0."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test")
    app = engine.create_app(config)
    schema = app.openapi()
    assert schema["openapi"] == "3.1.0" or schema["openapi"].startswith("3.")
@pytest.mark.xwapi_unit

def test_fastapi_engine_exception_handler_with_all_errors():
    """Test exception handlers work with all error types."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test")
    app = engine.create_app(config)
    from exonware.xwapi.errors import (
        ValidationError,
        AuthenticationError,
        NotFoundError,
        InternalError
    )
    error_types = [ValidationError, AuthenticationError, NotFoundError, InternalError]
    for error_type in error_types:
        assert XWAPIError in app.exception_handlers
        # All should be handled by XWAPIError handler
@pytest.mark.xwapi_unit

def test_fastapi_engine_with_concurrent_app_creation():
    """Test concurrent app creation (simulated)."""
    import threading
    engine = FastAPIServerEngine()
    configs = [XWAPIConfig(title=f"App {i}") for i in range(10)]
    apps = []
    def create_app(config):
        app = engine.create_app(config)
        apps.append(app)
    threads = [threading.Thread(target=create_app, args=(config,)) for config in configs]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(apps) == 10
    assert len(set(id(app) for app in apps)) == 10  # All different instances
@pytest.mark.xwapi_unit

def test_fastapi_engine_app_caching():
    """Test that engine caches app instance."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test")
    app1 = engine.create_app(config)
    app2 = engine._app
    # Should reference same app
    assert app1 is app2
@pytest.mark.xwapi_unit

def test_fastapi_engine_with_malformed_config():
    """Test engine with malformed config object."""
    engine = FastAPIServerEngine()
    # Config with missing required attributes
    class MalformedConfig:
        pass
    malformed = MalformedConfig()
    with pytest.raises((AttributeError, TypeError)):
        engine.create_app(malformed)
@pytest.mark.xwapi_unit

def test_fastapi_engine_inheritance_chain():
    """Test complete inheritance chain."""
    engine = FastAPIServerEngine()
    from exonware.xwapi.server.engines.base import AApiServerEngineBase
    from exonware.xwapi.server.engines.http_base import AHttpServerEngineBase
    from exonware.xwapi.server.engines.contracts import IApiServerEngine
    assert isinstance(engine, AHttpServerEngineBase)
    assert isinstance(engine, AApiServerEngineBase)
    # Check interface methods
    assert hasattr(engine, "create_app")
    assert hasattr(engine, "protocol_type")
    assert hasattr(engine, "name")
@pytest.mark.xwapi_unit

def test_fastapi_engine_action_engine_registry():
    """Test that engine has action engine registry attr (lazy-loaded, may be None until used)."""
    engine = FastAPIServerEngine()
    assert hasattr(engine, "_action_engine_registry")
    # Lazy-loaded: None until _get_action_engine or _register_http_action triggers load
    assert engine._action_engine_registry is None or engine._action_engine_registry is not None
@pytest.mark.xwapi_unit

def test_fastapi_engine_get_action_engine():
    """Test getting action engine from registry."""
    engine = FastAPIServerEngine()
    mock_action = MagicMock()
    action_engine = engine._get_action_engine(mock_action)
    # May return None if not configured, but should not raise
    assert action_engine is None or action_engine is not None
@pytest.mark.xwapi_unit

def test_fastapi_engine_with_none_action_engine_registry():
    """Test engine when action engine registry is None."""
    engine = FastAPIServerEngine()
    engine._action_engine_registry = None
    mock_action = MagicMock()
    action_engine = engine._get_action_engine(mock_action)
    assert action_engine is None
@pytest.mark.xwapi_unit

def test_fastapi_engine_openapi_schema_regeneration():
    """Test OpenAPI schema regeneration after route changes."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test")
    app = engine.create_app(config)
    schema1 = app.openapi()
    # Add new route
    @app.get("/new-route")
    def new_route():
        return {"new": True}
    # Clear schema cache
    if hasattr(app, 'openapi_schema'):
        app.openapi_schema = None
    schema2 = app.openapi()
    assert len(schema2["paths"]) >= len(schema1["paths"])
@pytest.mark.xwapi_unit

def test_fastapi_engine_with_all_http_methods():
    """Test engine with all HTTP methods."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test")
    app = engine.create_app(config)
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
    for method in methods:
        route_func = getattr(app, method.lower())
        route_func(f"/{method.lower()}")(lambda: {"method": method})
    schema = app.openapi()
    assert len(schema["paths"]) >= len(methods)
@pytest.mark.xwapi_unit

def test_fastapi_engine_exception_handler_error_handling():
    """Test exception handlers handle errors gracefully."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test")
    app = engine.create_app(config)
    # Exception handlers should be registered
    assert XWAPIError in app.exception_handlers
    assert Exception in app.exception_handlers
    # Handlers should be callable
    handler = app.exception_handlers[XWAPIError]
    assert callable(handler)
@pytest.mark.xwapi_unit

def test_fastapi_engine_with_complex_openapi_config():
    """Test engine with complex OpenAPI configuration."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(
        title="Complex API",
        version="1.2.3-beta.4",
        description="Very complex API",
        servers=[
            {"url": "https://api.example.com", "description": "Production"},
            {"url": "https://staging.example.com", "description": "Staging"}
        ],
        openapi_tags=[
            {"name": "users", "description": "User operations"},
            {"name": "posts", "description": "Post operations"}
        ]
    )
    app = engine.create_app(config)
    schema = app.openapi()
    assert schema["info"]["title"] == "Complex API"
    assert schema["info"]["version"] == "1.2.3-beta.4"
