#!/usr/bin/env python3
"""
#exonware/xwapi/src/exonware/xwapi/facade.py
Facade pattern implementation for xwapi library (Engine-Agnostic).
Uses XWAction engine system for action execution - engine-agnostic pattern.
Delegates to engine-specific implementations for app creation and action registration.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.1
"""

from typing import Any, Optional, TYPE_CHECKING
# Engine-specific imports deferred - use TYPE_CHECKING for type hints only
if TYPE_CHECKING:
    from fastapi import FastAPI
else:
    # Runtime imports deferred - will use engine abstraction
    FastAPI = None
from exonware.xwapi.base import AAPIGenerator
from exonware.xwapi.config import XWAPIConfig
from exonware.xwapi.errors import OpenAPIGenerationError, FastAPICreationError
from exonware.xwapi.defs import OpenAPISpec
from exonware.xwapi.common.app import create_app


class XWAPI(AAPIGenerator):
    """
    Main facade class for xwapi library (engine-agnostic).
    Converts xwentity classes into web APIs with OpenAPI documentation.
    Uses XWAction engine system for action execution.
    """

    def __init__(
        self,
        entities: list[Any] = None,
        storage: Optional[Any] = None,
        auth: Optional[Any] = None,
        actions: Optional[list[Any]] = None,
        config: Optional[XWAPIConfig] = None,
        **kwargs,
    ):
        """
        Initialize XWAPI instance.
        Args:
            entities: List of entity classes to convert to API endpoints
            storage: Optional xwstorage instance for persistence
            auth: Optional xwauth instance for authentication
            actions: Optional list of xwaction-decorated functions to register as endpoints
            config: Optional XWAPIConfig instance
            **kwargs: Additional configuration options
        """
        self.entities = entities or []
        self.storage = storage
        self.auth = auth
        self.actions = actions or []
        # Merge kwargs into config
        if config:
            self.config = config
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
        else:
            self.config = XWAPIConfig(**kwargs)
        self._openapi_spec: Optional[OpenAPISpec] = None
        self._app: Optional[Any] = None  # Engine-agnostic app instance

    async def generate_openapi(self) -> OpenAPISpec:
        """
        Generate OpenAPI specification from entities and actions.
        Uses XWAction's OpenAPI generation capabilities.
        Returns:
            OpenAPI 3.1 specification dictionary
        Raises:
            OpenAPIGenerationError: If generation fails
        """
        try:
            # Start with base OpenAPI spec
            spec = {
                "openapi": "3.1.0",
                "info": {
                    "title": self.config.title,
                    "version": self.config.version,
                    "description": self.config.description or "",
                },
                "paths": {},
                "components": {
                    "schemas": {},
                    "securitySchemes": self.config.security_schemes or {},
                },
            }
            # Generate OpenAPI from XWAction actions
            from exonware.xwaction.core.openapi import openapi_generator
            for action in self.actions:
                if hasattr(action, 'xwaction'):
                    action_spec = action.xwaction.to_openapi()
                    # Merge action OpenAPI into main spec
                    if "paths" in action_spec:
                        spec["paths"].update(action_spec["paths"])
                    if "components" in action_spec:
                        if "schemas" in action_spec["components"]:
                            spec["components"]["schemas"].update(action_spec["components"]["schemas"])
            self._openapi_spec = spec
            return self._openapi_spec
        except Exception as e:
            raise OpenAPIGenerationError(f"Failed to generate OpenAPI spec: {e}") from e

    def create_app(self, engine: str = "fastapi") -> Any:  # Engine-agnostic return type
        """
        Create application using xwapi.create_app() (engine-agnostic).
        Registers all actions using XWAction engine system.
        Args:
            engine: Engine name (default: "fastapi")
        Returns:
            Application instance (engine-specific)
        Raises:
            FastAPICreationError: If creation fails
        """
        try:
            if not self._openapi_spec:
                # Generate OpenAPI spec if not already generated
                import asyncio
                self._openapi_spec = asyncio.run(self.generate_openapi())
            # Create app using xwapi factory (engine-agnostic)
            self._app = create_app(
                config=self.config,
                title=self.config.title,
                version=self.config.version,
                description=self.config.description,
                engine=engine,
            )
            # Register all actions using XWAction engines directly
            # Detect engine from app type
            app_type_name = type(self._app).__module__ + "." + type(self._app).__name__
            engine_name = None
            if "fastapi" in app_type_name.lower():
                engine_name = "fastapi"
            elif "flask" in app_type_name.lower():
                engine_name = "flask"
            if engine_name:
                # Get XWAction engine for this framework
                try:
                    from exonware.xwaction.engines import action_engine_registry
                    action_engine = action_engine_registry.get_engine(engine_name)
                    if action_engine:
                        # Setup engine with app
                        action_engine.setup({"app": self._app})
                        # Register all actions
                        for action in self.actions:
                            if hasattr(action, 'xwaction'):
                                xwaction = action.xwaction
                                # Get path from action metadata
                                path = getattr(xwaction, 'operationId', None) or action.__name__
                                path = f"/{path}"
                                # Determine HTTP method from action profile
                                method = "POST"  # Default
                                if hasattr(xwaction, 'profile'):
                                    profile = xwaction.profile
                                    if hasattr(profile, 'value'):
                                        if profile.value == "query":
                                            method = "GET"
                                        elif profile.value == "command":
                                            method = "POST"
                                # Register using XWAction engine directly
                                action_engine.register_action(xwaction, self._app, path, method)
                except ImportError:
                    # XWAction not available, skip action registration
                    pass
            return self._app
        except Exception as e:
            raise FastAPICreationError(f"Failed to create app: {e}") from e

    def start(self, host: str = "0.0.0.0", port: int = 8000, **kwargs) -> None:
        """
        Start the server (convenience method).
        Args:
            host: Host to bind to
            port: Port to bind to
            **kwargs: Additional server arguments
        """
        if not self._app:
            self.create_app()
        # Start server using uvicorn directly (FastAPI default)
        import uvicorn
        uvicorn.run(self._app, host=host, port=port, **kwargs)

    def stop(self) -> None:
        """Stop the server."""
        # Note: This is a placeholder - actual server stopping should be done via server instance
        # For facade, we'd need to track the server process/thread
        pass

    def restart(self) -> None:
        """Restart the server."""
        # Note: This is a placeholder - actual server restart should be done via server instance
        # For facade, we'd need to track the server process/thread
        pass
