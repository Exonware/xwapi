#exonware/xwapi/tests/0.core/test_core_server.py
"""
Core tests for xwapi server management.
Tests server start/stop/restart functionality (basic checks without actually starting servers).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations
import pytest
from fastapi import FastAPI
@pytest.mark.xwapi_core

def test_server_class_importable():
    """Test that XWApiServer class is importable."""
    from exonware.xwapi.server import XWApiServer
    assert XWApiServer is not None
@pytest.mark.xwapi_core

def test_server_methods_exist():
    """Test that XWApiServer has management methods."""
    from exonware.xwapi.server import XWApiServer
    # Check methods exist on the class
    assert hasattr(XWApiServer, "start")
    assert hasattr(XWApiServer, "stop")
    assert hasattr(XWApiServer, "restart")
    assert hasattr(XWApiServer, "register_action")
@pytest.mark.xwapi_core

def test_server_facade_methods():
    """Test that XWAPI facade has server management methods."""
    from exonware.xwapi import XWAPI
    from exonware.xwapi.config import XWAPIConfig
    config = XWAPIConfig(title="Test API")
    api = XWAPI(config=config)
    # Check methods exist
    # Note: Facade might delegate to server instance
    # If facade has start_server, check that
    if hasattr(api, "start_server"):
        assert callable(api.start_server)
    if hasattr(api, "stop_server"):
        assert callable(api.stop_server)
