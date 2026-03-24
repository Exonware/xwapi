#exonware/xwapi/src/exonware/xwapi/__init__.py
"""
xwapi: Entity-to-Web-API Conversion Library
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.1
"""
# =============================================================================
# XWLAZY INTEGRATION - Auto-install missing dependencies silently (EARLY)
# =============================================================================
# Activate xwlazy BEFORE other imports to enable auto-installation of missing dependencies
# This enables silent auto-installation of missing libraries when they are imported

try:
    from exonware.xwlazy import auto_enable_lazy
    auto_enable_lazy(__package__ or "exonware.xwapi", mode="smart")
except ImportError:
    # xwlazy not installed - lazy mode simply stays disabled (normal behavior)
    pass
# Core imports - safe, no dependencies
from exonware.xwapi.version import __version__, __author__, __email__
# Config imports - safe, minimal dependencies
from exonware.xwapi.config import XWAPIConfig
# Base imports - safe, only imports contracts
# Import from xwapi.base for consistency (these re-export from server/client/base for backward compatibility)
from exonware.xwapi.base import AApiServer, AApiAgent, AApiServicesProvider
# Errors - direct import (no circular dependency since errors.py doesn't import from __init__.py)
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
    create_error_response,
    get_http_status_code,
    error_to_http_response,
    get_error_headers,
    # HTTP Status Code Constants
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_501_NOT_IMPLEMENTED,
    HTTP_502_BAD_GATEWAY,
    HTTP_503_SERVICE_UNAVAILABLE,
    HTTP_504_GATEWAY_TIMEOUT,
)
# Engine system - engine-agnostic: only interfaces and registry imported
# Specific engines (FastAPIServerEngine, etc.) should be imported directly from their modules
from exonware.xwapi.server.engines import (
    IApiServerEngine,
    AApiServerEngineBase,
    ApiServerEngineRegistry,
    api_server_engine_registry,
)
# App factory - direct import
from exonware.xwapi.common.app import (
    create_app,
    register_module,
    add_version_router,
    add_openapi_endpoints,
)
# Query parameter parsing is handled directly in engine implementations
# Use XWQuery directly for query execution - no wrapper needed
# Middleware - direct import
from exonware.xwapi.server.middleware import (
    trace_middleware,
    tenant_middleware,
    rate_limit_middleware,
    auth_middleware,
    observability_middleware,
)
# OpenAPI - direct import
from exonware.xwapi.common.openapi import (
    merge_openapi_schemas,
    validate_openapi_schema,
    export_openapi_schema,
    add_openapi_metadata,
    get_openapi_version,
)
# Server - direct import
from exonware.xwapi.server.xwserver import XWApiServer
from exonware.xwapi.contracts import IApiServer
# Agent - direct import
from exonware.xwapi.client.xwclient import XWApiAgent
from exonware.xwapi.contracts import IApiAgent, IApiServicesProvider
# Agent engines - direct import
from exonware.xwapi.client.engines import (
    IApiAgentEngine,
    AgentType,
    ApiAgentEngineRegistry,
    api_agent_engine_registry,
    NativeAgentEngine,
)
# Serialization - use XWData/XWSystem directly, no wrapper needed
# Facade - direct import (import last to ensure all dependencies are loaded)
from exonware.xwapi.facade import XWAPI
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    # Facade
    "XWAPI",
    "XWAPIConfig",
    # App factory
    "create_app",
    "register_module",
    "add_version_router",
    "add_openapi_endpoints",
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
    "create_error_response",
    "get_http_status_code",
    "error_to_http_response",
    "get_error_headers",
    # HTTP Status Code Constants
    "HTTP_200_OK",
    "HTTP_201_CREATED",
    "HTTP_202_ACCEPTED",
    "HTTP_204_NO_CONTENT",
    "HTTP_400_BAD_REQUEST",
    "HTTP_401_UNAUTHORIZED",
    "HTTP_403_FORBIDDEN",
    "HTTP_404_NOT_FOUND",
    "HTTP_405_METHOD_NOT_ALLOWED",
    "HTTP_409_CONFLICT",
    "HTTP_422_UNPROCESSABLE_ENTITY",
    "HTTP_429_TOO_MANY_REQUESTS",
    "HTTP_500_INTERNAL_SERVER_ERROR",
    "HTTP_501_NOT_IMPLEMENTED",
    "HTTP_502_BAD_GATEWAY",
    "HTTP_503_SERVICE_UNAVAILABLE",
    "HTTP_504_GATEWAY_TIMEOUT",
    # Serialization - use XWData/XWSystem directly
    # Server management - XWApiServer (extends AApiServer)
    "XWApiServer",
    "AApiServer",
    "AApiAgent",
    "AApiServicesProvider",
    "IApiServer",
    "IApiServicesProvider",
    # Agent system
    "XWApiAgent",
    "IApiAgent",
    # Engine system (engine-agnostic: engines imported from their modules)
    "IApiServerEngine",
    "AApiServerEngineBase",
    "ApiServerEngineRegistry",
    "api_server_engine_registry",
    # Query - use XWQuery directly
    # Action - use XWAction engines directly
    # Middleware
    "trace_middleware",
    "tenant_middleware",
    "rate_limit_middleware",
    "auth_middleware",
    "observability_middleware",
    # OpenAPI
    "merge_openapi_schemas",
    "validate_openapi_schema",
    "export_openapi_schema",
    "add_openapi_metadata",
    "get_openapi_version",
]
