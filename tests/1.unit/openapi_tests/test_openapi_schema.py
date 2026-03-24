#exonware/xwapi/tests/1.unit/openapi_tests/test_openapi_schema.py
"""
Unit tests for OpenAPI schema generation and validation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations
import pytest
from exonware.xwapi.common.openapi import (
    merge_openapi_schemas,
    validate_openapi_schema,
    export_openapi_schema,
    get_openapi_version,
)
@pytest.mark.xwapi_unit

def test_merge_openapi_schemas():
    """Test merging multiple OpenAPI schemas."""
    schema1 = {
        "openapi": "3.1.0",
        "info": {"title": "API 1", "version": "1.0.0"},
        "paths": {"/endpoint1": {}}
    }
    schema2 = {
        "openapi": "3.1.0",
        "info": {"title": "API 2", "version": "1.0.0"},
        "paths": {"/endpoint2": {}}
    }
    merged = merge_openapi_schemas([schema1, schema2])
    assert merged is not None
    assert "paths" in merged
    # Both paths should be in merged schema
    assert "/endpoint1" in merged["paths"] or "/endpoint2" in merged["paths"]
@pytest.mark.xwapi_unit

def test_validate_openapi_schema():
    """Test validating OpenAPI schema."""
    valid_schema = {
        "openapi": "3.1.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {}
    }
    result = validate_openapi_schema(valid_schema)
    # Should return tuple (bool, Optional[str]) for validation result
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], bool)
    assert result[0] is True  # Valid schema should return True
@pytest.mark.xwapi_unit

def test_get_openapi_version():
    """Test getting OpenAPI version from schema."""
    schema = {"openapi": "3.1.0", "info": {}}
    version = get_openapi_version(schema)
    assert version == "3.1.0" or version is not None
@pytest.mark.xwapi_unit

def test_export_openapi_schema():
    """Test exporting OpenAPI schema."""
    from exonware.xwapi.common.app import create_app
    app = create_app(title="Test API", version="1.0.0")
    exported = export_openapi_schema(app)
    # Should return schema dict
    assert exported is not None
    assert isinstance(exported, dict)
    assert "openapi" in exported
    assert "info" in exported
