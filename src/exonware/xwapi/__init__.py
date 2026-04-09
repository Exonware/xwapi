#exonware/xwapi/src/exonware/xwapi/__init__.py
"""
xwapi: entity- and action-centric API library for the eXonware stack.

Define *exposable actions* (xwaction) and entities once, then publish them over HTTP/OpenAPI
(and align bots, consoles, or other adapters to the same contracts). The mirror direction is
first-class: build *clients* and agents that call those actions over APIs (see XWApiAgent).

Tagline: **build once, publish anywhere** — one logical surface; FastAPI is the default HTTP
engine (full OpenAPI/async ecosystem); Flask is available as an alternate registered engine
so you can swap deployment style without rewriting actions.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.5
"""
# =============================================================================
# XWLAZY — GUIDE_00_MASTER: config_package_lazy_install_enabled (EARLY)
# =============================================================================
# Dependency: exonware-xwlazy ([lazy] extra). Canonical import: exonware.xwlazy
try:
    from exonware.xwlazy import config_package_lazy_install_enabled

    config_package_lazy_install_enabled(
        __package__ or "exonware.xwapi",
        enabled=True,
        mode="smart",
    )
except ImportError:
    # xwlazy not installed — omit [lazy] extra or install exonware-xwlazy for lazy mode.
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
    ServerLifecycleError,
    StorageUnavailableError,
    ServicePausedError,
    create_error_response,
    xwapi_error_to_http_parts,
    http_status_to_xwapi_error,
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
from exonware.xwapi.server.pipeline import ActionPipelineManager, BackgroundWorker, InMemoryOutboxStore
from exonware.xwapi.providers import (
    LocalAuthProvider,
    XWAuthLibraryProvider,
    InMemoryStorageProvider,
    XWStorageProvider,
    InMemoryPaymentProvider,
)
from exonware.xwapi.token_management import APITokenManager
from exonware.xwapi.contracts import IApiServer
# Agent - direct import
from exonware.xwapi.client.xwclient import XWApiAgent
from exonware.xwapi.contracts import IApiAgent, IApiServicesProvider
from exonware.xwapi.contracts import IAuthProvider, IStorageProvider, IPaymentProvider
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
    "ServerLifecycleError",
    "StorageUnavailableError",
    "ServicePausedError",
    "create_error_response",
    "xwapi_error_to_http_parts",
    "http_status_to_xwapi_error",
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
    "ActionPipelineManager",
    "BackgroundWorker",
    "InMemoryOutboxStore",
    "APITokenManager",
    "LocalAuthProvider",
    "XWAuthLibraryProvider",
    "InMemoryStorageProvider",
    "XWStorageProvider",
    "InMemoryPaymentProvider",
    "AApiServer",
    "AApiAgent",
    "AApiServicesProvider",
    "IApiServer",
    "IAuthProvider",
    "IStorageProvider",
    "IPaymentProvider",
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
