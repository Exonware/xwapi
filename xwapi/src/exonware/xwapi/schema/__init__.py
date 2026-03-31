"""
Schema integration for xwapi.
Request/response validation and OpenAPI/GraphQL schema generation using xwschema.
"""

from .contracts import (
    IAPIRulesValidator,
    IAPISchemaGenerator,
    IGraphQLSchemaGenerator,
    IRequestValidator,
)
from .validator import APIRulesValidator, RequestValidator, ResponseValidator
from .generator import APISchemaGenerator
from .graphql import GraphQLSchemaGenerator
__all__ = [
    'IAPISchemaGenerator',
    'IGraphQLSchemaGenerator',
    'IRequestValidator',
    'IAPIRulesValidator',
    'RequestValidator',
    'ResponseValidator',
    'APIRulesValidator',
    'APISchemaGenerator',
    'GraphQLSchemaGenerator',
]
