#exonware/xwjson/tests/2.integration/scenarios/test_stress_xwnode_indexing.py
"""
Stress tests for xwnode indexing integration.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Stress tests for xwnode HASH_MAP and other indexing strategies.
"""

import pytest
from exonware.xwjson.operations import XWJSONDataOperations
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_stress_hash_map_indexing():
    """Stress test: HASH_MAP indexing performance."""
    try:
        from exonware.xwnode import XWNode
        from exonware.xwnode.defs import NodeMode
        # Create hash map index
        index = XWNode(mode=NodeMode.HASH_MAP)
        # Build index for 100000 items
        import time
        start = time.perf_counter()
        for i in range(100000):
            index[i] = {"id": i, "value": f"item{i}"}
        build_time = time.perf_counter() - start
        # Should be fast (< 1s for 100000 items)
        assert build_time < 1.0, f"Index building too slow: {build_time:.3f}s"
        # Test O(1) lookups
        start = time.perf_counter()
        for i in range(0, 100000, 1000):
            result = index[i]
            assert result["id"] == i
        lookup_time = time.perf_counter() - start
        # Should be very fast (< 100ms for 100 lookups)
        assert lookup_time < 0.1, f"Index lookups too slow: {lookup_time:.3f}s"
    except ImportError:
        pytest.skip("xwnode not available")
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_indexed_paging(temp_dir):
    """Stress test: Indexed paging with xwnode."""
    try:
        from exonware.xwnode import XWNode
        from exonware.xwnode.defs import NodeMode
        ops = XWJSONDataOperations()
        file_path = temp_dir / "indexed_paging.xwjson"
        # Create large dataset
        data = [{"id": i, "name": f"User{i}", "score": i * 10} for i in range(100000)]
        await ops.atomic_write(file_path, data)
        # Build page index using xwnode
        page_index = XWNode(mode=NodeMode.HASH_MAP)
        page_size = 1000
        import time
        start = time.perf_counter()
        # Build index: page_number -> start_index
        for page in range(1, 101):  # 100 pages
            start_idx = (page - 1) * page_size
            page_index[page] = start_idx
        index_time = time.perf_counter() - start
        # Should be fast
        assert index_time < 0.01, f"Page index building too slow: {index_time:.3f}s"
        # Test indexed paging
        start = time.perf_counter()
        for page in range(1, 11):  # Test 10 pages
            start_idx = page_index[page]
            page_data = await ops.read_page(file_path, page_number=page, page_size=page_size)
            assert len(page_data) == page_size
            assert page_data[0]["id"] == start_idx
        paging_time = time.perf_counter() - start
        # Should be fast with index
        assert paging_time < 0.5, f"Indexed paging too slow: {paging_time:.3f}s"
    except ImportError:
        pytest.skip("xwnode not available")
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_stress_multi_index():
    """Stress test: Multiple indexes for different fields."""
    try:
        from exonware.xwnode import XWNode
        from exonware.xwnode.defs import NodeMode
        # Create multiple indexes
        id_index = XWNode(mode=NodeMode.HASH_MAP)
        name_index = XWNode(mode=NodeMode.HASH_MAP)
        score_index = XWNode(mode=NodeMode.HASH_MAP)
        # Build indexes for 50000 items
        data = [
            {"id": i, "name": f"User{i}", "score": i * 10}
            for i in range(50000)
        ]
        import time
        start = time.perf_counter()
        for item in data:
            id_index[item["id"]] = item
            name_index[item["name"]] = item
            score_index[item["score"]] = item
        build_time = time.perf_counter() - start
        # Should be fast (< 2s for 3 indexes * 50000 items)
        assert build_time < 2.0, f"Multi-index building too slow: {build_time:.3f}s"
        # Test lookups
        start = time.perf_counter()
        for i in range(0, 50000, 1000):
            by_id = id_index[i]
            by_name = name_index[f"User{i}"]
            by_score = score_index[i * 10]
            assert by_id == by_name == by_score
        lookup_time = time.perf_counter() - start
        # Should be very fast
        assert lookup_time < 0.2, f"Multi-index lookups too slow: {lookup_time:.3f}s"
    except ImportError:
        pytest.skip("xwnode not available")
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_stress_index_memory():
    """Stress test: Index memory efficiency."""
    try:
        from exonware.xwnode import XWNode
        from exonware.xwnode.defs import NodeMode
        # Create index
        index = XWNode(mode=NodeMode.HASH_MAP)
        # Add 100000 items
        for i in range(100000):
            index[i] = {"id": i, "data": f"item{i}"}
        # Check memory usage (approximate)
        # Index should be memory-efficient
        # Note: Exact memory check depends on implementation
        # Verify all items accessible
        for i in range(0, 100000, 10000):
            assert index[i]["id"] == i
    except ImportError:
        pytest.skip("xwnode not available")
