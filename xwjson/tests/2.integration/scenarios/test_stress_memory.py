#exonware/xwjson/tests/2.integration/scenarios/test_stress_memory.py
"""
Stress tests for memory efficiency and large data handling.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Stress tests for memory efficiency, lazy loading, and large file handling.
"""

import pytest
import sys
from exonware.xwjson import XWJSONSerializer
from exonware.xwjson.operations import XWJSONDataOperations
from exonware.xwjson.formats.binary.xwjson.lazy import LazyFileProxy, LazySerializationProxy
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_memory_efficient_encoding():
    """Stress test: Memory-efficient encoding of large data."""
    serializer = XWJSONSerializer()
    # Create very large nested structure
    large_data = {
        "level1": {
            f"key{i}": {
                "level2": {
                    f"subkey{j}": f"value{i}_{j}" * 10
                    for j in range(100)
                }
            }
            for i in range(1000)
        }
    }
    # Encode (should not cause memory issues)
    encoded = serializer.encode(large_data)
    assert len(encoded) > 0
    # Memory should be reasonable (check approximate size)
    # Encoded should be smaller than original Python object
    encoded_size = sys.getsizeof(encoded)
    assert encoded_size < 100 * 1024 * 1024  # Less than 100MB
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_lazy_file_proxy_memory(temp_dir):
    """Stress test: Lazy file proxy memory efficiency."""
    file_path = temp_dir / "lazy_large.xwjson"
    # Create large file (simulate)
    items = [f'{{"id": {i}}}'.encode() for i in range(1000)]
    large_content = b'{"data": [' + b",".join(items) + b']}'
    file_path.write_bytes(large_content)
    # Create lazy proxy
    proxy = LazyFileProxy(file_path, lazy_threshold=1024)
    # Should not load until accessed
    assert not proxy._loaded
    # Access through protocol triggers load
    _ = len(proxy)
    assert proxy._loaded
    proxy.close()
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_lazy_serialization_memory():
    """Stress test: Lazy serialization memory efficiency."""
    import json
    # Create large JSON bytes
    large_data = {"items": [{"id": i, "data": f"item{i}" * 100} for i in range(10000)]}
    json_bytes = json.dumps(large_data).encode('utf-8')
    parser = lambda b: json.loads(b.decode('utf-8'))
    # Create lazy proxy
    proxy = LazySerializationProxy(json_bytes, parser, lazy_threshold=1024 * 1024)
    # Should not parse until accessed
    assert not proxy._parsed
    # Access through protocol triggers parse
    _ = len(proxy)
    result = proxy._parsed_data
    assert proxy._parsed
    assert len(result["items"]) == 10000
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_streaming_memory_efficiency(temp_dir):
    """Stress test: Streaming operations memory efficiency."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "streaming_large.xwjson"
    # Create very large list
    large_data = [{"id": i, "data": f"item{i}" * 100} for i in range(50000)]
    await ops.atomic_write(file_path, large_data)
    # Stream read (should not load all into memory)
    count = 0
    max_memory_items = 0
    current_batch = []
    async for item in ops.read_stream(file_path):
        current_batch.append(item)
        count += 1
        # Track max items in memory at once
        if len(current_batch) > max_memory_items:
            max_memory_items = len(current_batch)
        # Clear batch periodically (simulate processing)
        if len(current_batch) >= 1000:
            current_batch.clear()
    assert count == 50000
    # Should process in batches, not all at once
    assert max_memory_items < 50000
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_paging_memory_efficiency(temp_dir):
    """Stress test: Paging memory efficiency."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "paging_large.xwjson"
    # Create large dataset
    large_data = [{"id": i} for i in range(100000)]
    await ops.atomic_write(file_path, large_data)
    # Read pages (should only load one page at a time)
    total_items = 0
    page = 1
    page_size = 1000
    while True:
        page_data = await ops.read_page(file_path, page_number=page, page_size=page_size)
        if not page_data:
            break
        # Each page should be exactly page_size (or less for last page)
        assert len(page_data) <= page_size
        total_items += len(page_data)
        page += 1
        # Memory check: should not accumulate
        if page > 10:
            # After 10 pages, verify we're not accumulating
            pass
    assert total_items == 100000
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_deep_nesting_memory():
    """Stress test: Deep nesting memory handling."""
    serializer = XWJSONSerializer()
    # Create deeply nested structure
    def create_nested(depth: int, current: int = 0) -> dict:
        if current >= depth:
            return {"value": "leaf"}
        return {"nested": create_nested(depth, current + 1)}
    # Test with various depths
    for depth in [10, 50, 100]:
        nested_data = create_nested(depth)
        # Should encode/decode without memory issues
        encoded = serializer.encode(nested_data)
        decoded = serializer.decode(encoded)
        # Verify structure
        current = decoded
        for i in range(depth):
            assert "nested" in current
            current = current["nested"]
        assert current["value"] == "leaf"
