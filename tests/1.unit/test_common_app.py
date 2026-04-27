#exonware/xwapi/tests/1.unit/test_common_app.py
"""
Unit tests for common/app.py (create_app, register_module, add_version_router).
Company: eXonware.com
"""

from __future__ import annotations
import pytest


@pytest.mark.xwapi_unit
class TestCreateApp:
    """Tests for create_app factory."""

    def test_create_app_default_engine(self):
        from exonware.xwapi.common.app import create_app
        app = create_app(title="Test", version="1.0.0")
        assert app is not None
        # Should be a FastAPI instance
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)

    def test_create_app_with_config(self):
        from exonware.xwapi.common.app import create_app
        from exonware.xwapi.config import XWAPIConfig
        cfg = XWAPIConfig(title="Custom", version="2.0.0")
        app = create_app(config=cfg)
        assert app is not None

    def test_create_app_unknown_engine_raises(self):
        from exonware.xwapi.common.app import create_app
        with pytest.raises(ValueError, match="Unknown engine"):
            create_app(engine="nonexistent_engine")

    def test_create_app_overrides_config(self):
        from exonware.xwapi.common.app import create_app
        from exonware.xwapi.config import XWAPIConfig
        cfg = XWAPIConfig(title="Original")
        app = create_app(config=cfg, title="Overridden")
        assert cfg.title == "Overridden"


@pytest.mark.xwapi_unit
class TestAddVersionRouter:
    """Tests for add_version_router."""

    def test_version_none_raises(self):
        from exonware.xwapi.common.app import add_version_router
        with pytest.raises(TypeError, match="version must be a string"):
            add_version_router(None, None, None)

    def test_register_module_none_app_raises(self):
        from exonware.xwapi.common.app import register_module
        with pytest.raises((TypeError, AttributeError)):
            register_module(None, None)
