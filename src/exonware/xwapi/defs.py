#exonware/xwapi/src/exonware/xwapi/defs.py
"""
Types and constants shared by publishers and clients of exposable actions (OpenAPI, OAuth2).

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.10
"""

from typing import Any, Optional
from datetime import datetime
# Type aliases
OpenAPISpec = dict[str, Any]
OAuth2Config = dict[str, Any]
EndpointConfig = dict[str, Any]
# Constants
DEFAULT_API_VERSION = "1.0.0"
DEFAULT_API_TITLE = "XWAPI Generated API"
OPENAPI_VERSION = "3.1.0"
# Default OAuth 2.0 endpoints
DEFAULT_OAUTH2_AUTHORIZATION_URL = "/oauth/authorize"
DEFAULT_OAUTH2_TOKEN_URL = "/oauth/token"
DEFAULT_OAUTH2_USERINFO_URL = "/oauth/userinfo"
# Supported OAuth 2.0 providers
OAUTH2_PROVIDERS = [
    "google",
    "github",
    "microsoft",
    "facebook",
    "apple",
    "custom",
]
# Default HTTP methods for CRUD operations
CRUD_METHODS = {
    "list": "GET",
    "get": "GET",
    "create": "POST",
    "update": "PUT",
    "patch": "PATCH",
    "delete": "DELETE",
}
