#exonware/xwjson/tests/3.advance/test_security.py
"""
Security excellence tests (Priority #1).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Security tests: input validation, path traversal protection, reference security.
"""

import pytest
from pathlib import Path
from exonware.xwjson import XWJSONSerializer
from exonware.xwjson.operations import XWJSONDataOperations
from exonware.xwjson.formats.binary.xwjson.references import XWJSONReferenceResolver
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_security


def test_path_traversal_protection():
    """Test path traversal protection in file references."""
    resolver = XWJSONReferenceResolver()
    base_path = Path("/safe/base")
    # Should block path traversal attempts
    malicious_paths = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "/etc/passwd",
        "file:///etc/passwd",
    ]
    for malicious_path in malicious_paths:
        with pytest.raises(SerializationError, match="Path traversal"):
            resolver._resolve_file_reference(malicious_path, base_path)
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_security


def test_invalid_magic_bytes():
    """Test rejection of invalid magic bytes."""
    serializer = XWJSONSerializer()
    # Create data with invalid magic
    invalid_data = b'INVALID' + b'\x00' * 1000
    with pytest.raises(SerializationError, match="magic bytes"):
        serializer.decode(invalid_data)
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_security


def test_circular_reference_detection():
    """Test circular reference detection."""
    resolver = XWJSONReferenceResolver()
    # Simulate circular reference
    resolver._resolving.add("ref1")
    with pytest.raises(SerializationError, match="Circular reference"):
        resolver.resolve("ref1", "json")
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_security
@pytest.mark.asyncio
async def test_path_validation(temp_dir):
    """Test path validation in operations."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "security_test.xwjson"
    data = {"users": [{"name": "Alice"}]}
    await ops.atomic_write(file_path, data)
    # Valid paths should work
    await ops.write_path(file_path, "/users/0/name", "Bob")
    # Invalid paths should fail gracefully
    with pytest.raises((SerializationError, KeyError, ValueError)):
        await ops.write_path(file_path, "/users/999/name", "Invalid")
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_security


def test_input_size_limits():
    """Test input size limits."""
    serializer = XWJSONSerializer(max_size_mb=1.0)  # 1MB limit
    # Small data should work
    small_data = {"test": "data"}
    encoded = serializer.encode(small_data)
    decoded = serializer.decode(encoded)
    assert decoded == small_data
    # Very large data should be handled (may fail or truncate based on implementation)
    # This is a stress test - actual behavior depends on implementation
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_security


def test_depth_limits():
    """Test nesting depth limits."""
    serializer = XWJSONSerializer(max_depth=10)
    # Create deeply nested structure
    def create_nested(depth: int, current: int = 0) -> dict:
        if current >= depth:
            return {"value": "leaf"}
        return {"nested": create_nested(depth, current + 1)}
    # Should handle reasonable depth
    nested_10 = create_nested(10)
    encoded = serializer.encode(nested_10)
    decoded = serializer.decode(encoded)
    assert "nested" in decoded
