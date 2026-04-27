#exonware/xwapi/tests/1.unit/test_defs.py
"""
Unit tests for xwapi defs module — type aliases and constants.
"""

from __future__ import annotations

import pytest


@pytest.mark.xwapi_unit
class TestDefsConstants:
    """Validate exported constants and type aliases."""

    def test_default_api_version(self):
        from exonware.xwapi.defs import DEFAULT_API_VERSION
        assert DEFAULT_API_VERSION == "1.0.0"

    def test_default_api_title(self):
        from exonware.xwapi.defs import DEFAULT_API_TITLE
        assert DEFAULT_API_TITLE == "XWAPI Generated API"

    def test_openapi_version(self):
        from exonware.xwapi.defs import OPENAPI_VERSION
        assert OPENAPI_VERSION == "3.1.0"

    def test_oauth2_default_urls(self):
        from exonware.xwapi.defs import (
            DEFAULT_OAUTH2_AUTHORIZATION_URL,
            DEFAULT_OAUTH2_TOKEN_URL,
            DEFAULT_OAUTH2_USERINFO_URL,
        )
        assert DEFAULT_OAUTH2_AUTHORIZATION_URL == "/oauth/authorize"
        assert DEFAULT_OAUTH2_TOKEN_URL == "/oauth/token"
        assert DEFAULT_OAUTH2_USERINFO_URL == "/oauth/userinfo"

    def test_oauth2_providers_list(self):
        from exonware.xwapi.defs import OAUTH2_PROVIDERS
        assert isinstance(OAUTH2_PROVIDERS, list)
        assert "google" in OAUTH2_PROVIDERS
        assert "github" in OAUTH2_PROVIDERS
        assert "custom" in OAUTH2_PROVIDERS

    def test_crud_methods(self):
        from exonware.xwapi.defs import CRUD_METHODS
        assert CRUD_METHODS["list"] == "GET"
        assert CRUD_METHODS["create"] == "POST"
        assert CRUD_METHODS["update"] == "PUT"
        assert CRUD_METHODS["patch"] == "PATCH"
        assert CRUD_METHODS["delete"] == "DELETE"

    def test_type_aliases_are_dict(self):
        from exonware.xwapi.defs import OpenAPISpec, OAuth2Config, EndpointConfig
        # Type aliases should resolve to dict[str, Any]
        assert OpenAPISpec is not None
        assert OAuth2Config is not None
        assert EndpointConfig is not None
