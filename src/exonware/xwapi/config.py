#exonware/xwapi/src/exonware/xwapi/config.py
"""
Configuration classes for xwapi library.
Uses XWSystem's configuration system for system-level settings.
API-specific settings (title, version, OAuth2) are stored here.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.2
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
    description: Optional[str] = None
    terms_of_service: Optional[str] = None
    contact: Optional[dict[str, str]] = None
    license_info: Optional[dict[str, str]] = None
    servers: list[dict[str, str]] = field(default_factory=list)
    enable_oauth2: bool = False
    oauth2_config: Optional[OAuth2Config] = None
    default_security: list[str] = field(default_factory=list)
    security_schemes: dict[str, Any] = field(default_factory=dict)
    openapi_tags: Optional[list[dict[str, Any]]] = None

    def __post_init__(self):
        """Post-initialization validation."""
        if self.enable_oauth2 and not self.oauth2_config:
            self.oauth2_config = {
                "authorization_url": "/oauth/authorize",
                "token_url": "/oauth/token",
                "userinfo_url": "/oauth/userinfo",
                "providers": [],
            }
