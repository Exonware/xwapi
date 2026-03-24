"""
Schema integration contracts for xwapi.
Company: eXonware.com
"""

from typing import Any, Optional, Protocol, runtime_checkable
@runtime_checkable


class IAPISchemaGenerator(Protocol):
    """Interface for generating OpenAPI schemas from entities."""

    async def generate_openapi_schema(
        self,
        entities: list[Any],
        **opts
    ) -> dict[str, Any]:
        """Generate OpenAPI schema from entities."""
        ...
@runtime_checkable


class IGraphQLSchemaGenerator(Protocol):
    """Interface for generating GraphQL schemas from entities."""

    async def generate_graphql_schema(
        self,
        entities: list[Any],
        **opts
    ) -> str:
        """Generate GraphQL schema (SDL) from entities."""
        ...
@runtime_checkable


class IRequestValidator(Protocol):
    """Interface for API request/response validation using schemas."""

    async def validate_request(
        self,
        request_data: Any,
        schema: dict[str, Any],
        endpoint: str,
        **opts
    ) -> dict[str, Any]:
        """Validate API request against schema."""
        ...

    async def validate_response(
        self,
        response_data: Any,
        schema: dict[str, Any],
        endpoint: str,
        **opts
    ) -> dict[str, Any]:
        """Validate API response against schema."""
        ...
# Alias: API rules validator is the same contract as request validator
IAPIRulesValidator = IRequestValidator
