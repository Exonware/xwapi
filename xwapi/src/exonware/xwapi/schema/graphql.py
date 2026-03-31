"""
GraphQL schema generation for xwapi.
Uses xwschema engine for schema generation and format conversion.
"""

from typing import Any, Optional
from exonware.xwsystem import get_logger
from exonware.xwschema.engine import XWSchemaEngine
from exonware.xwschema.defs import SchemaFormat
from .contracts import IGraphQLSchemaGenerator
from ..errors import XWAPIError
logger = get_logger(__name__)


class GraphQLSchemaGenerator(IGraphQLSchemaGenerator):
    """GraphQL schema generator using xwschema."""

    def __init__(self):
        self._engine = XWSchemaEngine()
        logger.debug("GraphQLSchemaGenerator initialized")

    async def generate_graphql_schema(
        self,
        entities: list[Any],
        **opts
    ) -> str:
        try:
            types = []
            for entity in entities:
                if hasattr(entity, 'to_dict'):
                    entity_data = entity.to_dict()
                elif hasattr(entity, '__dict__'):
                    entity_data = entity.__dict__
                else:
                    entity_data = dict(entity) if hasattr(entity, '__iter__') else {'value': entity}
                json_schema = await self._engine.generate_schema(entity_data)
                graphql_schema = await self._engine.convert_schema(
                    json_schema,
                    SchemaFormat.JSON_SCHEMA,
                    SchemaFormat.GRAPHQL
                )
                type_name = type(entity).__name__ if hasattr(entity, '__class__') else 'Entity'
                type_def = self._generate_graphql_type(type_name, graphql_schema)
                types.append(type_def)
            schema_sdl = "\n\n".join(types)
            if 'type Query' not in schema_sdl:
                query_fields = "\n  ".join([f"{t.split()[1]}: {t.split()[1]}" for t in types if t.startswith('type ')])
                if query_fields:
                    schema_sdl += f"\n\ntype Query {{\n  {query_fields}\n}}"
            logger.debug(f"GraphQL schema generated for {len(entities)} entities")
            return schema_sdl
        except Exception as e:
            logger.error(f"Failed to generate GraphQL schema: {e}")
            raise XWAPIError(f"Failed to generate GraphQL schema: {str(e)}") from e

    def _generate_graphql_type(self, type_name: str, graphql_schema: dict[str, Any]) -> str:
        fields = []
        if 'types' in graphql_schema:
            for type_def in graphql_schema['types'].values():
                if 'fields' in type_def:
                    for field_name, field_def in type_def['fields'].items():
                        field_type = field_def.get('type', 'String')
                        required = '!' if field_def.get('required', False) else ''
                        fields.append(f"  {field_name}: {field_type}{required}")
        if not fields:
            fields.append("  id: ID!")
        return f"type {type_name} {{\n" + "\n".join(fields) + "\n}"
