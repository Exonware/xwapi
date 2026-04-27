#exonware/xwapi/src/exonware/xwapi/base.py
"""
Abstract bases for API servers, agents, generators, and service providers.

Spans both *publishing* (servers, OpenAPI generators) and *consuming* (agents) sides of
exposable actions.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.12
"""

from typing import Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from exonware.xwaction.base import AActionsProvider
from exonware.xwapi.contracts import (
    IAPIEndpoint,
    IAPIGenerator,
    IOAuth2Provider,
    IApiServer,
    IApiAgent,
    IApiServicesProvider,
    HTTPMethod,
    SecurityType,
)


class AApiServicesProvider(IApiServicesProvider, AActionsProvider, ABC):
    """
    Abstract base for API-level providers that expose @XWAction commands.
    Extends AActionsProvider (xwaction); used by command providers (xwbots).
    """

    pass


class AAPIEndpoint(ABC, IAPIEndpoint):
    """Abstract base class for API endpoint configuration implementing IAPIEndpoint interface."""

    def __init__(
        self,
        endpoint_id: str,
        path: str,
        method: HTTPMethod,
        entity_type: str,
        action_name: str | None = None,
    ):
        self.endpoint_id = endpoint_id
        self.path = path
        self.method = method
        self.entity_type = entity_type
        self.action_name = action_name

    def get_path(self) -> str:
        """Get endpoint path."""
        return self.path

    def get_method(self) -> HTTPMethod:
        """Get HTTP method."""
        return self.method

    def get_entity_type(self) -> str:
        """Get entity type name."""
        return self.entity_type


class AAPIGenerator(ABC, IAPIGenerator):
    """Abstract base for turning actions/entities into an OpenAPI-backed app (publisher side)."""
    @abstractmethod

    async def generate_openapi(self) -> dict[str, Any]:
        """Generate OpenAPI specification."""
        pass
    @abstractmethod

    def create_app(self):
        """Create application instance (engine-specific)."""
        pass


class AOAuth2Provider(ABC, IOAuth2Provider):
    """Abstract base class for OAuth 2.0 provider implementing IOAuth2Provider interface."""

    def __init__(
        self,
        provider_name: str,
        authorization_url: str,
        token_url: str,
        userinfo_url: str | None = None,
    ):
        self.provider_name = provider_name
        self.authorization_url = authorization_url
        self.token_url = token_url
        self.userinfo_url = userinfo_url

    def get_authorization_url(self) -> str:
        """Get authorization URL."""
        return self.authorization_url

    def get_token_url(self) -> str:
        """Get token URL."""
        return self.token_url

    def get_userinfo_url(self) -> str | None:
        """Get userinfo URL."""
        return self.userinfo_url


