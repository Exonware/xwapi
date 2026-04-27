#exonware/xwapi/src/exonware/xwapi/server/engines/fastapi.py
"""
Default HTTP **server engine**: FastAPI (ASGI, OpenAPI, async) for exposable actions.

Uses ``FastAPIActionEngine`` from xwaction. Prefer this engine when you want the full
FastAPI/Starlette ecosystem; use ``flask`` engine for WSGI instead.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.12
"""

from typing import Any
from datetime import datetime, timezone
import fastapi
from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn
from exonware.xwaction.engines.fastapi import FastAPIActionEngine
from exonware.xwapi.errors import (
    XWAPIError,
    ValidationError,
    InternalError,
    get_trace_id,
    http_status_to_xwapi_error,
    xwapi_error_to_http_parts,
)
# Query parameter parsing - use XWQuery directly, no need for QueryParams class
from exonware.xwapi.version import __version__
from exonware.xwapi.server.http import starlette_json_response_from_xwapi_error
from exonware.xwapi.server.middleware.trace import trace_middleware
from .http_base import AHttpServerEngineBase
from .contracts import ProtocolType
from exonware.xwapi.config import XWAPIConfig
from exonware.xwsystem import get_logger
logger = get_logger(__name__)
# FastAPI-specific query parameter dependency (engine-specific)
# Parse query strings directly and pass to XWQuery - no need for QueryParams class

def get_query_params(
    filter: str | None = Query(None, alias="filter", description="Filter expression (e.g., 'status:active')"),
    sort: str | None = Query(None, description="Sort expression (e.g., '-created_at' or 'name:asc')"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    cursor: str | None = Query(None, description="Cursor for cursor-based pagination"),
    search: str | None = Query(None, description="Search query string"),
) -> dict[str, Any]:
    """
    FastAPI dependency for parsing query parameters.
    Returns query parameters as dict for direct use with XWQuery.
    Usage:
        @app.get("/items")
        async def list_items(params: dict = Depends(get_query_params)):
            # Build XWQuery from params
            if params.get("filter") or params.get("search"):
                from exonware.xwquery import XWQuery
                query_str = build_query_string(params)
                results = XWQuery.execute(query_str, data)
            else:
                results = data
            return results
    Args:
        filter: Filter expression
        sort: Sort expression
        limit: Maximum results (1-100, default: 20)
        offset: Pagination offset (default: 0)
        cursor: Cursor for pagination
        search: Search query
    Returns:
        Dictionary with query parameters
    """
    return {
        "filter": filter,
        "sort": sort,
        "limit": limit,
        "offset": offset,
        "cursor": cursor,
        "search": search,
    }
# FastAPI-specific exception handlers (engine-specific)
async def xwapi_exception_handler(request: "fastapi.Request", exc: XWAPIError) -> "fastapi.responses.JSONResponse":
    """
    Global exception handler for XWAPIError (FastAPI-specific).
    Handles all XWAPIError exceptions and converts them to uniform error responses
    with trace_id injection and structured logging.
    Args:
        request: FastAPI request object
        exc: XWAPIError exception
    Returns:
        JSONResponse with uniform error shape
    """
    trace_id = get_trace_id(request)
    # Log error (structured logging)
    logger.error(
        f"API error: {exc.code} - {exc.message}",
        extra={
            "trace_id": trace_id,
            "error_code": exc.code,
            "path": request.url.path,
            "method": request.method,
            "details": exc.details,
        }
    )
    return starlette_json_response_from_xwapi_error(exc, request=request)
async def http_exception_handler(request: "fastapi.Request", exc: Any) -> "fastapi.responses.JSONResponse":
    """
    Handler for FastAPI HTTPException (FastAPI-specific).
    Converts HTTPException to uniform error response format.
    Args:
        request: FastAPI request object
        exc: HTTPException (FastAPI or Starlette)
    Returns:
        JSONResponse with uniform error shape
    """
    message = str(exc.detail or "HTTP error")
    error = http_status_to_xwapi_error(exc.status_code, message)
    body, _, headers = xwapi_error_to_http_parts(error, request=request)
    if isinstance(getattr(exc, "headers", None), dict):
        headers.update(exc.headers)
    # Preserve original framework status for HTTPException passthrough.
    return JSONResponse(status_code=exc.status_code, content=body, headers=headers)

async def request_validation_exception_handler(request: "fastapi.Request", exc: RequestValidationError) -> "fastapi.responses.JSONResponse":
    """Convert FastAPI validation errors into unified XWAPI format."""
    error = ValidationError(
        message="Request validation failed",
        details={"errors": exc.errors()},
        hint="Ensure request payload and parameters match endpoint schema",
    )
    return starlette_json_response_from_xwapi_error(error, request=request)
async def generic_exception_handler(request: "fastapi.Request", exc: Exception) -> "fastapi.responses.JSONResponse":
    """
    Handler for unhandled exceptions (FastAPI-specific).
    Converts all unhandled exceptions to InternalError with uniform shape.
    Args:
        request: FastAPI request object
        exc: Exception
    Returns:
        JSONResponse with uniform error shape
    """
    trace_id = get_trace_id(request)
    # Classify error type for better error messages
    error_type = type(exc).__name__
    error_message = str(exc) or "Internal server error"
    # Handle connection-related errors
    if any(keyword in error_type.lower() or keyword in error_message.lower() 
           for keyword in ['connection', 'connect', 'network', 'timeout', 'refused', 'unreachable']):
        error = InternalError(
            message=f"Connection error: {error_message}",
            code="ConnectionError",
            details={
                "exception_type": error_type,
                "error_category": "connection"
            },
            hint="Check network connectivity and server availability",
        )
    # Handle template-related errors
    elif any(keyword in error_type.lower() or keyword in error_message.lower() 
             for keyword in ['template', 'missing template']):
        error = InternalError(
            message=f"Template error: {error_message}",
            code="TemplateError",
            details={
                "exception_type": error_type,
                "error_category": "template"
            },
            hint="Check template configuration and file availability",
        )
    else:
        # Generic internal error
        error = InternalError(
            message=error_message,
            code="InternalError",
            details={"exception_type": error_type},
            hint="Check server logs for details",
        )
    # Use generic engine-agnostic utilities
    trace_id = get_trace_id(request)
    # Log error
    logger.exception(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "trace_id": trace_id,
            "path": request.url.path,
            "method": request.method,
        }
    )
    return starlette_json_response_from_xwapi_error(error, request=request)

