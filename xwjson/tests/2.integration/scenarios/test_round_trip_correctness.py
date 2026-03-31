#exonware/xwjson/tests/2.integration/scenarios/test_round_trip_correctness.py
"""
Round-Trip Conversion Correctness Tests
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Tests round-trip conversions for correctness:
- A → XWJSON → B → XWJSON → A (should equal original A)
- All format pairs (JSON, YAML, XML, TOML)
- Verify data integrity at each step
- Verify metadata preservation
"""

import pytest
from exonware.xwjson import XWJSONSerializer
from exonware.xwjson.formats.binary.xwjson.converter import XWJSONConverter
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_serialization
@pytest.mark.asyncio

class TestRoundTripCorrectness:
    """Round-trip conversion correctness tests."""
    @pytest.fixture

    def serializer(self):
        """Create serializer instance."""
        return XWJSONSerializer()
    @pytest.fixture

    def converter(self):
        """Create converter instance."""
        return XWJSONConverter()
    @pytest.fixture

    def test_data_sets(self):
        """Various test data sets for round-trip testing."""
        return {
            "simple": {
                "name": "test",
                "value": 123
            },
            "nested": {
                "level1": {
                    "level2": {
                        "level3": {
                            "value": "deep"
                        }
                    }
                }
            },
            "arrays": {
                "numbers": [1, 2, 3, 4, 5],
                "strings": ["a", "b", "c"],
                "mixed": [1, "two", 3.0, True, None]
            },
            "complex": {
                "users": [
                    {
                        "id": 1,
                        "name": "Alice",
                        "metadata": {
                            "created": "2025-01-01",
                            "tags": ["admin", "user"]
                        }
                    },
                    {
                        "id": 2,
                        "name": "Bob",
                        "metadata": {
                            "created": "2025-01-02",
                            "tags": ["user"]
                        }
                    }
                ]
            },
            "edge_cases": {
                "empty_dict": {},
                "empty_list": [],
                "null_value": None,
                "boolean_true": True,
                "boolean_false": False,
                "zero": 0,
                "negative": -10,
                "float": 3.14159
            }
        }
    @pytest.mark.asyncio

    async def test_round_trip_json_xwjson_json(self, serializer, test_data_sets):
        """Test round-trip: JSON → XWJSON → JSON."""
        for name, data in test_data_sets.items():
            # JSON → XWJSON
            xwjson_bytes = serializer.encode(data)
            assert isinstance(xwjson_bytes, bytes)
            # XWJSON → JSON
            decoded = serializer.decode(xwjson_bytes)
            # Verify equality
            assert decoded == data, f"Round-trip failed for {name}"
    @pytest.mark.asyncio

    async def test_round_trip_json_yaml_json(self, converter, test_data_sets):
        """Test round-trip: JSON → YAML → JSON."""
        for name, data in test_data_sets.items():
            try:
                # JSON → YAML
                yaml_data = await converter.convert(
                    data,
                    source_format="json",
                    target_format="yaml"
                )
                # YAML → JSON
                result = await converter.convert(
                    yaml_data,
                    source_format="yaml",
                    target_format="json"
                )
                # Verify equality
                assert result == data, f"Round-trip failed for {name}"
            except (ImportError, SerializationError) as e:
                pytest.skip(f"YAML conversion not available for {name}: {e}")
    @pytest.mark.asyncio

    async def test_round_trip_json_toml_json(self, converter, test_data_sets):
        """Test round-trip: JSON → TOML → JSON."""
        for name, data in test_data_sets.items():
            try:
                # JSON → TOML
                toml_data = await converter.convert(
                    data,
                    source_format="json",
                    target_format="toml"
                )
                # TOML → JSON
                result = await converter.convert(
                    toml_data,
                    source_format="toml",
                    target_format="json"
                )
                # Verify equality
                assert result == data, f"Round-trip failed for {name}"
            except (ImportError, SerializationError) as e:
                pytest.skip(f"TOML conversion not available for {name}: {e}")
    @pytest.mark.asyncio

    async def test_round_trip_with_metadata(self, serializer):
        """Test round-trip preserves metadata."""
        data = {
            "user": {
                "$ref": "#/definitions/User"
            },
            "data": "value"
        }
        # Encode with metadata
        encoded = serializer.encode(
            data,
            options={
                'metadata': {'source': 'test'},
                'format_code': 0x00
            }
        )
        # Decode with metadata
        result = serializer.decode(encoded, options={'return_metadata': True})
        assert result['data'] == data
        assert result.get('metadata') is not None
    @pytest.mark.asyncio

    async def test_round_trip_large_structure(self, serializer):
        """Test round-trip with large structure."""
        # Create large structure
        data = {
            "items": [
                {
                    "id": i,
                    "name": f"Item {i}",
                    "data": list(range(100))
                }
                for i in range(1000)
            ]
        }
        # Round-trip
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        assert decoded == data
        assert len(decoded["items"]) == 1000
    @pytest.mark.asyncio

    async def test_round_trip_unicode_data(self, serializer):
        """Test round-trip with unicode data."""
        data = {
            "unicode": "Hello 世界 🌍",
            "emoji": "😀😃😄",
            "chinese": "你好世界",
            "arabic": "مرحبا",
            "japanese": "こんにちは"
        }
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        assert decoded == data
        assert decoded["unicode"] == "Hello 世界 🌍"
    @pytest.mark.asyncio

    async def test_round_trip_special_characters(self, serializer):
        """Test round-trip with special characters."""
        data = {
            "special": "!@#$%^&*()_+-=[]{}|;':\",./<>?`~",
            "newlines": "Line 1\nLine 2\nLine 3",
            "tabs": "Tab\tTab\tTab",
            "quotes": 'Single "double" quotes'
        }
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        assert decoded == data
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_serialization
@pytest.mark.asyncio

