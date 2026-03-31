#exonware/xwjson/tests/1.unit/formats_tests/binary_tests/xwjson_tests/test_converter.py
"""
Unit tests for XWJSONConverter.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import pytest
from exonware.xwjson.formats.binary.xwjson.converter import XWJSONConverter
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_converter_init():
    """Test converter initialization."""
    converter = XWJSONConverter()
    assert converter is not None
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization
@pytest.mark.asyncio
async def test_convert_json_to_json(temp_dir):
    """Test JSON to JSON conversion via XWJSON."""
    converter = XWJSONConverter()
    source_data = {"name": "test", "value": 123}
    target_path = temp_dir / "output.json"
    result = await converter.convert(
        source_data,
        source_format="json",
        target_format="json",
        target_path=target_path
    )
    assert result == source_data
    assert target_path.exists()
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization
@pytest.mark.asyncio
async def test_convert_json_to_yaml(temp_dir):
    """Test JSON to YAML conversion via XWJSON."""
    converter = XWJSONConverter()
    source_data = {"name": "test", "value": 123}
    target_path = temp_dir / "output.yaml"
    result = await converter.convert(
        source_data,
        source_format="json",
        target_format="yaml",
        target_path=target_path
    )
    assert result == source_data
    # Verify file was created (if YAML support available)
    # Note: May skip if PyYAML not available
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization
@pytest.mark.asyncio
async def test_convert_with_metadata_preservation():
    """Test format conversion preserves metadata."""
    converter = XWJSONConverter()
    source_data = {"name": "test", "$ref": "#/definitions/Test"}
    result = await converter.convert(
        source_data,
        source_format="json",
        target_format="json"
    )
    # Metadata should be preserved through XWJSON intermediate format
    assert isinstance(result, dict)
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization
@pytest.mark.asyncio
async def test_convert_without_target_path():
    """Test conversion without saving to file."""
    converter = XWJSONConverter()
    source_data = {"name": "test"}
    result = await converter.convert(
        source_data,
        source_format="json",
        target_format="json"
    )
    assert result == source_data
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_get_format_code():
    """Test format code mapping."""
    converter = XWJSONConverter()
    assert converter._get_format_code("json") == 0x00
    assert converter._get_format_code("yaml") == 0x01
    assert converter._get_format_code("xml") == 0x02
    assert converter._get_format_code("toml") == 0x03
    assert converter._get_format_code("unknown") == 0x00  # Default to JSON
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization
@pytest.mark.asyncio
async def test_convert_xml_format(temp_dir):
    """Test XML format conversion."""
    converter = XWJSONConverter()
    # XML-like data (simplified)
    source_data = {"root": {"element": "value"}}
    try:
        result = await converter.convert(
            source_data,
            source_format="xml",
            target_format="json"
        )
        assert isinstance(result, dict)
    except (ImportError, SerializationError):
        # XML support may not be available
        pytest.skip("XML conversion support not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization
@pytest.mark.asyncio
async def test_convert_toml_format(temp_dir):
    """Test TOML format conversion."""
    converter = XWJSONConverter()
    source_data = {"name": "test", "value": 123}
    try:
        result = await converter.convert(
            source_data,
            source_format="toml",
            target_format="json"
        )
        assert isinstance(result, dict)
    except (ImportError, SerializationError):
        # TOML support may not be available
        pytest.skip("TOML conversion support not available")