class FastAPIServerEngine(AHttpServerEngineBase):
    """
    FastAPI Server Engine
    Implements API server using FastAPI framework.
    Uses XWAction's FastAPIActionEngine internally for action execution.
    """

    def __init__(self):
        """Initialize FastAPI server engine."""
        super().__init__("fastapi")
        self._app: FastAPI | None = None
        self._protocol_type = ProtocolType.HTTP_REST  # FastAPI is HTTP REST
        self._fastapi_action_engine: FastAPIActionEngine | None = None
    @property

    def protocol_type(self) -> ProtocolType:
        """Get protocol type (HTTP_REST)."""
        return self._protocol_type

    def create_app(self, config: XWAPIConfig) -> FastAPI:
        """
        Create FastAPI application.
        Args:
            config: XWAPI configuration
        Returns:
            FastAPI application instance
        """
        # Prepare final config values
        final_title = config.title or "XWAPI Application"
        final_version = config.version or "1.0.0"
        final_description = config.description
        servers = config.servers or []
        # Create FastAPI app
        app = FastAPI(
            title=final_title,
            version=final_version,
            description=final_description,
            servers=servers if servers else None,
        )
        # Apply OpenAPI tags if configured
        if config.openapi_tags:
            app.openapi_tags = config.openapi_tags
            logger.debug(f"Applied {len(config.openapi_tags)} OpenAPI tags")
        # Register global exception handlers
        app.add_exception_handler(XWAPIError, xwapi_exception_handler)
        app.add_exception_handler(HTTPException, http_exception_handler)
        # Starlette middleware often raises starlette.exceptions.HTTPException directly.
        # Register the same adapter to keep error shape consistent across middleware stacks.
        app.add_exception_handler(StarletteHTTPException, http_exception_handler)
        app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
        app.add_exception_handler(Exception, generic_exception_handler)
        # Install request trace correlation middleware for all routes.
        app.middleware("http")(trace_middleware)
        # Fix middleware structure if needed (workaround for middleware format issues)
        # FastAPI expects user_middleware to contain tuples of (cls, options) with exactly 2 elements
        # Some engines may add middleware incorrectly, causing "too many values to unpack" errors
        if hasattr(app, 'user_middleware'):
            fixed_middleware = []
            for item in app.user_middleware:
                # FastAPI expects tuples of (cls, options) with exactly 2 elements
                if isinstance(item, tuple):
                    if len(item) == 2:
                        # Correct format: (cls, options)
                        fixed_middleware.append(item)
                    elif len(item) > 2:
                        # Too many values: take only first 2 elements
                        logger.warning(f"Middleware item has {len(item)} elements, expected 2. Truncating.")
                        fixed_middleware.append((item[0], item[1]))
                    # Skip items with 0 or 1 elements as they're invalid
                # Non-tuple items should not be in user_middleware, skip them
            app.user_middleware[:] = fixed_middleware
        # Customize OpenAPI schema
        def custom_openapi() -> dict[str, Any]:
            """Generate custom OpenAPI schema with xwapi enhancements."""
            if app.openapi_schema:
                return app.openapi_schema
            openapi_schema = get_openapi(
                title=final_title,
                version=final_version,
                description=final_description,
                routes=app.routes,
            )
            # Ensure OpenAPI 3.1.0
            openapi_schema["openapi"] = "3.1.0"
            # Collect schemas from XWApiServer (pre-collected during action registration)
            # This is engine-agnostic: xwapi collects schemas, engine just includes them
            collected_schemas = {}
            # Get pre-collected schemas from app state (collected by XWApiServer)
            if hasattr(app, 'state') and hasattr(app.state, 'xwapi_collected_schemas'):
                collected_schemas = app.state.xwapi_collected_schemas.copy()
            # Ensure components.schemas exists
            if "components" not in openapi_schema:
                openapi_schema["components"] = {}
            if "schemas" not in openapi_schema["components"]:
                openapi_schema["components"]["schemas"] = {}
            # Merge collected schemas (deduplicate: existing FastAPI schemas take precedence)
            existing_schema_names = set(openapi_schema["components"]["schemas"].keys())
            for schema_name, schema_def in collected_schemas.items():
                if schema_name not in existing_schema_names:
                    openapi_schema["components"]["schemas"][schema_name] = schema_def
            if collected_schemas:
                logger.debug(f"Included {len(collected_schemas)} pre-collected schemas from XWApiServer")
            # Collect all tags from routes and ensure descriptions
            # Priority: 1) config.openapi_tags, 2) app.openapi_tags, 3) collect from routes
            config_tags = {t.get("name") if isinstance(t, dict) else t: t for t in (config.openapi_tags or [])}
            app_tags = {t.get("name") if isinstance(t, dict) else t: t for t in (app.openapi_tags or [])}
            route_tags = set()
            # Collect tags from all routes
            for route in app.routes:
                if hasattr(route, 'tags') and route.tags:
                    route_tags.update(route.tags)
            # Build tags list with descriptions (engine-agnostic: use what's provided)
            final_tags = []
            for tag_name in sorted(route_tags):
                # Priority: config tags > app tags > generic fallback
                if tag_name in config_tags:
                    tag_def = config_tags[tag_name]
                    if isinstance(tag_def, dict):
                        final_tags.append(tag_def)
                    else:
                        final_tags.append({"name": tag_name, "description": f"{tag_name} endpoints"})
                elif tag_name in app_tags:
                    tag_def = app_tags[tag_name]
                    if isinstance(tag_def, dict):
                        final_tags.append(tag_def)
                    else:
                        final_tags.append({"name": tag_name, "description": f"{tag_name} endpoints"})
                else:
                    # Generic fallback - no hardcoded descriptions
                    final_tags.append({"name": tag_name, "description": f"{tag_name} endpoints"})
            # Update schema with collected tags
            if final_tags:
                openapi_schema["tags"] = final_tags
                # Update app.openapi_tags if not already set from config
                if not app.openapi_tags:
                    app.openapi_tags = final_tags
            # Add xwapi metadata
            openapi_schema["info"]["x-xwapi-version"] = __version__
            openapi_schema["info"]["x-generated-at"] = datetime.now(timezone.utc).isoformat()
            app.openapi_schema = openapi_schema
            return app.openapi_schema
        app.openapi = custom_openapi
        self._app = app
        return app

    def _register_http_action(self, app: FastAPI, action: Any, 
                              path: str, method: str) -> bool:
        """
        Register XWAction as FastAPI endpoint.
        Uses XWAction's FastAPIActionEngine.register_action() method.
        Args:
            app: FastAPI application instance
            action: XWAction instance
            path: Endpoint path
            method: HTTP method
        Returns:
            True if registration successful
        Raises:
            TypeError: If action is None
        """
        # Validate action is not None
        if action is None:
            raise TypeError("action must not be None")
        # Validate path is not None
        if path is None:
            raise TypeError("path must not be None")
        # Trigger lazy load of action_engine_registry (base._get_action_engine)
        _ = self._get_action_engine(action, "fastapi")
        if not self._action_engine_registry:
            logger.error("Action Engine Registry not available. xwaction is required.")
            return False
        # Optimization: Don't fetch from registry every time
        if not self._fastapi_action_engine:
            # Get or create FastAPIActionEngine
            engine = self._action_engine_registry.get_engine("fastapi")
            if not engine:
                # Register FastAPIActionEngine if not present
                engine = FastAPIActionEngine()
                self._action_engine_registry.register(engine)
            self._fastapi_action_engine = engine
        # Use FastAPIActionEngine's register_action method
        # Note: register_action handles binding the app to the engine internally
        success = self._fastapi_action_engine.register_action(action, app, path, method)
        if success:
            logger.info(f"Registered action '{getattr(action, 'api_name', 'unknown')}' as {method} {path}")
        else:
            logger.error(f"Failed to register action '{getattr(action, 'api_name', 'unknown')}'")
        return success

    def generate_schema(self, app: FastAPI, actions: list[Any], 
                       config: XWAPIConfig) -> dict[str, Any]:
        """Generate OpenAPI specification (HTTP schema)."""
        return self.generate_openapi(app, actions, config)

    def generate_openapi(self, app: FastAPI, actions: list[Any], 
                        config: XWAPIConfig) -> dict[str, Any]:
        """
        Generate OpenAPI specification.
        Args:
            app: FastAPI application instance
            actions: List of actions to include
            config: XWAPIConfig instance
        Returns:
            OpenAPI schema dictionary
        Raises:
            TypeError: If app is None
        """
        # Validate app is not None
        if app is None:
            raise TypeError("app must not be None")
        """
        Generate OpenAPI specification.
        Args:
            app: FastAPI application instance
            actions: List of registered XWAction instances
            config: XWAPI configuration
        Returns:
            OpenAPI 3.1 specification dictionary
        """
        # FastAPI has built-in OpenAPI generation
        if hasattr(app, 'openapi'):
            return app.openapi()
        # Fallback: generate from generic base implementation
        return super().generate_openapi(app, actions, config)

    def start_server(self, app: FastAPI, host: str = "0.0.0.0", 
                    port: int = 8000, **kwargs) -> None:
        """
        Start FastAPI server using uvicorn.
        Args:
            app: FastAPI application instance
            host: Host to bind to
            port: Port to bind to
            **kwargs: Additional uvicorn options (reload, log_level, etc.)
        """
        import sys
        import asyncio
        # Fix for Windows asyncio event loop issues
        # uvicorn.run() will create its own event loop, but we need to ensure
        # the Windows event loop policy is set before uvicorn tries to create one
        if sys.platform == "win32":
            # Set Windows event loop policy to avoid 'NoneType' errors
            # This must be done before any asyncio operations
            if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
                try:
                    # Only set if not already set
                    current_policy = asyncio.get_event_loop_policy()
                    if not isinstance(current_policy, asyncio.WindowsSelectorEventLoopPolicy):
                        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                except (RuntimeError, AttributeError):
                    # If there's any issue, just set it
                    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            # Disable uvloop on Windows (uvloop doesn't support Windows)
            # Force use of asyncio's default event loop policy
            kwargs.setdefault("loop", "auto")  # Use auto, but Windows will fall back to SelectorEventLoop
        # Default uvicorn options
        uvicorn_kwargs = {
            "host": host,
            "port": port,
            "log_level": kwargs.pop("log_level", "info"),
        }
        # On Windows, explicitly use asyncio loop (uvloop doesn't support Windows)
        if sys.platform == "win32":
            uvicorn_kwargs["loop"] = "asyncio"
        else:
            # On Unix, use auto (will try uvloop if available)
            if "loop" in kwargs:
                uvicorn_kwargs["loop"] = kwargs.pop("loop")
        # Add remaining kwargs
        uvicorn_kwargs.update(kwargs)
        logger.info(f"Starting FastAPI server on {host}:{port}")
        config = uvicorn.Config(app, **uvicorn_kwargs)
        if sys.platform == "win32":
            config.loop = "asyncio"
        server = uvicorn.Server(config)
        if hasattr(app, "state"):
            app.state.xwapi_uvicorn_server = server
        server.run()

    def stop_server(self, app: FastAPI) -> None:
        """Stop a running FastAPI uvicorn server if it is tracked on app state."""
        server = None
        if hasattr(app, "state"):
            server = getattr(app.state, "xwapi_uvicorn_server", None)
        if server is None:
            logger.warning("No tracked uvicorn server found on FastAPI app state")
            return
        server.should_exit = True
