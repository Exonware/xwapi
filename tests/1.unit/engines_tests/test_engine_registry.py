#exonware/xwapi/tests/1.unit/engines_tests/test_engine_registry.py
"""
Unit tests for API Server Engine Registry.
Tests engine registration, lookup, and management.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations
import pytest
from unittest.mock import Mock, MagicMock
from exonware.xwapi.server.engines import ApiServerEngineRegistry, api_server_engine_registry
from exonware.xwapi.server.engines.contracts import IApiServerEngine
@pytest.mark.xwapi_unit

def test_engine_registry_initialization():
    """Test engine registry initialization."""
    registry = ApiServerEngineRegistry()
    assert registry is not None
    assert hasattr(registry, "_engines")
    assert isinstance(registry._engines, dict)
@pytest.mark.xwapi_unit

def test_engine_registry_register_engine():
    """Test registering an engine with registry."""
    registry = ApiServerEngineRegistry()
    mock_engine = MagicMock(spec=IApiServerEngine)
    mock_engine.name = "test_engine"
    registry.register(mock_engine)
    assert "test_engine" in registry._engines
    assert registry._engines["test_engine"] == mock_engine
@pytest.mark.xwapi_unit

def test_engine_registry_get_engine():
    """Test retrieving an engine from registry."""
    registry = ApiServerEngineRegistry()
    mock_engine = MagicMock(spec=IApiServerEngine)
    mock_engine.name = "test_engine"
    registry.register(mock_engine)
    retrieved = registry.get_engine("test_engine")
    assert retrieved == mock_engine
@pytest.mark.xwapi_unit

def test_engine_registry_get_nonexistent_engine():
    """Test retrieving non-existent engine returns None."""
    registry = ApiServerEngineRegistry()
    result = registry.get_engine("nonexistent")
    assert result is None
@pytest.mark.xwapi_unit

def test_engine_registry_default_engine():
    """Test setting and getting default engine."""
    registry = ApiServerEngineRegistry()
    mock_engine = MagicMock(spec=IApiServerEngine)
    mock_engine.name = "default_engine"
    registry.register(mock_engine, set_default=True)
    default = registry.get_engine()  # No name = default
    assert default == mock_engine
@pytest.mark.xwapi_unit

def test_global_engine_registry_exists():
    """Test that global engine registry exists."""
    assert api_server_engine_registry is not None
    assert isinstance(api_server_engine_registry, ApiServerEngineRegistry)
@pytest.mark.xwapi_unit

def test_global_engine_registry_has_fastapi():
    """Test that global registry has FastAPI engine."""
    engine = api_server_engine_registry.get_engine("fastapi")
    # FastAPI engine should be auto-registered
    assert engine is not None
    assert engine.name == "fastapi"


_OPTIONAL_HTTP_ENGINES = (
    "starlette",
    "quart",
    "sanic",
    "aiohttp",
    "blacksheep",
    "litestar",
    "django",
    "mangum",
)


@pytest.mark.xwapi_unit
@pytest.mark.parametrize("engine_name", _OPTIONAL_HTTP_ENGINES)
def test_optional_http_engine_registered_when_dependency_installed(engine_name: str) -> None:
    """
    Optional engines register only when their framework imports cleanly.
    If the extra is installed, the global registry must expose the engine.
    """
    try:
        __import__(engine_name)
    except ImportError:
        pytest.skip(f"{engine_name} not installed")
    api_server_engine_registry.get_engine("fastapi")  # trigger lazy _auto_register_engines
    eng = api_server_engine_registry.get_engine(engine_name)
    assert eng is not None
    assert eng.name == engine_name
