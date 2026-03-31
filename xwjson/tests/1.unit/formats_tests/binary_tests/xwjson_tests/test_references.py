#exonware/xwjson/tests/1.unit/formats_tests/binary_tests/xwjson_tests/test_references.py
"""
Unit tests for XWJSON reference resolution.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import pytest
from exonware.xwjson.formats.binary.xwjson.references import XWJSONReferenceResolver
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_references


def test_reference_resolver_init():
    """Test reference resolver initialization."""
    resolver = XWJSONReferenceResolver()
    assert resolver is not None
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_references


def test_json_pointer_resolution():
    """Test JSON Pointer resolution."""
    resolver = XWJSONReferenceResolver()
    data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ],
        "metadata": {"version": "1.0"}
    }
    # Test simple path
    result = resolver._resolve_json_pointer("/users/0/name", data)
    assert result == "Alice"
    # Test nested path
    result = resolver._resolve_json_pointer("/metadata/version", data)
    assert result == "1.0"
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_references


def test_json_pointer_invalid_path():
    """Test JSON Pointer with invalid path."""
    resolver = XWJSONReferenceResolver()
    data = {"users": [{"name": "Alice"}]}
    with pytest.raises(SerializationError):
        resolver._resolve_json_pointer("/users/999/name", data)
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_references


def test_detect_json_references():
    """Test JSON reference detection."""
    resolver = XWJSONReferenceResolver()
    data = {
        "user": {"$ref": "#/definitions/user"},
        "definitions": {
            "user": {"type": "object"}
        }
    }
    references = resolver._detect_json_references(data)
    assert len(references) > 0
    assert references[0]["type"] == "json"
    assert references[0]["reference"] == "#/definitions/user"
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_references


def test_circular_reference_detection():
    """Test circular reference detection."""
    resolver = XWJSONReferenceResolver()
    # Simulate circular reference
    resolver._resolving.add("ref1")
    with pytest.raises(SerializationError, match="Circular reference"):
        resolver.resolve("ref1", "json")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_references


def test_reference_caching():
    """Test reference caching."""
    resolver = XWJSONReferenceResolver()
    data = {"value": "test"}
    # Use public resolve method which uses cache
    result1 = resolver.resolve("/value", reference_type="json", data=data)
    result2 = resolver.resolve("/value", reference_type="json", data=data)
    assert result1 == result2 == "test"
    # Cache should be used (check cache size)
    assert len(resolver._cache) > 0
