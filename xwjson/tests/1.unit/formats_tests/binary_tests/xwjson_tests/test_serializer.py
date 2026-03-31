#exonware/xwjson/tests/1.unit/formats_tests/binary_tests/xwjson_tests/test_serializer.py
"""
Unit tests for XWJSONSerializer.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import pytest
from exonware.xwjson import XWJSONSerializer
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization


def test_serializer_properties():
    """Test serializer metadata properties."""
    serializer = XWJSONSerializer()
    assert serializer.codec_id == "xwjson"
    assert serializer.is_binary_format is True
    assert serializer.supports_streaming is True
    assert serializer.supports_lazy_loading is True
    assert serializer.supports_path_based_updates is True
    assert serializer.supports_atomic_path_write is True
    assert serializer.supports_schema_validation is True
    assert serializer.supports_queries is True
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization


def test_serializer_encode():
    """Test serializer encode method."""
    serializer = XWJSONSerializer()
    data = {"test": "data"}
    encoded = serializer.encode(data)
    assert isinstance(encoded, bytes)
    assert len(encoded) > 0
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization


def test_serializer_decode():
    """Test serializer decode method."""
    serializer = XWJSONSerializer()
    data = {"test": "data"}
    encoded = serializer.encode(data)
    decoded = serializer.decode(encoded)
    assert decoded == data
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization


def test_serializer_decode_with_metadata():
    """Test serializer decode with metadata return."""
    serializer = XWJSONSerializer()
    data = {"test": "data"}
    encoded = serializer.encode(data, options={'metadata': {"source": "json"}})
    result = serializer.decode(encoded, options={'return_metadata': True})
    assert 'data' in result
    assert result['data'] == data
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization


def test_serializer_save_load_file(temp_dir):
    """Test serializer file save/load."""
    serializer = XWJSONSerializer()
    file_path = temp_dir / "test.xwjson"
    data = {"test": "data"}
    serializer.save_file(data, file_path)
    assert file_path.exists()
    loaded = serializer.load_file(file_path)
    assert loaded == data
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization
@pytest.mark.asyncio
async def test_serializer_save_load_file_async(temp_dir):
    """Test serializer async file save/load."""
    serializer = XWJSONSerializer()
    file_path = temp_dir / "test_async.xwjson"
    data = {"test": "async"}
    await serializer.save_file_async(data, file_path)
    assert file_path.exists()
    loaded = await serializer.load_file_async(file_path)
    assert loaded == data
