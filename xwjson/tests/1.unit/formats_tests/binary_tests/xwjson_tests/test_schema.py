#exonware/xwjson/tests/1.unit/formats_tests/binary_tests/xwjson_tests/test_schema.py
"""
Unit tests for XWJSONSchemaValidator.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import pytest
from pathlib import Path
import json
from exonware.xwjson.formats.binary.xwjson.schema import XWJSONSchemaValidator
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_schema_validator_init():
    """Test schema validator initialization without schema."""
    validator = XWJSONSchemaValidator()
    assert validator is not None
    assert validator._schema is None
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_schema_validator_init_with_schema():
    """Test schema validator initialization with schema dict."""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name"]
    }
    try:
        validator = XWJSONSchemaValidator(schema)
        assert validator._schema == schema
    except ImportError:
        pytest.skip("Schema validation libraries not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_schema_validator_init_with_file(temp_dir):
    """Test schema validator initialization with schema file."""
    schema_file = temp_dir / "schema.json"
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        }
    }
    with open(schema_file, 'w', encoding='utf-8') as f:
        json.dump(schema, f)
    try:
        validator = XWJSONSchemaValidator(schema_file)
        assert validator._schema == schema
    except ImportError:
        pytest.skip("Schema validation libraries not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_validate_valid_data():
    """Test validation of valid data."""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name"]
    }
    try:
        validator = XWJSONSchemaValidator(schema)
        valid_data = {"name": "Alice", "age": 30}
        result = validator.validate(valid_data)
        assert result is True
    except ImportError:
        pytest.skip("Schema validation libraries not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_validate_invalid_data():
    """Test validation of invalid data."""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name"]
    }
    try:
        validator = XWJSONSchemaValidator(schema)
        invalid_data = {"age": "not_an_integer"}  # Missing required "name", wrong type for age
        result = validator.validate(invalid_data)
        assert result is False
    except ImportError:
        pytest.skip("Schema validation libraries not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_validate_no_schema():
    """Test validation without schema (should always return True)."""
    validator = XWJSONSchemaValidator()
    # Without schema, everything is valid
    result = validator.validate({"any": "data"})
    assert result is True
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_get_validation_errors_valid():
    """Test getting validation errors for valid data."""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        },
        "required": ["name"]
    }
    try:
        validator = XWJSONSchemaValidator(schema)
        valid_data = {"name": "Alice"}
        errors = validator.get_validation_errors(valid_data)
        assert len(errors) == 0
    except ImportError:
        pytest.skip("Schema validation libraries not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_get_validation_errors_invalid():
    """Test getting validation errors for invalid data."""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        },
        "required": ["name"]
    }
    try:
        validator = XWJSONSchemaValidator(schema)
        invalid_data = {}  # Missing required "name"
        errors = validator.get_validation_errors(invalid_data)
        assert len(errors) > 0
        assert any("name" in error.lower() or "required" in error.lower() for error in errors)
    except ImportError:
        pytest.skip("Schema validation libraries not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_load_schema(temp_dir):
    """Test loading schema from file."""
    schema_file = temp_dir / "schema.json"
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        }
    }
    with open(schema_file, 'w', encoding='utf-8') as f:
        json.dump(schema, f)
    try:
        validator = XWJSONSchemaValidator()
        validator.load_schema(schema_file)
        assert validator._schema == schema
    except ImportError:
        pytest.skip("Schema validation libraries not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_save_schema(temp_dir):
    """Test saving schema to file."""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        }
    }
    try:
        validator = XWJSONSchemaValidator(schema)
        schema_file = temp_dir / "saved_schema.json"
        validator.save_schema(schema_file)
        assert schema_file.exists()
        with open(schema_file, encoding='utf-8') as f:
            saved_schema = json.load(f)
        assert saved_schema == schema
    except ImportError:
        pytest.skip("Schema validation libraries not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_save_schema_no_schema():
    """Test saving schema when no schema is set."""
    validator = XWJSONSchemaValidator()
    schema_file = Path("test_schema.json")
    with pytest.raises(SerializationError):
        validator.save_schema(schema_file)
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization
@pytest.mark.asyncio
async def test_validate_async():
    """Test async validation."""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        },
        "required": ["name"]
    }
    try:
        validator = XWJSONSchemaValidator(schema)
        valid_data = {"name": "Alice"}
        result = await validator.validate_async(valid_data)
        assert result is True
    except ImportError:
        pytest.skip("Schema validation libraries not available")
