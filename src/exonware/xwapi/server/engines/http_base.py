#exonware/xwapi/engines/http_base.py
"""
HTTP Protocol Base Engine
Base class for HTTP-based API server engines (REST, GraphQL, RPC over HTTP).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.7
"""

from typing import Any
from datetime import datetime
from .base import AApiServerEngineBase
from .contracts import ProtocolType
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


class AHttpServerEngineBase(AApiServerEngineBase):
    """
    Abstract Base Class for HTTP-based API Server Engines.
    Provides common functionality for HTTP engines (FastAPI, Flask, Django REST, etc.).
    """

    def __init__(self, name: str, protocol_type: ProtocolType | None = None):
        """
        Initialize HTTP engine base.
        Args:
            name: Engine name (e.g., 'fastapi', 'flask')
            protocol_type: Protocol type (default: HTTP_REST)
        """
        super().__init__(name)
        self._protocol_type = protocol_type or ProtocolType.HTTP_REST
    @property

    def protocol_type(self) -> ProtocolType:
        """Get protocol type (HTTP)."""
        return self._protocol_type
    @property

    def supports_admin_endpoints(self) -> bool:
        """HTTP engines support admin endpoints."""
        return True

    def register_action(self, app: Any, action: Any, 
                       route_info: dict[str, Any]) -> bool:
        """
        Register XWAction as HTTP endpoint.
        Args:
            app: HTTP framework app instance
            action: XWAction instance to register
            route_info: Must contain 'path' and 'method' keys
                Example: {'path': '/users', 'method': 'GET'}
        Returns:
            True if registration successful
        """
        path = route_info.get('path')
        method = route_info.get('method', 'POST')
        if not path:
            logger.error("HTTP route_info must contain 'path'")
            return False
        # Delegate to protocol-specific implementation
        return self._register_http_action(app, action, path, method)

    def _register_http_action(self, app: Any, action: Any, 
                             path: str, method: str) -> bool:
        """
        Protocol-specific HTTP action registration.
        Subclasses must implement this.
        Args:
            app: HTTP framework app instance
            action: XWAction instance
            path: Endpoint path
            method: HTTP method
        Returns:
            True if registration successful
        """
        raise NotImplementedError("Subclasses must implement _register_http_action")

    def generate_schema(self, app: Any, actions: list[Any], 
                       config: Any) -> dict[str, Any]:
        """
        Generate OpenAPI specification for HTTP engines.
        Args:
            app: HTTP framework app instance
            actions: List of registered XWAction instances
            config: XWAPI configuration
        Returns:
            OpenAPI 3.1 specification dictionary
        """
        return self.generate_openapi(app, actions, config)

    def generate_openapi(self, app: Any, actions: list[Any], 
                        config: Any) -> dict[str, Any]:
        """
        Generate OpenAPI specification.
        This serves as the DEFAULT implementation. Derived classes (like FastAPI)
        can override this if the framework provides its own generator, or call 
        super().generate_openapi() as a fallback.
        Args:
            app: HTTP framework app instance
            actions: List of registered XWAction instances
            config: XWAPI configuration
        Returns:
            OpenAPI 3.1 specification dictionary
        """
        # 1. Prepare Metadata
        title = getattr(config, 'title', 'API') or 'API'
        version = getattr(config, 'version', '1.0.0') or '1.0.0'
        description = getattr(config, 'description', '') or ''
        # 2. Build Skeleton (lazy-import __version__ to avoid circular import)
        from exonware.xwapi.version import __version__
        spec = {
            "openapi": "3.1.0",
            "info": {
                "title": title,
                "version": version,
                "description": description,
                "x-xwapi-version": __version__,
                "x-generated-at": datetime.utcnow().isoformat(),
            },
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": getattr(config, 'security_schemes', {}) or {},
            },
        }
        # Apply OpenAPI tags if configured
        if hasattr(config, 'openapi_tags') and config.openapi_tags:
            spec["tags"] = config.openapi_tags
        # 3. Aggregate Actions (Generic logic for all engines)
        for action in actions:
            # Check if action supports OpenAPI export
            if hasattr(action, 'to_openapi'):
                action_spec = action.to_openapi()
                # Merge Paths
                if "paths" in action_spec:
                    spec["paths"].update(action_spec["paths"])
                # Merge Components/Schemas
                if "components" in action_spec and "schemas" in action_spec["components"]:
                    spec["components"]["schemas"].update(
                        action_spec["components"]["schemas"]
                    )
        return spec

    def start_server(self, app: Any, host: str = "0.0.0.0", 
                    port: int = 8000, **kwargs) -> None:
        """
        Start HTTP server.
        Args:
            app: HTTP framework app instance
            host: Host to bind to
            port: Port to bind to
            **kwargs: Additional HTTP server options
        """
        raise NotImplementedError("Subclasses must implement start_server")
