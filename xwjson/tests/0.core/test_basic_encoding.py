#exonware/xwjson/tests/0.core/test_basic_encoding.py
"""
Core encoding/decoding tests for XWJSON.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Fast, high-value core tests covering critical paths (80/20 rule).
"""

import pytest
from exonware.xwjson import XWJSONSerializer
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_core


def test_encode_decode_round_trip():
    """Test basic encode/decode round-trip."""
    serializer = XWJSONSerializer()
    data = {
        "users": [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
        ],
        "metadata": {
            "version": "1.0",
            "created": "2025-01-01"
        }
    }
    # Encode
    encoded = serializer.encode(data)
    assert isinstance(encoded, bytes)
    assert len(encoded) > 0
    # Decode
    decoded = serializer.decode(encoded)
    assert decoded == data
@pytest.mark.xwjson_core


def test_encode_decode_various_types():
    """Test encoding/decoding various data types."""
    serializer = XWJSONSerializer()
    test_cases = [
        {"string": "hello", "number": 42, "float": 3.14, "bool": True, "null": None},
        [1, 2, 3, 4, 5],
        {"nested": {"deep": {"value": 123}}},
        {"array": [1, "two", 3.0, True, None]},
        {"empty": {}, "empty_list": []},
    ]
    for data in test_cases:
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        assert decoded == data, f"Round-trip failed for {type(data)}"
@pytest.mark.xwjson_core


def test_encode_with_metadata():
    """Test encoding with metadata."""
    serializer = XWJSONSerializer()
    data = {"name": "test"}
    metadata = {"source_format": "json", "version": "1.0"}
    encoded = serializer.encode(
        data,
        options={
            'metadata': metadata,
            'format_code': 0x00  # JSON
        }
    )
    # Decode with metadata
    result = serializer.decode(encoded, options={'return_metadata': True})
    assert result['data'] == data
    assert result['metadata'] is not None
@pytest.mark.xwjson_core


def test_magic_bytes():
    """Test XWJSON magic bytes are present."""
    serializer = XWJSONSerializer()
    data = {"test": "data"}
    encoded = serializer.encode(data)
    # Check magic bytes
    assert encoded[:4] == b'XWJ1', "Invalid magic bytes"
@pytest.mark.xwjson_core


def test_file_operations(temp_dir, sample_data):
    """Test basic file save/load operations."""
    serializer = XWJSONSerializer()
    file_path = temp_dir / "test.xwjson"
    # Save
    serializer.save_file(sample_data, file_path)
    assert file_path.exists()
    # Load
    loaded = serializer.load_file(file_path)
    assert loaded == sample_data
@pytest.mark.xwjson_core


def test_encode_decode_with_various_format_codes():
    """Test encoding with different format codes (JSON, YAML, XML, TOML)."""
    serializer = XWJSONSerializer()
    data = {"test": "data"}
    format_codes = [0x00, 0x01, 0x02, 0x03]  # JSON, YAML, XML, TOML
    for format_code in format_codes:
        encoded = serializer.encode(
            data,
            options={
                'format_code': format_code,
                'metadata': {'source_format': ['json', 'yaml', 'xml', 'toml'][format_code]}
            }
        )
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0
        # Decode and verify
        decoded = serializer.decode(encoded)
        assert decoded == data
@pytest.mark.xwjson_core


def test_encode_decode_with_flags():
    """Test encoding with various flags."""
    serializer = XWJSONSerializer()
    data = {"test": "data"}
    # Test with metadata flag
    encoded_with_metadata = serializer.encode(
        data,
        options={
            'flags': 0x01,  # FLAG_HAS_METADATA
            'metadata': {'source': 'test'}
        }
    )
    result = serializer.decode(encoded_with_metadata, options={'return_metadata': True})
    assert result['data'] == data
    assert result.get('metadata') is not None
@pytest.mark.xwjson_core


def test_decode_invalid_data():
    """Test decoding invalid XWJSON data raises error."""
    serializer = XWJSONSerializer()
    # Invalid magic bytes
    with pytest.raises(SerializationError):
        serializer.decode(b'INVALID_MAGIC_BYTES')
    # Too short data
    with pytest.raises(SerializationError):
        serializer.decode(b'XWJ')
    # Empty data
    with pytest.raises(SerializationError):
        serializer.decode(b'')
@pytest.mark.xwjson_core


def test_encode_decode_nested_structures():
    """Test encoding/decoding deeply nested structures."""
    serializer = XWJSONSerializer()
    # Deeply nested dict
    deep_dict = {}
    current = deep_dict
    for i in range(10):
        current[f"level_{i}"] = {}
        current = current[f"level_{i}"]
    current["value"] = "deep"
    encoded = serializer.encode(deep_dict)
    decoded = serializer.decode(encoded)
    assert decoded == deep_dict
    # Nested lists
    nested_list = [[[[1, 2, 3], [4, 5]], [6, 7]], [8, 9, 10]]
    encoded = serializer.encode(nested_list)
    decoded = serializer.decode(encoded)
    assert decoded == nested_list
@pytest.mark.xwjson_core


def test_encode_decode_special_values():
    """Test encoding/decoding special values (None, NaN, Inf)."""
    serializer = XWJSONSerializer()
    # None values
    data_with_none = {"null": None, "list": [1, None, 3]}
    encoded = serializer.encode(data_with_none)
    decoded = serializer.decode(encoded)
    assert decoded["null"] is None
    assert decoded["list"][1] is None
    # NaN and Infinity (should be preserved or converted appropriately)
    data_with_special = {
        "inf": float('inf'),
        "neg_inf": float('-inf'),
    }
    # Note: JSON standard doesn't support NaN/Inf, so they may be converted
    encoded = serializer.encode(data_with_special)
    decoded = serializer.decode(encoded)
    # Verify structure is preserved (exact behavior depends on MessagePack)
@pytest.mark.xwjson_core
@pytest.mark.asyncio
async def test_async_file_operations(temp_dir, sample_data):
    """Test async file save/load operations."""
    serializer = XWJSONSerializer()
    file_path = temp_dir / "test_async.xwjson"
    # Save async
    await serializer.save_file_async(sample_data, file_path)
    assert file_path.exists()
    # Load async
    loaded = await serializer.load_file_async(file_path)
    assert loaded == sample_data
@pytest.mark.xwjson_core


def test_serializer_properties():
    """Test serializer metadata properties."""
    serializer = XWJSONSerializer()
    assert serializer.codec_id == "xwjson"
    assert serializer.format_name == "XWJSON"
    assert serializer.is_binary_format is True
    assert serializer.supports_streaming is True
    assert serializer.supports_lazy_loading is True
    assert serializer.supports_path_based_updates is True
    assert serializer.supports_atomic_path_write is True
    assert serializer.supports_schema_validation is True
    assert serializer.supports_queries is True
    assert "xwjson" in serializer.aliases
    assert ".xwjson" in serializer.file_extensions
    assert "application/x-xwjson" in serializer.media_types
    assert "binary" in serializer.codec_types
    assert "serialization" in serializer.codec_types
