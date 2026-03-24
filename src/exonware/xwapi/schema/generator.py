"""
OpenAPI schema generation for xwapi.
Uses xwschema engine for schema generation and format conversion.
"""

from typing import Any, Optional
from exonware.xwsystem import get_logger
from exonware.xwschema import XWSchema
from exonware.xwschema.engine import XWSchemaEngine
from exonware.xwschema.defs import SchemaFormat
from .contracts import IAPISchemaGenerator
from ..errors import XWAPIError
logger = get_logger(__name__)


class APISchemaGenerator(IAPISchemaGenerator):
    """OpenAPI schema generator using xwschema."""

    def __init__(self):
        self._engine = XWSchemaEngine()
        logger.debug("APISchemaGenerator initialized")

    async def generate_openapi_schema(
        self,
        entities: list[Any],
        **opts
    ) -> dict[str, Any]:
        try:
            schemas = {}
            for entity in entities:
                if hasattr(entity, 'to_dict'):
                    entity_data = entity.to_dict()
                elif hasattr(entity, '__dict__'):
                    entity_data = entity.__dict__
                else:
                    entity_data = dict(entity) if hasattr(entity, '__iter__') else {'value': entity}
                json_schema = await self._engine.generate_schema(entity_data)
                openapi_schema = await self._engine.convert_schema(
                    json_schema,
                    SchemaFormat.JSON_SCHEMA,
                    SchemaFormat.OPENAPI
                )
                entity_name = type(entity).__name__ if hasattr(entity, '__class__') else 'Entity'
                schemas[entity_name] = json_schema
            openapi_doc = {
                'openapi': '3.0.0',
                'info': {
                    'title': opts.get('title', 'API'),
                    'version': opts.get('version', '1.0.0')
                },
                'components': {'schemas': schemas}
            }
            logger.debug(f"OpenAPI schema generated for {len(entities)} entities")
            return openapi_doc
        except Exception as e:
            logger.error(f"Failed to generate OpenAPI schema: {e}")
            raise XWAPIError(f"Failed to generate OpenAPI schema: {str(e)}") from e
