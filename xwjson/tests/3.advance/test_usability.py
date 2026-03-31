#exonware/xwjson/tests/3.advance/test_usability.py
"""
Usability excellence tests (Priority #2).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Usability tests: API intuitiveness, error messages, documentation.
"""

import pytest
from exonware.xwjson import XWJSONSerializer
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_usability


def test_api_intuitiveness():
    """Test API is intuitive and easy to use."""
    serializer = XWJSONSerializer()
    # Should be simple to use
    data = {"test": "data"}
    encoded = serializer.encode(data)
    decoded = serializer.decode(encoded)
    assert decoded == data
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_usability


def test_error_messages_clarity():
    """Test error messages are clear and helpful."""
    serializer = XWJSONSerializer()
    # Invalid data should give clear error
    invalid_data = b'INVALID' + b'\x00' * 100
    with pytest.raises(SerializationError) as exc_info:
        serializer.decode(invalid_data)
    error_msg = str(exc_info.value)
    assert "magic bytes" in error_msg.lower() or "invalid" in error_msg.lower()
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_usability
@pytest.mark.asyncio
async def test_async_api_consistency(temp_dir):
    """Test async API is consistent and intuitive."""
    serializer = XWJSONSerializer()
    file_path = temp_dir / "async_test.xwjson"
    data = {"test": "async"}
    # Async save
    await serializer.save_file_async(data, file_path)
    # Async load
    loaded = await serializer.load_file_async(file_path)
    assert loaded == data
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_usability


def test_sync_wrapper_consistency():
    """Test sync wrappers work consistently."""
    serializer = XWJSONSerializer()
    data = {"test": "sync"}
    # Sync methods should work
    encoded = serializer.encode(data)
    decoded = serializer.decode(encoded)
    assert decoded == data
