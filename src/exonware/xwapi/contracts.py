#exonware/xwapi/src/exonware/xwapi/contracts.py
"""
Contracts for servers and clients built around *exposable actions* and API surfaces.

Defines protocols for endpoints, generators, agents, servers, providers, and entity stores so
publishers (``XWApiServer``) and consumers (``XWApiAgent``) share the same vocabulary.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.4
"""

from typing import Protocol, runtime_checkable, Any
from enum import Enum
from exonware.xwaction.contracts import IActionsProvider
from exonware.xwsystem.security.contracts import AuthContext


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
class IEntityCrudStore(Protocol):
    """Interface for entity CRUD storage backends."""

    async def list_items(self, collection: str) -> list[dict[str, Any]]:
        """List all items in a collection."""
        ...

    async def get_item(self, collection: str, entity_id: str) -> dict[str, Any] | None:
        """Get a single item by ID."""
        ...

    async def put_item(self, collection: str, entity_id: str, item: dict[str, Any]) -> None:
        """Create or replace an item."""
        ...

    async def delete_item(self, collection: str, entity_id: str) -> bool:
        """Delete an item and return whether it existed."""
        ...


@runtime_checkable
class IAuthProvider(Protocol):
    """Provider contract for API token lifecycle using auth library backends."""

    async def issue_api_token(
        self,
        *,
        subject_id: str,
        name: str,
        scopes: list[str],
        expires_in_seconds: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ...

    async def verify_api_token(self, token: str) -> dict[str, Any] | None:
        ...

    async def revoke_api_token(self, token_id: str) -> bool:
        ...

    async def resolve_auth_context(self, token: str) -> AuthContext | None:
        """
        Resolve bearer token into normalized context for request middleware.
        Backends that do not support bearer sessions can return None.
        """
        ...


@runtime_checkable
class IStorageProvider(Protocol):
    """Provider contract for persistence backends (xwstorage-compatible)."""

    async def read(self, key: str) -> Any:
        ...

    async def write(self, key: str, value: Any) -> None:
        ...

    async def delete(self, key: str) -> None:
        ...

    async def exists(self, key: str) -> bool:
        ...


@runtime_checkable
class IPaymentProvider(Protocol):
    """Provider contract for recharge/billing operations."""

    async def create_recharge(
        self,
        *,
        subject_id: str,
        amount: float,
        currency: str = "USD",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ...

    async def get_balance(self, subject_id: str) -> float:
        ...

    async def consume_credits(
        self,
        *,
        subject_id: str,
        amount: float,
        metadata: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        ...


@runtime_checkable
class IApiServicesProvider(IActionsProvider, Protocol):
    """
    Interface for API-level providers that expose @XWAction commands.
    Extends IActionsProvider (xwaction); used by command providers (xwbots).
    """
    ...
