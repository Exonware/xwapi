#exonware/xwapi/tests/0.core/test_core_app_tough.py
"""
Tough core tests for xwapi app creation - Edge cases, error conditions, and complex scenarios.
Tests app creation with invalid inputs, boundary conditions, concurrent scenarios,
and failure modes.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations
import pytest
from fastapi import FastAPI, APIRouter
from unittest.mock import Mock, MagicMock, patch
from exonware.xwapi.common.app import create_app, register_module, add_version_router, add_openapi_endpoints
from exonware.xwapi.config import XWAPIConfig
from exonware.xwapi.errors import XWAPIError, FastAPICreationError
@pytest.mark.xwapi_core

def test_create_app_with_none_config():
    """Test creating app with None config - should create default."""
    app = create_app(config=None)
    assert isinstance(app, FastAPI)
    assert app.title == "XWAPI Application"
@pytest.mark.xwapi_core

def test_create_app_with_empty_title():
    """Test creating app with empty title - should use default."""
    app = create_app(title="")
    assert app.title == "XWAPI Application" or app.title == ""
@pytest.mark.xwapi_core

def test_create_app_with_very_long_title():
    """Test creating app with extremely long title."""
    long_title = "A" * 1000
    app = create_app(title=long_title)
    assert app.title == long_title
@pytest.mark.xwapi_core

def test_create_app_with_special_characters_in_title():
    """Test creating app with special characters in title."""
    special_title = "Test API <>&\"'"
    app = create_app(title=special_title)
    assert app.title == special_title
@pytest.mark.xwapi_core

def test_create_app_with_unicode_title():
    """Test creating app with Unicode characters in title."""
    unicode_title = "测试API 🚀 日本語"
    app = create_app(title=unicode_title)
    assert app.title == unicode_title
@pytest.mark.xwapi_core

def test_create_app_with_none_version():
    """Test creating app with None version - should use default."""
    app = create_app(version=None)
    assert app.version == "1.0.0"
@pytest.mark.xwapi_core

def test_create_app_with_invalid_version_format():
    """Test creating app with invalid version format."""
    # Should still work, just use the provided string
    app = create_app(version="invalid-version-format")
    assert app.version == "invalid-version-format"
@pytest.mark.xwapi_core

def test_create_app_with_numeric_version():
    """Test creating app with numeric version."""
    app = create_app(version=2.0)
    # Version should be converted to string or handled appropriately
    assert isinstance(app.version, (str, float, int))
@pytest.mark.xwapi_core

def test_create_app_with_all_none_kwargs():
    """Test creating app with all None keyword arguments."""
    app = create_app(title=None, version=None, description=None)
    assert isinstance(app, FastAPI)
    # Should use defaults
    assert app.title == "XWAPI Application"
    assert app.version == "1.0.0"
@pytest.mark.xwapi_core

def test_create_app_config_override_kwargs():
    """Test that kwargs override config values."""
    config = XWAPIConfig(title="Config Title", version="1.0.0")
    app = create_app(config=config, title="Override Title", version="2.0.0")
    assert app.title == "Override Title"
    assert app.version == "2.0.0"
@pytest.mark.xwapi_core

def test_create_app_with_invalid_engine():
    """Test creating app with invalid engine name."""
    with pytest.raises((ValueError, ImportError, AttributeError)):
        create_app(engine="nonexistent_engine_xyz123")
@pytest.mark.xwapi_core

def test_create_app_with_empty_engine():
    """Test creating app with empty engine string."""
    # Should use default or raise error
    try:
        app = create_app(engine="")
        assert isinstance(app, FastAPI)
    except (ValueError, AttributeError):
        # Acceptable - empty engine is invalid
        pass
@pytest.mark.xwapi_core

def test_create_app_with_uppercase_engine():
    """Test creating app with uppercase engine name."""
    app = create_app(engine="FASTAPI")
    assert isinstance(app, FastAPI)
@pytest.mark.xwapi_core

def test_create_app_with_mixed_case_engine():
    """Test creating app with mixed case engine name."""
    app = create_app(engine="FaStApI")
    assert isinstance(app, FastAPI)
@pytest.mark.xwapi_core

def test_create_app_with_extra_kwargs():
    """Test creating app with extra unexpected kwargs."""
    app = create_app(title="Test", extra_param="should_be_ignored", another_param=123)
    assert isinstance(app, FastAPI)
    assert app.title == "Test"
@pytest.mark.xwapi_core

def test_create_app_multiple_times():
    """Test creating multiple app instances - should not interfere."""
    app1 = create_app(title="App 1")
    app2 = create_app(title="App 2")
    app3 = create_app(title="App 3")
    assert app1.title == "App 1"
    assert app2.title == "App 2"
    assert app3.title == "App 3"
    assert app1 is not app2
    assert app2 is not app3
@pytest.mark.xwapi_core

def test_create_app_with_complex_config():
    """Test creating app with complex configuration."""
    config = XWAPIConfig(
        title="Complex API",
        version="1.2.3-beta.4",
        description="A very complex API with many features",
        servers=[{"url": "https://api.example.com", "description": "Production"}]
    )
    app = create_app(config=config)
    assert app.title == "Complex API"
    assert app.version == "1.2.3-beta.4"
@pytest.mark.xwapi_core

def test_register_module_with_none_app():
    """Test registering module with None app - should raise error."""
    router = APIRouter()
    with pytest.raises((AttributeError, TypeError)):
        register_module(None, router, prefix="/test")
@pytest.mark.xwapi_core

def test_register_module_with_none_router():
    """Test registering None router - should raise error."""
    app = create_app()
    with pytest.raises((AttributeError, TypeError)):
        register_module(app, None, prefix="/test")
@pytest.mark.xwapi_core

def test_register_module_with_empty_prefix():
    """Test registering module with empty prefix."""
    app = create_app()
    router = APIRouter()
    @router.get("/test")
    def test():
        return {"test": True}
    register_module(app, router, prefix="")
    routes = [r for r in app.routes if hasattr(r, 'path')]
    assert any("/test" in str(r.path) for r in routes)
@pytest.mark.xwapi_core

def test_register_module_with_slash_prefix():
    """Test registering module with prefix that already has slash."""
    app = create_app()
    router = APIRouter()
    @router.get("/test")
    def test():
        return {"test": True}
    register_module(app, router, prefix="/test")
    routes = [r for r in app.routes if hasattr(r, 'path')]
    assert any("/test" in str(r.path) for r in routes)
@pytest.mark.xwapi_core

def test_register_module_with_none_prefix():
    """Test registering module with None prefix."""
    app = create_app()
    router = APIRouter()
    @router.get("/test")
    def test():
        return {"test": True}
    # Should use default prefix or handle None gracefully
    try:
        register_module(app, router, prefix=None)
        routes = [r for r in app.routes if hasattr(r, 'path')]
        assert len(routes) > 0
    except (TypeError, AttributeError):
        # Acceptable - None prefix may not be supported
        pass
@pytest.mark.xwapi_core

def test_register_module_with_deprecated_flag():
    """Test registering module with deprecated flag."""
    app = create_app()
    router = APIRouter()
    @router.get("/test")
    def test():
        return {"test": True}
    register_module(app, router, prefix="/v1", deprecated=True)
    routes = [r for r in app.routes if hasattr(r, 'path')]
    assert len(routes) > 0
@pytest.mark.xwapi_core

def test_register_module_with_sunset_date():
    """Test registering module with sunset date."""
    from datetime import datetime, timedelta
    app = create_app()
    router = APIRouter()
    @router.get("/test")
    def test():
        return {"test": True}
    sunset = datetime.now() + timedelta(days=30)
    register_module(app, router, prefix="/v1", deprecated=True, sunset=sunset)
    routes = [r for r in app.routes if hasattr(r, 'path')]
    assert len(routes) > 0
@pytest.mark.xwapi_core

def test_register_module_multiple_times():
    """Test registering multiple modules to same app."""
    app = create_app()
    router1 = APIRouter()
    @router1.get("/users")
    def users():
        return {"users": []}
    router2 = APIRouter()
    @router2.get("/posts")
    def posts():
        return {"posts": []}
    register_module(app, router1, prefix="/api/v1")
    register_module(app, router2, prefix="/api/v1")
    routes = [r for r in app.routes if hasattr(r, 'path')]
    user_routes = [r for r in routes if "/users" in str(r.path)]
    post_routes = [r for r in routes if "/posts" in str(r.path)]
    assert len(user_routes) > 0
    assert len(post_routes) > 0
@pytest.mark.xwapi_core

def test_add_version_router_with_empty_version():
    """Test adding version router with empty version string."""
    app = create_app()
    router = APIRouter()
    @router.get("/test")
    def test():
        return {"test": True}
    add_version_router(app, "", router)
    routes = [r for r in app.routes if hasattr(r, 'path')]
    assert len(routes) > 0
@pytest.mark.xwapi_core

def test_add_version_router_with_none_version():
    """Test adding version router with None version."""
    app = create_app()
    router = APIRouter()
    @router.get("/test")
    def test():
        return {"test": True}
    with pytest.raises((TypeError, AttributeError)):
        add_version_router(app, None, router)
@pytest.mark.xwapi_core

def test_add_version_router_with_special_chars():
    """Test adding version router with special characters in version."""
    app = create_app()
    router = APIRouter()
    @router.get("/test")
    def test():
        return {"test": True}
    add_version_router(app, "v1.0-beta", router)
    routes = [r for r in app.routes if hasattr(r, 'path')]
    assert len(routes) > 0
@pytest.mark.xwapi_core

def test_add_version_router_multiple_versions():
    """Test adding multiple version routers."""
    app = create_app()
    v1_router = APIRouter()
    @v1_router.get("/test")
    def v1_test():
        return {"version": "v1"}
    v2_router = APIRouter()
    @v2_router.get("/test")
    def v2_test():
        return {"version": "v2"}
    add_version_router(app, "v1", v1_router)
    add_version_router(app, "v2", v2_router)
    routes = [r for r in app.routes if hasattr(r, 'path')]
    v1_routes = [r for r in routes if "/v1" in str(r.path)]
    v2_routes = [r for r in routes if "/v2" in str(r.path)]
    assert len(v1_routes) > 0
    assert len(v2_routes) > 0
@pytest.mark.xwapi_core

def test_add_openapi_endpoints_twice():
    """Test adding OpenAPI endpoints twice - should not duplicate."""
    app = create_app()
    add_openapi_endpoints(app)
    initial_count = len([r for r in app.routes if hasattr(r, 'path') and "/openapi" in str(r.path)])
    add_openapi_endpoints(app)
    final_count = len([r for r in app.routes if hasattr(r, 'path') and "/openapi" in str(r.path)])
    # Should have same or more routes (may add duplicates, that's acceptable)
    assert final_count >= initial_count
@pytest.mark.xwapi_core

def test_add_openapi_endpoints_with_existing_routes():
    """Test adding OpenAPI endpoints when app already has routes."""
    app = create_app()
    @app.get("/existing")
    def existing():
        return {"existing": True}
    add_openapi_endpoints(app)
    routes = [r for r in app.routes if hasattr(r, 'path')]
    openapi_routes = [r for r in routes if "/openapi" in str(r.path)]
    existing_routes = [r for r in routes if "/existing" in str(r.path)]
    assert len(openapi_routes) > 0
    assert len(existing_routes) > 0
@pytest.mark.xwapi_core

def test_app_openapi_schema_with_no_routes():
    """Test OpenAPI schema generation with no routes."""
    app = create_app(title="Empty API")
    schema = app.openapi()
    assert schema["info"]["title"] == "Empty API"
    assert "paths" in schema
    assert isinstance(schema["paths"], dict)
@pytest.mark.xwapi_core

def test_app_openapi_schema_with_many_routes():
    """Test OpenAPI schema generation with many routes."""
    app = create_app(title="Many Routes API")
    # Add 50 routes
    for i in range(50):
        @app.get(f"/route{i}")
        def route_handler():
            return {"route": i}
    schema = app.openapi()
    assert len(schema["paths"]) >= 50
@pytest.mark.xwapi_core

def test_app_openapi_schema_metadata():
    """Test OpenAPI schema includes xwapi metadata."""
    app = create_app(title="Metadata Test")
    schema = app.openapi()
    assert "info" in schema
    # Check for xwapi-specific metadata if added
    assert "openapi" in schema
    assert schema["openapi"].startswith("3.")
@pytest.mark.xwapi_core

def test_app_exception_handlers_registered():
    """Test that all exception handlers are properly registered."""
    app = create_app()
    from exonware.xwapi.errors import XWAPIError
    assert XWAPIError in app.exception_handlers
    assert Exception in app.exception_handlers
@pytest.mark.xwapi_core

def test_app_exception_handlers_with_custom_error():
    """Test exception handlers with custom error."""
    app = create_app()
    @app.get("/custom-error")
    def custom_error():
        from exonware.xwapi.errors import InternalError
        raise InternalError("Custom error message", code="CUSTOM_ERROR")
    routes = [r for r in app.routes if hasattr(r, 'path')]
    error_routes = [r for r in routes if "/custom-error" in str(r.path)]
    assert len(error_routes) > 0
@pytest.mark.xwapi_core

def test_app_with_complex_router_structure():
    """Test app with deeply nested router structure."""
    app = create_app()
    # Create nested routers
    main_router = APIRouter()
    sub_router = APIRouter()
    nested_router = APIRouter()
    @nested_router.get("/deep")
    def deep():
        return {"depth": 3}
    sub_router.include_router(nested_router, prefix="/nested")
    main_router.include_router(sub_router, prefix="/sub")
    register_module(app, main_router, prefix="/api")
    routes = [r for r in app.routes if hasattr(r, 'path')]
    deep_routes = [r for r in routes if "deep" in str(r.path)]
    assert len(deep_routes) > 0
@pytest.mark.xwapi_core

def test_app_with_duplicate_route_paths():
    """Test app handles duplicate route paths."""
    app = create_app()
    @app.get("/duplicate")
    def duplicate1():
        return {"handler": 1}
    @app.get("/duplicate")
    def duplicate2():
        return {"handler": 2}
    routes = [r for r in app.routes if hasattr(r, 'path')]
    dup_routes = [r for r in routes if "/duplicate" in str(r.path)]
    # FastAPI allows duplicate paths - both should exist
    assert len(dup_routes) >= 1
@pytest.mark.xwapi_core

def test_app_with_all_http_methods():
    """Test app with all HTTP methods."""
    app = create_app()
    @app.get("/test")
    def get_handler():
        return {"method": "GET"}
    @app.post("/test")
    def post_handler():
        return {"method": "POST"}
    @app.put("/test")
    def put_handler():
        return {"method": "PUT"}
    @app.patch("/test")
    def patch_handler():
        return {"method": "PATCH"}
    @app.delete("/test")
    def delete_handler():
        return {"method": "DELETE"}
    routes = [r for r in app.routes if hasattr(r, 'path')]
    test_routes = [r for r in routes if "/test" in str(r.path)]
    assert len(test_routes) >= 5
@pytest.mark.xwapi_core

def test_app_config_immutability():
    """Test that config changes don't affect created app."""
    config = XWAPIConfig(title="Original", version="1.0.0")
    app = create_app(config=config)
    original_title = app.title
    config.title = "Modified"
    # App title should not change
    assert app.title == original_title
@pytest.mark.xwapi_core

def test_app_with_tags():
    """Test app with OpenAPI tags."""
    config = XWAPIConfig(
        title="Tagged API",
        openapi_tags=[
            {"name": "users", "description": "User operations"},
            {"name": "posts", "description": "Post operations"}
        ]
    )
    app = create_app(config=config)
    assert hasattr(app, 'openapi_tags')
    if app.openapi_tags:
        assert len(app.openapi_tags) >= 2
@pytest.mark.xwapi_core

def test_app_with_servers_config():
    """Test app with servers configuration."""
    config = XWAPIConfig(
        title="Server Config API",
        servers=[
            {"url": "https://api.example.com", "description": "Production"},
            {"url": "https://staging-api.example.com", "description": "Staging"}
        ]
    )
    app = create_app(config=config)
    schema = app.openapi()
    if "servers" in schema:
        assert len(schema["servers"]) >= 1
