#exonware/xwapi/tests/1.unit/test_config.py
"""
Unit tests for xwapi config module — XWAPIConfig dataclass.
"""

from __future__ import annotations

import pytest


@pytest.mark.xwapi_unit
class TestXWAPIConfig:
    """Validate XWAPIConfig defaults and post_init behavior."""

    def test_defaults(self):
        from exonware.xwapi.config import XWAPIConfig
        cfg = XWAPIConfig()
        assert cfg.title == "XWAPI Generated API"
        assert cfg.version == "1.0.0"
        assert cfg.description is None
        assert cfg.enable_oauth2 is False
        assert cfg.oauth2_config is None
        assert cfg.servers == []
        assert cfg.default_security == []
        assert cfg.security_schemes == {}

    def test_custom_values(self):
        from exonware.xwapi.config import XWAPIConfig
        cfg = XWAPIConfig(
            title="My API",
            version="2.0.0",
            description="Test",
            enable_oauth2=False,
        )
        assert cfg.title == "My API"
        assert cfg.version == "2.0.0"
        assert cfg.description == "Test"

    def test_oauth2_auto_config_when_enabled(self):
        from exonware.xwapi.config import XWAPIConfig
        cfg = XWAPIConfig(enable_oauth2=True)
        assert cfg.oauth2_config is not None
        assert cfg.oauth2_config["authorization_url"] == "/oauth/authorize"
        assert cfg.oauth2_config["token_url"] == "/oauth/token"

    def test_oauth2_preserves_explicit_config(self):
        from exonware.xwapi.config import XWAPIConfig
        custom = {"authorization_url": "/custom/auth", "token_url": "/custom/token"}
        cfg = XWAPIConfig(enable_oauth2=True, oauth2_config=custom)
        assert cfg.oauth2_config["authorization_url"] == "/custom/auth"

    def test_servers_field(self):
        from exonware.xwapi.config import XWAPIConfig
        cfg = XWAPIConfig(servers=[{"url": "https://api.example.com"}])
        assert len(cfg.servers) == 1
        assert cfg.servers[0]["url"] == "https://api.example.com"

    def test_openapi_tags(self):
        from exonware.xwapi.config import XWAPIConfig
        tags = [{"name": "users", "description": "User operations"}]
        cfg = XWAPIConfig(openapi_tags=tags)
        assert cfg.openapi_tags == tags
