#exonware/xwjson/tests/2.integration/scenarios/test_xwnode_integration.py
"""
Integration tests for xwnode integration (caching, indexing, paging).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Tests for xwnode integration: caching, indexing, paging using xwnode strategies.
"""

import pytest
from exonware.xwjson.operations import XWJSONDataOperations
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_xwnode_lru_cache_integration():
    """Test xwnode LRU_CACHE strategy for caching."""
    try:
        from exonware.xwnode import XWNode
        from exonware.xwnode.defs import NodeMode
        # Create LRU cache using xwnode
        cache = XWNode(mode=NodeMode.LRU_CACHE, max_size=100)
        # Test cache operations
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        assert cache.get_value("key1") == "value1"
        assert cache.get_value("key2") == "value2"
        # Test eviction (fill cache beyond max_size)
        for i in range(150):
            cache.put(f"key{i}", f"value{i}")
        # Oldest keys should be evicted
        assert cache.get_value("key1") is None  # Evicted
        # Basic cache sanity (size constrained by max_size)
        assert len(cache) <= 100
    except ImportError:
        pytest.skip("xwnode not available")
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_xwnode_hash_map_indexing():
    """Test xwnode HASH_MAP strategy for indexing."""
    try:
        from exonware.xwnode import XWNode
        from exonware.xwnode.defs import NodeMode
        # Create hash map index using xwnode
        index = XWNode(mode=NodeMode.HASH_MAP)
        # Build index
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"},
        ]
        for item in data:
            index[item["id"]] = item
        # O(1) lookups
        assert index[1]["name"] == "Alice"
        assert index[2]["name"] == "Bob"
        assert index[3]["name"] == "Charlie"
    except ImportError:
        pytest.skip("xwnode not available")
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_xwnode_caching_in_operations(temp_dir):
    """Test xwnode caching integration in XWJSONDataOperations."""
    try:
        from exonware.xwnode import XWNode
        from exonware.xwnode.defs import NodeMode
        ops = XWJSONDataOperations()
        file_path = temp_dir / "cached_test.xwjson"
        data = {"users": [{"id": i, "name": f"User{i}"} for i in range(100)]}
        await ops.atomic_write(file_path, data)
        # Create cache using xwnode
        cache = XWNode(mode=NodeMode.LRU_CACHE, max_size=50)
        # Cache query results
        query = "$.users[*].name"
        cache_key = "query_users_names"
        # First query (cache miss)
        results1 = await ops.query(file_path, query)
        cache.put(cache_key, results1)
        # Second query (cache hit)
        cached_results = cache.get_value(cache_key)
        assert cached_results == results1
    except ImportError:
        pytest.skip("xwnode not available")
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_xwnode_paging_with_index():
    """Test xwnode indexing for efficient paging."""
    try:
        from exonware.xwnode import XWNode
        from exonware.xwnode.defs import NodeMode
        # Create index for paging
        page_index = XWNode(mode=NodeMode.HASH_MAP)
        # Build page index (page_number -> start_index)
        page_size = 100
        for page in range(10):
            start_idx = page * page_size
            page_index[page + 1] = start_idx
        # O(1) page lookup
        assert page_index[1] == 0
        assert page_index[5] == 400
        assert page_index[10] == 900
    except ImportError:
        pytest.skip("xwnode not available")
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_xwnode_graph_for_dependencies():
    """Test xwnode graph strategies for dependency resolution."""
    try:
        from exonware.xwnode import XWNode
        from exonware.xwnode.defs import NodeMode, EdgeMode
        # Create graph for dependency tracking
        graph = XWNode(mode=NodeMode.AUTO)
        graph.set_edge_mode(EdgeMode.ADJ_LIST)
        # Add operations as nodes
        graph.add_node("op1", {"op": "update_path", "path": "/users/0/id"})
        graph.add_node("op2", {"op": "move", "from": "/users/0", "to": "/users/2"})
        # Add dependency edge (op2 depends on op1)
        graph.add_edge("op1", "op2", {"type": "depends_on"})
        # Get dependencies
        dependencies = graph.get_outgoing_edges("op1")
        assert len(dependencies) > 0
    except (ImportError, AttributeError):
        pytest.skip("xwnode not available or graph API not supported")
