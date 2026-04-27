#exonware/xwapi/tests/1.unit/test_http_helpers.py
"""
Unit tests for xwapi http module — register_startup_handler, add_http_middleware.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.mark.xwapi_unit
class TestHTTPHelpers:

    def test_register_startup_handler(self):
        from exonware.xwapi.http import register_startup_handler
        app = MagicMock()
        handler = AsyncMock()
        register_startup_handler(app, handler)
        app.on_event.assert_called_once_with("startup")

    def test_add_http_middleware(self):
        from exonware.xwapi.http import add_http_middleware
        app = MagicMock()
        middleware = AsyncMock()
        add_http_middleware(app, middleware)
        app.middleware.assert_called_once_with("http")
