#exonware/xwapi/src/exonware/xwapi/contracts.py
"""
Contracts (interfaces and enums) for xwapi library.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.1
"""

from typing import Protocol, runtime_checkable, Any
from enum import Enum
from exonware.xwaction.contracts import IActionsProvider


class HTTPMethod(str, Enum):
    """HTTP method enumeration."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class SecurityType(str, Enum):
    """Security type enumeration."""
    OAUTH2 = "oauth2"
    API_KEY = "apiKey"
    BEARER = "bearer"
    BASIC = "basic"
@runtime_checkable

class IAPIEndpoint(Protocol):
    """Interface for API endpoint configuration."""

    def get_path(self) -> str:
        """Get endpoint path."""
        ...

    def get_method(self) -> HTTPMethod:
        """Get HTTP method."""
        ...

    def get_entity_type(self) -> str:
        """Get entity type name."""
        ...
@runtime_checkable

class IAPIGenerator(Protocol):
    """Interface for API generator."""

    async def generate_openapi(self) -> dict:
        """Generate OpenAPI specification."""
        ...

    def create_app(self):
        """Create application instance (engine-specific)."""
        ...
@runtime_checkable

class IOAuth2Provider(Protocol):
    """Interface for OAuth 2.0 provider."""

    def get_authorization_url(self) -> str:
        """Get authorization URL."""
        ...

    def get_token_url(self) -> str:
        """Get token URL."""
        ...

    def get_userinfo_url(self) -> str:
        """Get userinfo URL."""
        ...
@runtime_checkable

class IApiAgent(Protocol):
    """Interface for API agent that provides XWAction functions."""

    def get_actions(self) -> list[Any]:
        """Get list of XWAction instances provided by this agent."""
        ...

    def register_to_server(self, server: Any) -> int:
        """
        Register all actions from this agent to an ApiServer.
        Args:
            server: ApiServer instance to register actions to
        Returns:
            Number of successfully registered actions
        """
        ...
@runtime_checkable

class IApiServer(Protocol):
    """Interface for API server operations."""

    def start(self, host: str = "0.0.0.0", port: int = 8000, **kwargs) -> None:
        """Start the API server."""
        ...

    def stop(self) -> None:
        """Stop the API server."""
        ...

    def restart(self) -> None:
        """Restart the API server."""
        ...


@runtime_checkable
class IApiServicesProvider(IActionsProvider, Protocol):
    """
    Interface for API-level providers that expose @XWAction commands.
    Extends IActionsProvider (xwaction); used by command providers (xwbots).
    """
    ...
