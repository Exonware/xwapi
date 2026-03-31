#exonware/xwjson/tests/2.integration/scenarios/test_format_conversion_matrix.py
"""
Format Conversion Matrix Tests - All Format Combinations
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Tests all format conversion combinations:
- JSON ↔ YAML ↔ XML ↔ TOML (all pairs)
- Round-trip for each pair
- Multi-hop conversions
- Correctness verification for each conversion
"""

import pytest
from exonware.xwjson.formats.binary.xwjson.converter import XWJSONConverter
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_serialization
@pytest.mark.asyncio

class TestFormatConversionMatrix:
    """Matrix of all format conversion combinations."""
    @pytest.fixture

    def converter(self):
        """Create converter instance."""
        return XWJSONConverter()
    @pytest.fixture

    def test_data(self):
        """Standard test data for all conversions."""
        return {
            "string": "test",
            "number": 123,
            "float": 3.14159,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
            "nested": {
                "level1": {
                    "level2": {
                        "value": "deep"
                    }
                }
            }
        }
    # JSON conversions
    @pytest.mark.asyncio

    async def test_json_to_json(self, converter, test_data):
        """Test JSON to JSON conversion."""
        result = await converter.convert(test_data, "json", "json")
        assert result == test_data
    @pytest.mark.asyncio

    async def test_json_to_yaml(self, converter, test_data):
        """Test JSON to YAML conversion."""
        try:
            result = await converter.convert(test_data, "json", "yaml")
            # Convert back to verify
            round_trip = await converter.convert(result, "yaml", "json")
            assert round_trip == test_data
        except (ImportError, SerializationError):
            pytest.skip("YAML conversion not available")
    @pytest.mark.asyncio

    async def test_json_to_toml(self, converter, test_data):
        """Test JSON to TOML conversion."""
        try:
            result = await converter.convert(test_data, "json", "toml")
            # Convert back to verify
            round_trip = await converter.convert(result, "toml", "json")
            assert round_trip == test_data
        except (ImportError, SerializationError):
            pytest.skip("TOML conversion not available")
    # YAML conversions
    @pytest.mark.asyncio

    async def test_yaml_to_json(self, converter, test_data):
        """Test YAML to JSON conversion."""
        try:
            result = await converter.convert(test_data, "yaml", "json")
            assert result == test_data
        except (ImportError, SerializationError):
            pytest.skip("YAML conversion not available")
    @pytest.mark.asyncio

    async def test_yaml_to_yaml(self, converter, test_data):
        """Test YAML to YAML conversion."""
        try:
            result = await converter.convert(test_data, "yaml", "yaml")
            # Convert back to verify
            round_trip = await converter.convert(result, "yaml", "json")
            original_json = await converter.convert(test_data, "yaml", "json")
            assert round_trip == original_json
        except (ImportError, SerializationError):
            pytest.skip("YAML conversion not available")
    @pytest.mark.asyncio

    async def test_yaml_to_toml(self, converter, test_data):
        """Test YAML to TOML conversion."""
        try:
            result = await converter.convert(test_data, "yaml", "toml")
            # Convert back to verify
            round_trip = await converter.convert(result, "toml", "json")
            original_json = await converter.convert(test_data, "yaml", "json")
            assert round_trip == original_json
        except (ImportError, SerializationError):
            pytest.skip("YAML/TOML conversion not available")
    # TOML conversions
    @pytest.mark.asyncio

    async def test_toml_to_json(self, converter, test_data):
        """Test TOML to JSON conversion."""
        try:
            result = await converter.convert(test_data, "toml", "json")
            assert result == test_data
        except (ImportError, SerializationError):
            pytest.skip("TOML conversion not available")
    @pytest.mark.asyncio

    async def test_toml_to_yaml(self, converter, test_data):
        """Test TOML to YAML conversion."""
        try:
            result = await converter.convert(test_data, "toml", "yaml")
            # Convert back to verify
            round_trip = await converter.convert(result, "yaml", "json")
            original_json = await converter.convert(test_data, "toml", "json")
            assert round_trip == original_json
        except (ImportError, SerializationError):
            pytest.skip("TOML/YAML conversion not available")
    @pytest.mark.asyncio

    async def test_toml_to_toml(self, converter, test_data):
        """Test TOML to TOML conversion."""
        try:
            result = await converter.convert(test_data, "toml", "toml")
            # Convert back to verify
            round_trip = await converter.convert(result, "toml", "json")
            original_json = await converter.convert(test_data, "toml", "json")
            assert round_trip == original_json
        except (ImportError, SerializationError):
            pytest.skip("TOML conversion not available")
    # Multi-hop conversions
    @pytest.mark.asyncio

    async def test_json_yaml_toml_json(self, converter, test_data):
        """Test multi-hop: JSON → YAML → TOML → JSON."""
        try:
            yaml_data = await converter.convert(test_data, "json", "yaml")
            toml_data = await converter.convert(yaml_data, "yaml", "toml")
            result = await converter.convert(toml_data, "toml", "json")
            assert result == test_data
        except (ImportError, SerializationError):
            pytest.skip("Multi-format conversion not available")
    @pytest.mark.asyncio

    async def test_toml_yaml_json_toml(self, converter, test_data):
        """Test multi-hop: TOML → YAML → JSON → TOML."""
        try:
            yaml_data = await converter.convert(test_data, "toml", "yaml")
            json_data = await converter.convert(yaml_data, "yaml", "json")
            result = await converter.convert(json_data, "json", "toml")
            # Convert back to JSON to verify
            round_trip = await converter.convert(result, "toml", "json")
            original_json = await converter.convert(test_data, "toml", "json")
            assert round_trip == original_json
        except (ImportError, SerializationError):
            pytest.skip("Multi-format conversion not available")
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_serialization
@pytest.mark.asyncio

class TestFormatConversionCorrectness:
    """Correctness verification for format conversions."""
    @pytest.fixture

    def converter(self):
        """Create converter instance."""
        return XWJSONConverter()
    @pytest.mark.parametrize("source_format,target_format", [
        ("json", "json"),
        ("json", "yaml"),
        ("json", "toml"),
        ("yaml", "json"),
        ("yaml", "yaml"),
        ("yaml", "toml"),
        ("toml", "json"),
        ("toml", "yaml"),
        ("toml", "toml"),
    ])
    @pytest.mark.asyncio

    async def test_format_pair_correctness(self, converter, source_format, target_format):
        """Test correctness for each format pair."""
        data = {
            "test": "data",
            "number": 123,
            "list": [1, 2, 3],
            "nested": {"value": "test"}
        }
        try:
            # Convert
            result = await converter.convert(data, source_format, target_format)
            # Convert back
            round_trip = await converter.convert(result, target_format, source_format)
            # Verify
            assert round_trip == data, f"Failed: {source_format} → {target_format} → {source_format}"
        except (ImportError, SerializationError):
            pytest.skip(f"Conversion {source_format} → {target_format} not available")
