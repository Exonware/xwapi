#exonware/xwapi/tests/1.unit/engines_tests/test_fastapi_engine.py
"""
Unit tests for FastAPI Server Engine.
Tests FastAPI engine initialization, app creation, and action registration.
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
@pytest.mark.xwapi_unit

def test_fastapi_engine_initialization():
    """Test FastAPI engine initialization."""
    engine = FastAPIServerEngine()
    assert engine is not None
    assert engine.name == "fastapi"
    assert engine.protocol_type == ProtocolType.HTTP_REST
@pytest.mark.xwapi_unit

def test_fastapi_engine_create_app():
    """Test creating FastAPI app with engine."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test API", version="1.0.0")
    app = engine.create_app(config)
    assert app is not None
    from fastapi import FastAPI
    assert isinstance(app, FastAPI)
    assert app.title == "Test API"
    assert app.version == "1.0.0"
@pytest.mark.xwapi_unit

def test_fastapi_engine_protocol_type():
    """Test that FastAPI engine has correct protocol type."""
    engine = FastAPIServerEngine()
    assert engine.protocol_type == ProtocolType.HTTP_REST
@pytest.mark.xwapi_unit

def test_fastapi_engine_exception_handlers():
    """Test that FastAPI engine registers exception handlers."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test API")
    app = engine.create_app(config)
    # Check that exception handlers are registered
    from exonware.xwapi.errors import XWAPIError
    assert XWAPIError in app.exception_handlers
    assert Exception in app.exception_handlers
@pytest.mark.xwapi_unit

def test_fastapi_engine_openapi_schema():
    """Test that FastAPI engine generates OpenAPI schema."""
    engine = FastAPIServerEngine()
    config = XWAPIConfig(title="Test API", version="1.0.0")
    app = engine.create_app(config)
    schema = app.openapi()
    assert schema is not None
    assert schema["info"]["title"] == "Test API"
    assert schema["info"]["version"] == "1.0.0"
    assert "openapi" in schema
    assert schema["openapi"].startswith("3.")
@pytest.mark.xwapi_unit

def test_fastapi_engine_inherits_from_base():
    """Test that FastAPIServerEngine inherits from base classes."""
    from exonware.xwapi.server.engines.base import AApiServerEngineBase
    from exonware.xwapi.server.engines.http_base import AHttpServerEngineBase
    engine = FastAPIServerEngine()
    assert isinstance(engine, AHttpServerEngineBase)
    assert isinstance(engine, AApiServerEngineBase)
@pytest.mark.xwapi_unit

def test_fastapi_engine_implements_interface():
    """Test that FastAPIServerEngine implements IApiServerEngine."""
    from exonware.xwapi.server.engines.contracts import IApiServerEngine
    engine = FastAPIServerEngine()
    # Check interface methods exist
    assert hasattr(engine, "create_app")
    assert hasattr(engine, "protocol_type")
    assert hasattr(engine, "name")
@pytest.mark.xwapi_unit

def test_fastapi_engine_registry_integration():
    """Test that FastAPI engine can be retrieved from registry."""
    from exonware.xwapi.server.engines import api_server_engine_registry
    engine = api_server_engine_registry.get_engine("fastapi")
    # Engine should be available (auto-registered)
    assert engine is not None
    assert engine.name == "fastapi"
