#exonware/xwapi/engines/graphql.py
"""
GraphQL Server Engine Implementation
GraphQL-based API server engine using Strawberry.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.9
"""

from typing import Any

from collections.abc import Callable
import inspect
from .http_base import AHttpServerEngineBase
from .contracts import ProtocolType
from exonware.xwapi.config import XWAPIConfig
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


class GraphQLServerEngine(AHttpServerEngineBase):
    """
    GraphQL Server Engine (Strawberry)
    Implements API server using Strawberry GraphQL framework.
    GraphQL runs over HTTP but uses a different query paradigm.
    """

    def __init__(self):
        """Initialize GraphQL server engine."""
        super().__init__("graphql", protocol_type=ProtocolType.HTTP_GRAPHQL)
        self._app: Any | None = None
        self._schema: Any | None = None
        self._queries: dict[str, Any] = {}
        self._mutations: dict[str, Any] = {}
        self._type_cache: dict[str, Any] = {}
    @property

    def protocol_type(self) -> ProtocolType:
        """Get protocol type (HTTP_GRAPHQL)."""
        return ProtocolType.HTTP_GRAPHQL

    def create_app(self, config: XWAPIConfig) -> Any:
        """
        Create GraphQL application.
        Args:
            config: XWAPI configuration
        Returns:
            FastAPI app (GraphQL router added in start_server)
        """
        try:
            from fastapi import FastAPI
            import strawberry
            from strawberry.fastapi import GraphQLRouter
        except ImportError:
            raise ImportError(
                "strawberry-graphql and fastapi are required for GraphQLServerEngine. "
                "Install with: pip install strawberry-graphql[fastapi]"
            )
        # Create FastAPI app (GraphQL runs over HTTP)
        app = FastAPI(
            title=config.title,
            version=config.version,
            description=config.description or "",
        )
        # Apply OpenAPI tags if configured
        if config.openapi_tags:
            app.openapi_tags = config.openapi_tags
            logger.debug(f"Applied {len(config.openapi_tags)} OpenAPI tags")
        self._app = app
        return app

    def _register_http_action(self, app: Any, action: Any, 
                             path: str, method: str) -> bool:
        """
        Register XWAction as GraphQL query or mutation.
        Args:
            app: FastAPI app instance
            action: XWAction instance
            path: Ignored for GraphQL
            method: Ignored for GraphQL
        Returns:
            True if registration successful
        """
        try:
            import strawberry
        except ImportError:
            logger.warning("strawberry not available, cannot register GraphQL action")
            return False
        # Get action function
        func = getattr(action, 'func', None)
        if not func and hasattr(action, '__call__'):
            func = action
        if not func:
            logger.error(f"Cannot register GraphQL action: no function found")
            return False
        # Determine if query or mutation
        is_mutation = False
        if hasattr(action, 'profile'):
            profile = getattr(action, 'profile', None)
            if hasattr(profile, 'value'):
                is_mutation = profile.value in ['command', 'task', 'workflow']
        # Override based on XWAction readonly property if available
        if hasattr(action, 'readonly') and action.readonly:
            is_mutation = False
        # Generate unique field name
        field_name = getattr(action, 'api_name', func.__name__)
        # Prepare arguments types
        in_types = getattr(action, 'in_types', {}) or {}
        out_types = getattr(action, 'out_types', {}) or {}
        # Generate Resolver
        # We need to wrap the action call to handle async/sync and args
        async def resolver(**kwargs) -> Any:
            # Here we would invoke the action
            # Note: XWAction instances are callable
            if inspect.iscoroutinefunction(action.__call__):
                return await action(**kwargs)
            else:
                return action(**kwargs)
        # Set name and annotations for the resolver to help Strawberry
        resolver.__name__ = field_name
        # Build argument annotations for the resolver
        # This is crucial for Strawberry to infer arguments
        annotations = {}
        for arg_name, schema in in_types.items():
            # Convert XWSchema to Strawberry type
            field_type = self._convert_schema_to_strawberry(schema, f"{field_name}_{arg_name}")
            annotations[arg_name] = field_type
        # Add return type annotation
        # Assuming single return value or using a specific key from out_types
        # If out_types has multiple keys, we return an object (ObjectType)
        return_type = Any
        if out_types:
            if len(out_types) == 1 and 'return' in out_types:
                 return_type = self._convert_schema_to_strawberry(out_types['return'], f"{field_name}_Response")
            else:
                # Composite return type
                return_type = self._create_composite_type(out_types, f"{field_name}_Response")
        else:
             # Try to infer from function signature if out_types missing
             sig = inspect.signature(func)
             if sig.return_annotation != inspect.Signature.empty:
                 # TODO: map python type to strawberry type if possible
                 pass
        annotations['return'] = return_type
        resolver.__annotations__ = annotations
        # Create Field
        field = strawberry.field(resolver=resolver)
        # Register
        if is_mutation:
            self._mutations[field_name] = field
        else:
            self._queries[field_name] = field
        logger.debug(f"Registered GraphQL {'mutation' if is_mutation else 'query'}: {field_name}")
        return True

    def _convert_schema_to_strawberry(self, schema: Any, name: str) -> type:
        """
        Convert XWSchema (or dict) to Strawberry type.
        """
        import strawberry
        # Check cache
        if name in self._type_cache:
            return self._type_cache[name]
        # Extract dict from XWSchema if necessary
        schema_dict = schema
        if hasattr(schema, 'definition'):
             schema_dict = schema.definition
        elif hasattr(schema, 'schema'):
             schema_dict = schema.schema
        if not isinstance(schema_dict, dict):
            # Fallback for simple types passed as classes or nothing
            return str 
        schema_type = schema_dict.get('type', 'string')
        if schema_type == 'string':
            return str
        elif schema_type == 'integer':
            return int
        elif schema_type == 'number':
            return float
        elif schema_type == 'boolean':
            return bool
        elif schema_type == 'array':
            # Handle array
            item_schema = schema_dict.get('items', {})
            item_type = self._convert_schema_to_strawberry(item_schema, f"{name}_Item")
            return list[item_type]
        elif schema_type == 'object':
            # Handle object - create dynamic Strawberry class
            props = schema_dict.get('properties', {})
            fields = {}
            for prop_name, prop_schema in props.items():
                prop_type = self._convert_schema_to_strawberry(prop_schema, f"{name}_{prop_name}")
                # Handle required
                required = prop_name in schema_dict.get('required', [])
                if not required:
                    prop_type = prop_type | None
                fields[prop_name] = prop_type
            # Use strawberry.tools.create_type (if available) or dynamic class creation
            # Since create_type is simpler:
            new_type = strawberry.tools.create_type(name, fields)
            self._type_cache[name] = new_type
            return new_type
        return str # Default fallback

    def _create_composite_type(self, types: dict[str, Any], name: str) -> type:
        """Create a Strawberry type from multiple output schemas."""
        import strawberry
        if name in self._type_cache:
            return self._type_cache[name]
        fields = {}
        for prop_name, schema in types.items():
             prop_type = self._convert_schema_to_strawberry(schema, f"{name}_{prop_name}")
             fields[prop_name] = prop_type
        new_type = strawberry.tools.create_type(name, fields)
        self._type_cache[name] = new_type
        return new_type

    def generate_openapi(self, app: Any, actions: list[Any], 
                        config: XWAPIConfig) -> dict[str, Any]:
        """
        Generate OpenAPI specification for GraphQL.
        """
        # (Preserved existing logic but simplified)
        if hasattr(app, 'openapi'):
            spec = app.openapi()
        else:
            spec = {
                "openapi": "3.1.0",
                "info": {
                    "title": config.title,
                    "version": config.version,
                    "description": config.description or "",
                },
                "paths": {},
            }
        spec["paths"]["/graphql"] = {
            "post": {
                "summary": "GraphQL endpoint",
                "description": "Execute GraphQL queries and mutations",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"},
                                    "variables": {"type": "object"},
                                    "operationName": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "GraphQL response",
                    }
                }
            }
        }
        return spec

    def start_server(self, app: Any, host: str = "0.0.0.0", 
                    port: int = 8000, **kwargs) -> None:
        """
        Start GraphQL server.
        Constructs the Schema and Router here before starting.
        """
        try:
            import uvicorn
            import strawberry
            from strawberry.fastapi import GraphQLRouter
            from strawberry.tools import create_type
        except ImportError:
            raise ImportError("Required packages missing")
        # 1. Build Query and Mutation types
        Query = None
        if self._queries:
            # We map the fields dict to annotations for create_type?
            # strawberry.tools.create_type takes 'fields' dict mapping name -> type
            # But we have strawberry.field objects.
            # create_type creates a class. We need to attach fields to it.
            # Alternative: Dynamic class creation
            # class Query: pass
            # for name, field in self._queries.items():
            #     setattr(Query, name, field)
            # Query = strawberry.type(Query)
            # This works better than create_type for fields with resolvers
            Query = type("Query", (), self._queries)
            Query = strawberry.type(Query)
        else:
            # Empty query required
            @strawberry.type
            class Query:
                @strawberry.field
                def _dummy(self) -> str: return "ping"
        Mutation = None
        if self._mutations:
            Mutation = type("Mutation", (), self._mutations)
            Mutation = strawberry.type(Mutation)
        # 2. Create Schema
        self._schema = strawberry.Schema(query=Query, mutation=Mutation)
        # 3. Create Router and include in app
        graphql_router = GraphQLRouter(self._schema)
        app.include_router(graphql_router, prefix="/graphql")
        # 4. Start Server
        uvicorn_kwargs = {
            "host": host,
            "port": port,
            "log_level": kwargs.pop("log_level", "info"),
            **kwargs
        }
        logger.info(f"Starting GraphQL server on {host}:{port}")
        logger.info(f"GraphQL endpoint: http://{host}:{port}/graphql")
        uvicorn.run(app, **uvicorn_kwargs)

    def stop_server(self, app: Any) -> None:
        """Stop GraphQL server."""
        logger.info("Stopping GraphQL server")
