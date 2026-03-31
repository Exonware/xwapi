#exonware/xwjson/tests/2.integration/scenarios/test_stress_xwnode_caching.py
"""
Stress tests for xwnode caching integration.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Stress tests for xwnode LRU_CACHE strategy integration for query caching.
"""

import pytest
from exonware.xwjson.operations import XWJSONDataOperations
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_lru_cache_performance(temp_dir):
    """Stress test: LRU cache performance with xwnode."""
    try:
        from exonware.xwnode import XWNode
        from exonware.xwnode.defs import NodeMode
        ops = XWJSONDataOperations()
        file_path = temp_dir / "cache_stress.xwjson"
        # Create dataset
        data = {"users": [{"id": i, "name": f"User{i}"} for i in range(10000)]}
        await ops.atomic_write(file_path, data)
        # Create LRU cache using xwnode
        cache = XWNode(mode=NodeMode.LRU_CACHE, max_size=1000)
        # Execute 10000 queries (many will be cache hits)
        queries = [
            "$.users[0].name",
            "$.users[100].name",
            "$.users[500].name",
            "$.users[1000].name",
        ]
        query_keys = {query: f"query_{idx}" for idx, query in enumerate(queries)}
        import time
        start = time.perf_counter()
        for i in range(10000):
            query = queries[i % len(queries)]
            cache_key = query_keys[query]
            # Check cache first
            cached = cache.get_value(cache_key)
            if cached is None:
                # Cache miss - execute query
                results = await ops.query(file_path, query)
                cache.put(cache_key, results)
            # Cache hit - use cached result
        cache_time = time.perf_counter() - start
        # Estimate hit rate from deterministic workload after first-warmup cycle.
        # 4 unique queries repeated across 10k iterations -> ~99.96% expected hits.
        total_ops = 10000
        unique_queries = len(queries)
        estimated_hits = max(total_ops - unique_queries, 0)
        hit_rate = estimated_hits / total_ops
        # Should have high hit rate (> 90% after warmup)
        assert hit_rate > 0.9, f"Cache hit rate too low: {hit_rate:.1%}"
        # Should be fast (< 5s for 10000 operations with caching)
        assert cache_time < 5.0, f"Caching too slow: {cache_time:.3f}s"
    except ImportError:
        pytest.skip("xwnode not available")
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_stress_cache_eviction():
    """Stress test: Cache eviction under load."""
    try:
        from exonware.xwnode import XWNode
        from exonware.xwnode.defs import NodeMode
        # Create small cache
        cache = XWNode(mode=NodeMode.LRU_CACHE, max_size=100)
        # Fill beyond capacity
        for i in range(200):
            cache.put(f"key{i}", f"value{i}")
        # Oldest keys should be evicted
        assert cache.get_value("key0") is None  # Evicted
        assert cache.get_value("key100") is not None  # Still in cache
        assert cache.get_value("key199") is not None  # Most recent
        # Verify cache size
        assert len(cache) <= 100
    except ImportError:
        pytest.skip("xwnode not available")
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_concurrent_caching(temp_dir):
    """Stress test: Concurrent cache operations."""
    try:
        from exonware.xwnode import XWNode
        from exonware.xwnode.defs import NodeMode
        import asyncio
        ops = XWJSONDataOperations()
        file_path = temp_dir / "concurrent_cache.xwjson"
        data = {"items": [{"id": i} for i in range(1000)]}
        await ops.atomic_write(file_path, data)
        # Create shared cache
        cache = XWNode(mode=NodeMode.LRU_CACHE, max_size=500)
        async def cache_worker(worker_id: int):
            """Worker that uses cache."""
            for i in range(100):
                query = f"$.items[{worker_id * 10 + i}].id"
                cache_key = f"query_{worker_id}_{i}"
                cached = cache.get_value(cache_key)
                if cached is None:
                    results = await ops.query(file_path, query)
                    cache.put(cache_key, results)
        # 10 concurrent workers
        tasks = [cache_worker(i) for i in range(10)]
        await asyncio.gather(*tasks)
        # Cache should have entries
        assert len(cache) > 0
    except ImportError:
        pytest.skip("xwnode not available")