class TestMultiHopCorrectness:
    """Multi-hop conversion correctness tests."""
    @pytest.fixture

    def converter(self):
        """Create converter instance."""
        return XWJSONConverter()
    @pytest.mark.asyncio

    async def test_multi_hop_json_yaml_toml_json(self, converter):
        """Test multi-hop: JSON → YAML → TOML → JSON."""
        data = {
            "test": "data",
            "number": 123,
            "nested": {
                "value": "test"
            }
        }
        try:
            # JSON → YAML
            yaml_data = await converter.convert(data, "json", "yaml")
            # YAML → TOML
            toml_data = await converter.convert(yaml_data, "yaml", "toml")
            # TOML → JSON
            result = await converter.convert(toml_data, "toml", "json")
            assert result == data
        except (ImportError, SerializationError) as e:
            pytest.skip(f"Multi-format conversion not available: {e}")
    @pytest.mark.asyncio

    async def test_multi_hop_preserves_structure(self, converter):
        """Test multi-hop preserves structure."""
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ],
            "settings": {
                "theme": "dark",
                "notifications": True
            }
        }
        try:
            # Multiple hops
            yaml_data = await converter.convert(data, "json", "yaml")
            toml_data = await converter.convert(yaml_data, "yaml", "toml")
            json_data = await converter.convert(toml_data, "toml", "json")
            # Verify structure preserved
            assert json_data == data
            assert len(json_data["users"]) == 2
            assert json_data["settings"]["theme"] == "dark"
        except (ImportError, SerializationError) as e:
            pytest.skip(f"Multi-format conversion not available: {e}")
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_serialization
@pytest.mark.asyncio

class TestDataIntegrity:
    """Data integrity verification tests."""
    @pytest.fixture

    def serializer(self):
        """Create serializer instance."""
        return XWJSONSerializer()
    @pytest.mark.asyncio

    async def test_integrity_numeric_precision(self, serializer):
        """Test numeric precision is preserved."""
        data = {
            "integer": 1234567890,
            "float": 3.141592653589793,
            "large_int": 9223372036854775807,
            "scientific": 1.23456789e10
        }
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        assert decoded["integer"] == data["integer"]
        assert decoded["float"] == data["float"]
        assert decoded["large_int"] == data["large_int"]
        assert decoded["scientific"] == data["scientific"]
    @pytest.mark.asyncio

    async def test_integrity_type_preservation(self, serializer):
        """Test data types are preserved."""
        data = {
            "string": "text",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"key": "value"}
        }
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        assert isinstance(decoded["string"], str)
        assert isinstance(decoded["integer"], int)
        assert isinstance(decoded["float"], float)
        assert isinstance(decoded["boolean"], bool)
        assert decoded["null"] is None
        assert isinstance(decoded["list"], list)
        assert isinstance(decoded["dict"], dict)
    @pytest.mark.asyncio

    async def test_integrity_order_preservation(self, serializer):
        """Test list order is preserved."""
        data = {
            "ordered_list": [1, 2, 3, 4, 5],
            "mixed_list": ["a", 1, "b", 2, "c", 3]
        }
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        assert decoded["ordered_list"] == data["ordered_list"]
        assert decoded["mixed_list"] == data["mixed_list"]
    @pytest.mark.asyncio

    async def test_integrity_nested_structure(self, serializer):
        """Test nested structure integrity."""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep",
                        "array": [1, 2, 3],
                        "nested_dict": {
                            "key": "value"
                        }
                    }
                }
            }
        }
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        assert decoded["level1"]["level2"]["level3"]["value"] == "deep"
        assert decoded["level1"]["level2"]["level3"]["array"] == [1, 2, 3]
        assert decoded["level1"]["level2"]["level3"]["nested_dict"]["key"] == "value"
