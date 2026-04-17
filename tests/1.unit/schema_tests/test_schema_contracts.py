#exonware/xwapi/tests/1.unit/schema_tests/test_schema_contracts.py
"""
Unit tests for schema contracts (IAPISchemaGenerator, IGraphQLSchemaGenerator, IRequestValidator).
Company: eXonware.com
"""

from __future__ import annotations
import pytest


@pytest.mark.xwapi_unit
class TestSchemaContracts:
    """Tests that schema contracts are runtime_checkable."""

    def test_api_schema_generator_protocol(self):
        from exonware.xwapi.schema.contracts import IAPISchemaGenerator

        class FakeGen:
            async def generate_openapi_schema(self, entities, **opts):
                return {}

        assert isinstance(FakeGen(), IAPISchemaGenerator)

    def test_graphql_schema_generator_protocol(self):
        from exonware.xwapi.schema.contracts import IGraphQLSchemaGenerator

        class FakeGen:
            async def generate_graphql_schema(self, entities, **opts):
                return ""

        assert isinstance(FakeGen(), IGraphQLSchemaGenerator)

    def test_request_validator_protocol(self):
        from exonware.xwapi.schema.contracts import IRequestValidator

        class FakeValidator:
            async def validate_request(self, request_data, schema, endpoint, **opts):
                return {"valid": True, "errors": []}
            async def validate_response(self, response_data, schema, endpoint, **opts):
                return {"valid": True, "errors": []}

        assert isinstance(FakeValidator(), IRequestValidator)

    def test_api_rules_validator_alias(self):
        from exonware.xwapi.schema.contracts import IAPIRulesValidator, IRequestValidator
        assert IAPIRulesValidator is IRequestValidator
