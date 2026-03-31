#!/usr/bin/env python3
"""
#exonware/xwapi/src/exonware/xwapi/common/app.py
Engine-Agnostic App Factory
Factory function for creating API applications with automatic OpenAPI generation,
versioning support, deprecation headers, and module router registration.
Works with any engine (FastAPI, Flask, etc.).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.2
"""

import logging
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from exonware.xwapi.config import XWAPIConfig
from exonware.xwapi.version import __version__
logger = logging.getLogger(__name__)


def create_app(
    config: Optional[XWAPIConfig] = None,
    title: Optional[str] = None,
    version: Optional[str] = None,
    description: Optional[str] = None,
    engine: str = "fastapi",
    **kwargs
) -> Any:
    """
    Create API application (engine-agnostic).
    Acts as a dispatcher to the appropriate engine implementation.
    Args:
        config: Optional XWAPIConfig instance
        title: API title (overrides config)
        version: API version (overrides config)
        description: API description (overrides config)
        engine: Engine name ("fastapi" default, or "flask", etc.)
        **kwargs: Additional framework-specific arguments
    Returns:
        Application instance (engine-specific)
    """
    # Prepare config
    if not config:
        config = XWAPIConfig(
            title=title or "XWAPI Application",
            version=version or "1.0.0",
            description=description
        )
    else:
        # Override if provided
        if title: config.title = title
        if version: config.version = version
        if description: config.description = description
    # Dispatch to engine via registry first (engine-agnostic pattern).
    engine_name = (engine or "").strip().lower()
    from exonware.xwapi.server.engines import api_server_engine_registry
    server_engine = api_server_engine_registry.get_engine(engine_name)
    if not server_engine:
        raise ValueError(f"Unknown engine: {engine}")
    return server_engine.create_app(config)


def register_module(
    app: Any,  # Engine-agnostic: accepts any framework app
    router: Any,  # Engine-agnostic: accepts any framework router
    prefix: str = "/v1",
    tags: Optional[list[str]] = None,
    deprecated: bool = False,
    sunset: Optional[datetime] = None,
) -> None:
    """
    Register a module router with versioning and deprecation support (engine-agnostic).
    Delegates to engine-specific implementations for router registration.
    Args:
        app: Framework application instance (engine-specific)
        router: Framework router instance (engine-specific)
        prefix: URL prefix (e.g., "/v1", "/v2")
        tags: Optional tags for OpenAPI grouping
        deprecated: Whether this version is deprecated
        sunset: Optional sunset date for deprecated version
    Example:
        >>> from exonware.xwapi import create_app
        >>> app = create_app(engine="fastapi")
        >>> 
        >>> # Engine-specific router creation
        >>> router = SomeRouterType()
        >>> router.get("/users")(get_users)
        >>> 
        >>> register_module(app, router, prefix="/v1", tags=["users"])
    """
    # Prefer capability-based registration over framework-name detection.
    if hasattr(app, "include_router"):
        app.include_router(
            router,
            prefix=prefix,
            tags=tags or [],
        )
        if deprecated and hasattr(app, "middleware"):
            @app.middleware("http")
            async def deprecation_middleware(request: Any, call_next: Callable):
                """Add deprecation headers to responses."""
                if request.url.path.startswith(prefix):
                    response = await call_next(request)
                    response.headers["Deprecation"] = "true"
                    if sunset:
                        response.headers["Sunset"] = sunset.strftime("%a, %d %b %Y %H:%M:%S GMT")
                    return response
                return await call_next(request)
        return

    if app is None:
        raise TypeError("Cannot register module with None app")
    app_type_name = type(app).__module__ + "." + type(app).__name__
    raise NotImplementedError(f"Module registration not implemented for engine type: {app_type_name}")


def add_version_router(
    app: Any,  # Engine-agnostic: accepts any framework app
    version: str,
    router: Any,  # Engine-agnostic: accepts any framework router
    tags: Optional[list[str]] = None,
    deprecated: bool = False,
    sunset: Optional[datetime] = None,
) -> None:
    """
    Add versioned router with automatic prefix (engine-agnostic).
    Convenience function that calls register_module with version prefix.
    Args:
        app: Framework application instance (engine-specific)
        version: Version string (e.g., "v1", "v2"). Empty string registers without version prefix.
        router: Framework router instance (engine-specific)
        tags: Optional tags for OpenAPI grouping
        deprecated: Whether this version is deprecated
        sunset: Optional sunset date for deprecated version
    Raises:
        TypeError: If version is None (must be a string)
    Example:
        >>> add_version_router(app, "v1", router, tags=["api"])
        >>> # Router will be available at /v1/...
    """
    # Validate version is not None
    if version is None:
        raise TypeError("version must be a string, not None")
    # Handle empty version: register without version prefix
    if not version:
        prefix = ""
    elif version.startswith("/"):
        prefix = version.rstrip("/")  # Remove trailing slash if present
    else:
        prefix = f"/{version}"
    register_module(app, router, prefix=prefix, tags=tags, deprecated=deprecated, sunset=sunset)


def add_openapi_endpoints(app: Any) -> None:  # Engine-agnostic: accepts any framework app
    """
    Add OpenAPI spec export endpoints (engine-agnostic).
    Delegates to engine-specific implementations for endpoint registration.
    Args:
        app: Framework application instance (engine-specific)
    """
    if hasattr(app, "get") and hasattr(app, "openapi"):
        @app.get("/openapi.json", include_in_schema=False)
        async def get_openapi_json() -> dict[str, Any]:
            """Get OpenAPI specification as JSON."""
            return app.openapi()
        @app.get("/openapi.yaml", include_in_schema=False)
        async def get_openapi_yaml() -> str:
            """Get OpenAPI specification as YAML using XWData."""
            schema = app.openapi()
            # Use XWData directly for YAML serialization
            try:
                from exonware.xwdata import XWData
                xwdata = XWData(schema)
                return xwdata.to_format("yaml")
            except ImportError:
                # Fallback: try xwsystem serializer
                from exonware.xwsystem.io.serialization import YamlSerializer
                return YamlSerializer().encode(schema, options={"default_flow_style": False})
        return

    app_type_name = type(app).__module__ + "." + type(app).__name__
    raise NotImplementedError(f"OpenAPI endpoints not implemented for engine type: {app_type_name}")
