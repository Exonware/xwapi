#exonware/xwjson/tests/3.advance/test_performance.py
"""
Performance excellence tests (Priority #4).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Performance tests: encoding/decoding speed, query performance, batch operations.
"""

import pytest
import time
from exonware.xwjson import XWJSONSerializer
from exonware.xwjson.operations import XWJSONDataOperations
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_performance


def test_encoding_performance():
    """Test encoding performance."""
    serializer = XWJSONSerializer()
    # Medium-sized data
    data = {
        "users": [
            {"id": i, "name": f"User{i}", "data": {f"key{j}": f"value{j}" for j in range(50)}}
            for i in range(1000)
        ]
    }
    # Time encoding
    start = time.perf_counter()
    encoded = serializer.encode(data)
    encode_time = time.perf_counter() - start
    # Should be fast (< 100ms for 1000 items)
    assert encode_time < 0.1, f"Encoding too slow: {encode_time:.3f}s"
    # Verify size is reasonable
    assert len(encoded) < len(str(data)) * 2  # Binary should be more compact
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_performance


def test_decoding_performance():
    """Test decoding performance."""
    serializer = XWJSONSerializer()
    # Create encoded data
    data = {"items": [{"id": i, "value": f"item{i}"} for i in range(5000)]}
    encoded = serializer.encode(data)
    # Time decoding
    start = time.perf_counter()
    decoded = serializer.decode(encoded)
    decode_time = time.perf_counter() - start
    # Should be fast (< 50ms for 5000 items)
    assert decode_time < 0.05, f"Decoding too slow: {decode_time:.3f}s"
    assert decoded == data
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_query_performance(temp_dir):
    """Test query performance."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "query_perf.xwjson"
    # Create dataset
    data = {
        "users": [
            {"id": i, "name": f"User{i}", "age": 20 + (i % 50), "city": ["NYC", "LA"][i % 2]}
            for i in range(10000)
        ]
    }
    await ops.atomic_write(file_path, data)
    # Time query
    start = time.perf_counter()
    results = await ops.query(file_path, "$.users[?(@.age > 30)].name")
    query_time = time.perf_counter() - start
    # Should be reasonably fast (< 5s for 10000 items with JSONPath)
    # Note: JSONPath queries can be slower than native queries
    assert query_time < 5.0, f"Query too slow: {query_time:.3f}s"
    assert len(results) > 0
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_batch_performance(temp_dir):
    """Test batch operations performance."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "batch_perf.xwjson"
    # Initial data
    data = {"users": [{"id": i, "name": f"User{i}"} for i in range(100)]}
    await ops.atomic_write(file_path, data)
    # Create 1000 operations
    operations = [
        {"op": "update_path", "path": f"/users/{i % 100}/name", "value": f"Updated{i}"}
        for i in range(1000)
    ]
    # Time batch execution
    start = time.perf_counter()
    results = await ops.execute_batch(file_path, operations)
    batch_time = time.perf_counter() - start
    # Should be faster than sequential (parallel execution)
    # Sequential would be ~1000 * avg_op_time, batch should be much faster
    assert batch_time < 5.0, f"Batch too slow: {batch_time:.3f}s"
    assert len(results) == 1000
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_paging_performance(temp_dir):
    """Test paging performance."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "paging_perf.xwjson"
    # Create large dataset
    data = [{"id": i, "value": f"item{i}"} for i in range(100000)]
    await ops.atomic_write(file_path, data)
    # Time paging
    start = time.perf_counter()
    page = await ops.read_page(file_path, page_number=50, page_size=1000)
    page_time = time.perf_counter() - start
    # Should be fast (< 100ms for any page)
    assert page_time < 0.1, f"Paging too slow: {page_time:.3f}s"
    assert len(page) == 1000
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_performance


def test_hybrid_parser_performance():
    """Test hybrid parser (orjson/msgspec) performance."""
    try:
        from exonware.xwjson.formats.binary.xwjson.encoder import XWJSONHybridParser
        parser = XWJSONHybridParser()
        # Large data
        data = {"items": [{"id": i, "value": f"item{i}" * 10} for i in range(10000)]}
        # Time encoding (orjson)
        start = time.perf_counter()
        encoded = parser.dumps(data)
        encode_time = time.perf_counter() - start
        # Time decoding (msgspec)
        start = time.perf_counter()
        decoded = parser.loads(encoded)
        decode_time = time.perf_counter() - start
        # Both should be fast
        assert encode_time < 0.05, f"orjson encoding too slow: {encode_time:.3f}s"
        assert decode_time < 0.05, f"msgspec decoding too slow: {decode_time:.3f}s"
        assert decoded == data
    except ImportError:
        pytest.skip("msgspec or orjson not available")
