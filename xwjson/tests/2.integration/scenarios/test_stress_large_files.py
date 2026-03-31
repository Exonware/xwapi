#exonware/xwjson/tests/2.integration/scenarios/test_stress_large_files.py
"""
Stress tests for large file handling.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Stress tests for large files, memory efficiency, and performance.
"""

import pytest
import asyncio
from exonware.xwjson import XWJSONSerializer
from exonware.xwjson.operations import XWJSONDataOperations
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_encode_large_data():
    """Stress test: Encode large data structure."""
    serializer = XWJSONSerializer()
    # Create large nested structure
    large_data = {
        "users": [
            {
                "id": i,
                "name": f"User{i}",
                "data": {f"key{j}": f"value{j}" for j in range(100)}
            }
            for i in range(1000)
        ]
    }
    encoded = serializer.encode(large_data)
    assert len(encoded) > 0
    # Decode and verify
    decoded = serializer.decode(encoded)
    assert len(decoded["users"]) == 1000
    assert decoded["users"][0]["id"] == 0
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_concurrent_writes(temp_dir):
    """Stress test: Concurrent write operations."""
    ops = XWJSONDataOperations()
    # Create multiple files concurrently
    tasks = []
    for i in range(100):
        file_path = temp_dir / f"concurrent_{i}.xwjson"
        data = {"id": i, "data": f"test{i}"}
        tasks.append(ops.atomic_write(file_path, data))
    await asyncio.gather(*tasks)
    # Verify all files created
    for i in range(100):
        file_path = temp_dir / f"concurrent_{i}.xwjson"
        assert file_path.exists()
        loaded = await ops.atomic_read(file_path)
        assert loaded["id"] == i
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_large_paging(temp_dir):
    """Stress test: Paging with large dataset."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "large_paging.xwjson"
    # Create large list
    large_data = [{"id": i, "value": f"item{i}"} for i in range(10000)]
    await ops.atomic_write(file_path, large_data)
    # Read all pages
    all_items = []
    page = 1
    page_size = 100
    while True:
        page_data = await ops.read_page(file_path, page_number=page, page_size=page_size)
        if not page_data:
            break
        all_items.extend(page_data)
        page += 1
    assert len(all_items) == 10000
    assert all_items[0]["id"] == 0
    assert all_items[-1]["id"] == 9999
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_batch_operations(temp_dir):
    """Stress test: Large batch operations."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "batch_test.xwjson"
    # Initial data
    data = {"users": [{"id": i, "name": f"User{i}"} for i in range(100)]}
    await ops.atomic_write(file_path, data)
    # Create 1000 batch operations
    operations = []
    for i in range(1000):
        operations.append({
            "op": "update_path",
            "path": f"/users/{i % 100}/name",
            "value": f"UpdatedUser{i}"
        })
    # Execute batch
    results = await ops.execute_batch(file_path, operations)
    assert len(results) == 1000
    # Verify final structure (100 users, each has name)
    loaded = await ops.atomic_read(file_path)
    assert len(loaded["users"]) == 100
    for u in loaded["users"]:
        assert "name" in u
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_streaming(temp_dir):
    """Stress test: Streaming operations."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "streaming_test.xwjson"
    # Create large list
    large_data = [{"id": i} for i in range(5000)]
    await ops.atomic_write(file_path, large_data)
    # Stream read
    count = 0
    async for item in ops.read_stream(file_path):
        assert "id" in item
        count += 1
    assert count == 5000
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_stress_memory_efficiency():
    """Stress test: Memory efficiency with large data."""
    serializer = XWJSONSerializer()
    # Create very large structure
    large_data = {
        "data": [
            {f"key{i}": f"value{i}" * 100 for i in range(1000)}
            for _ in range(100)
        ]
    }
    # Encode (should not cause memory issues)
    encoded = serializer.encode(large_data)
    # Decode (should not cause memory issues)
    decoded = serializer.decode(encoded)
    assert len(decoded["data"]) == 100
    assert len(decoded["data"][0]) == 1000
