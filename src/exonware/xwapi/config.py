#exonware/xwapi/src/exonware/xwapi/config.py
"""
API-level configuration for publishing exposable actions (title, version, OAuth2, security).

System-wide settings remain in XWSystem; this module holds what OpenAPI and HTTP engines need.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.4
"""

from typing import Any, Optional
from dataclasses import dataclass, field
from exonware.xwapi.defs import OAuth2Config, DEFAULT_API_VERSION, DEFAULT_API_TITLE
@dataclass

class XWAPIConfig:
    """
    Configuration for XWAPI instance.
    API-specific configuration. For system-level settings, use XWSystem config.
    """
    title: str = DEFAULT_API_TITLE
    version: str = DEFAULT_API_VERSION
    description: str | None = None
    terms_of_service: str | None = None
    contact: dict[str, str] | None = None
    license_info: dict[str, str] | None = None
    servers: list[dict[str, str]] = field(default_factory=list)
    enable_oauth2: bool = False
    oauth2_config: OAuth2Config | None = None
    default_security: list[str] = field(default_factory=list)
    security_schemes: dict[str, Any] = field(default_factory=dict)
    openapi_tags: list[dict[str, Any]] | None = None

    def __post_init__(self):
        """Post-initialization validation."""
        if self.enable_oauth2 and not self.oauth2_config:
            self.oauth2_config = {
                "authorization_url": "/oauth/authorize",
                "token_url": "/oauth/token",
                "userinfo_url": "/oauth/userinfo",
                "providers": [],
            }
