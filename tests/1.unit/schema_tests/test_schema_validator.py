#exonware/xwapi/tests/1.unit/schema_tests/test_schema_validator.py
"""
Unit tests for RequestValidator (API request/response validation via xwschema).
Company: eXonware.com
"""

from __future__ import annotations
import pytest


@pytest.mark.xwapi_unit
class TestRequestValidator:
    """Tests for RequestValidator."""

    @pytest.fixture
    def validator(self):
        from exonware.xwapi.schema.validator import RequestValidator
        return RequestValidator()

    @pytest.mark.asyncio
    async def test_validate_request_returns_dict(self, validator):
        result = await validator.validate_request(
            request_data={"name": "test"},
            schema={"type": "object"},
            endpoint="/test",
        )
        assert isinstance(result, dict)
        assert "valid" in result
        assert "errors" in result
        assert result["endpoint"] == "/test"
        assert result["type"] == "request"

    @pytest.mark.asyncio
    async def test_validate_response_returns_dict(self, validator):
        result = await validator.validate_response(
            response_data={"id": 1},
            schema={"type": "object"},
            endpoint="/test",
        )
        assert isinstance(result, dict)
        assert result["type"] == "response"

    @pytest.mark.asyncio
    async def test_validate_request_handles_error(self, validator):
        # Pass something that might cause validation error
        result = await validator.validate_request(
            request_data=None,
            schema=None,
            endpoint="/broken",
        )
        assert isinstance(result, dict)
        assert "errors" in result

    def test_aliases(self):
        from exonware.xwapi.schema.validator import (
            ResponseValidator,
            APIRulesValidator,
            RequestValidator,
        )
        assert ResponseValidator is RequestValidator
        assert APIRulesValidator is RequestValidator
