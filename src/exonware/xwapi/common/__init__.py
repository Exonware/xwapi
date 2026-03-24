#exonware/xwapi/src/exonware/xwapi/common/__init__.py
"""
Common package for xwapi library.
Contains shared utilities used by both server and client:
- base.py: Abstract base classes (AApiServer, AApiAgent)
- errors.py: Error handling
- openapi.py: OpenAPI schema generation
- app.py: App factory functions
- utils/: Common utilities
Note: config.py moved to root folder, action.py/query.py/serialization.py removed (use XWAction/XWQuery/XWData directly)
"""
# Re-export commonly used items for backward compatibility

from exonware.xwapi.base import AAPIEndpoint, AAPIGenerator
from exonware.xwapi.server.base import AApiServer
from exonware.xwapi.client.base import AApiAgent
from exonware.xwapi.config import XWAPIConfig
from exonware.xwapi.errors import (
    XWAPIError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    InternalError,
    OpenAPIGenerationError,
    FastAPICreationError,
    EntityMappingError,
    OAuth2ConfigurationError,
    EndpointConfigurationError,
)
from exonware.xwapi.contracts import (
    IApiServer,
    IApiAgent,
    IAPIEndpoint,
    IAPIGenerator,
)
from exonware.xwapi.common.openapi import (
    merge_openapi_schemas,
    validate_openapi_schema,
    export_openapi_schema,
    add_openapi_metadata,
    get_openapi_version,
)
from exonware.xwapi.common.app import (
    create_app,
    register_module,
    add_version_router,
    add_openapi_endpoints,
)
from exonware.xwapi.facade import XWAPI
__all__ = [
    # Base classes
    "AApiServer",
    "AApiAgent",
    "AAPIEndpoint",
    "AAPIGenerator",
    # Config
    "XWAPIConfig",
    # Errors
    "XWAPIError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "RateLimitError",
    "InternalError",
    "OpenAPIGenerationError",
    "FastAPICreationError",
    "EntityMappingError",
    "OAuth2ConfigurationError",
    "EndpointConfigurationError",
    # Contracts
    "IApiServer",
    "IApiAgent",
    "IAPIEndpoint",
    "IAPIGenerator",
    # OpenAPI
    "merge_openapi_schemas",
    "validate_openapi_schema",
    "export_openapi_schema",
    "add_openapi_metadata",
    "get_openapi_version",
    # App
    "create_app",
    "register_module",
    "add_version_router",
    "add_openapi_endpoints",
    # Facade
    "XWAPI",
]