class AApiServer(ABC, IApiServer):
    """Abstract base class for API server implementing IApiServer interface."""

    def __init__(self):
        """Initialize AApiServer with logging."""
        from exonware.xwsystem import get_logger
        self.logger = get_logger(self.__class__.__name__)
        self._is_running = False
        self._start_time: datetime | None = None
        self._services_running = False
        # Track flushable handlers for shutdown
        self._flushable_handlers: list[Any] = []
        # Call on_init hook
        self.on_init()

    def on_init(self) -> None:
        """
        Lifecycle hook: Called during initialization.
        Subclasses can override this to perform initialization tasks.
        This is called automatically in __init__.
        """
        pass

    def pre_server_start(self) -> None:
        """
        Lifecycle hook: Called before server starts (protocol-agnostic).
        For HTTP engines, this is equivalent to pre_http_start().
        For other protocols (gRPC, WebSocket, etc.), this is the generic hook.
        Subclasses can override this to perform tasks before the server
        starts (e.g., validate configuration, check dependencies).
        """
        pass

    def post_server_start(self) -> None:
        """
        Lifecycle hook: Called after server starts (protocol-agnostic).
        For HTTP engines, this is equivalent to post_http_start().
        For other protocols (gRPC, WebSocket, etc.), this is the generic hook.
        Subclasses can override this to perform tasks after the server
        has started (e.g., register routes, warm up caches).
        """
        pass

    def pre_http_start(self) -> None:
        """
        Lifecycle hook: Called before HTTP server starts (HTTP-specific).
        For backward compatibility. Delegates to pre_server_start().
        Subclasses can override this for HTTP-specific logic.
        """
        self.pre_server_start()

    def post_http_start(self) -> None:
        """
        Lifecycle hook: Called after HTTP server starts (HTTP-specific).
        For backward compatibility. Delegates to post_server_start().
        Subclasses can override this for HTTP-specific logic.
        """
        self.post_server_start()

    def pre_services_start(self) -> None:
        """
        Lifecycle hook: Called before domain services start.
        Subclasses can override this to perform tasks before domain services
        start (e.g., load data, initialize connections).
        """
        pass

    def post_services_start(self) -> None:
        """
        Lifecycle hook: Called after domain services start.
        Subclasses can override this to perform tasks after domain services
        have started (e.g., verify services are ready, start background tasks).
        """
        pass

    def pre_stop(self) -> None:
        """
        Lifecycle hook: Called before stopping.
        Subclasses can override this to perform cleanup tasks before stopping
        (e.g., save state, notify clients).
        """
        pass

    def post_stop(self) -> None:
        """
        Lifecycle hook: Called after stopping.
        Subclasses can override this to perform final cleanup tasks after
        stopping (e.g., close connections, cleanup resources).
        """
        pass

    def register_flushable(self, handler: Any) -> None:
        """
        Register a flushable handler for shutdown cleanup.
        Handlers must implement flush() and optionally close() methods.
        These will be called during shutdown to ensure all logs/data are flushed.
        Args:
            handler: Object with flush() and optionally close() methods
        """
        if handler not in self._flushable_handlers:
            self._flushable_handlers.append(handler)
            self.logger.debug(f"Registered flushable handler: {type(handler).__name__}")

    def unregister_flushable(self, handler: Any) -> None:
        """
        Unregister a flushable handler.
        Args:
            handler: Handler to unregister
        """
        if handler in self._flushable_handlers:
            self._flushable_handlers.remove(handler)
            self.logger.debug(f"Unregistered flushable handler: {type(handler).__name__}")
    @abstractmethod

    def start(self, host: str = "0.0.0.0", port: int = 8000, **kwargs) -> None:
        """Start the API server services."""
        pass
    @abstractmethod

    def stop(self) -> None:
        """Stop the API server services."""
        pass

    def restart(self, host: str = "0.0.0.0", port: int = 8000, **kwargs) -> None:
        """Restart the API server."""
        self.logger.info("Restarting server...")
        self.stop()
        self.start(host=host, port=port, **kwargs)
        self.logger.info("Server restarted")

    def status(self) -> dict[str, Any]:
        """
        Get server status.
        Returns:
            Dictionary with server status information
        """
        uptime = None
        if self._start_time:
            from datetime import datetime
            uptime = (datetime.now() - self._start_time).total_seconds()
        return {
            "status": "running" if self._is_running else "stopped",
            "is_running": self._is_running,
            "services_running": getattr(self, '_services_running', False),
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "uptime_seconds": uptime,
        }

    def health(self) -> dict[str, Any]:
        """
        Get server health check.
        Returns:
            Dictionary with health check information
        """
        from datetime import datetime
        return {
            "status": "healthy" if self._is_running else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "is_running": self._is_running,
        }

    def log(self, level: str = "INFO", message: str = "") -> None:
        """
        Log a message.
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)
    @property

    def is_running(self) -> bool:
        """Check if server is running."""
        return self._is_running

    def pre_register_action(self, action: Any) -> Any:
        """
        Lifecycle hook: Called before registering an action.
        Subclasses can override this to transform actions before registration
        (e.g., inject authorizers, add middleware, modify metadata).
        Args:
            action: Action to be registered
        Returns:
            Transformed action (or original if no transformation needed)
        """
        return action

    def post_register_action(self, action: Any, route_info: dict[str, Any]) -> None:
        """
        Lifecycle hook: Called after registering an action.
        Subclasses can override this to perform tasks after action registration
        (e.g., log registration, update metrics, validate route).
        Args:
            action: Registered action
            route_info: Dictionary with route information (path, method, etc.)
        """
        pass


class AApiAgent(ABC, IApiAgent):
    """Abstract base class for API agent implementing IApiAgent interface."""

    def __init__(self, name: str | None = None):
        """
        Initialize API agent.
        Args:
            name: Optional name for this agent
        """
        self._name = name or self.__class__.__name__
        self._actions: list[Any] = []
    @property

    def name(self) -> str:
        """Get agent name."""
        return self._name
    @abstractmethod

    def get_actions(self) -> list[Any]:
        """
        Get list of XWAction instances provided by this agent.
        Subclasses must implement this to return their actions.
        Returns:
            List of XWAction instances or decorated functions
        """
        pass

    def register_to_server(self, server: Any, path_prefix: str = "") -> int:
        """
        Register all actions from this agent to an ApiServer.
        Args:
            server: ApiServer instance to register actions to
            path_prefix: Optional path prefix for all actions
        Returns:
            Number of successfully registered actions
        """
        actions = self.get_actions()
        if not actions:
            return 0
        # Use server's register_actions method
        if hasattr(server, 'register_actions'):
            return server.register_actions(actions, path_prefix=path_prefix)
        elif hasattr(server, 'register_action'):
            # Fallback: register one by one
            registered = 0
            for action in actions:
                if server.register_action(action, path=path_prefix):
                    registered += 1
            return registered
        else:
            raise TypeError(f"Server must have register_actions or register_action method, got {type(server)}")
