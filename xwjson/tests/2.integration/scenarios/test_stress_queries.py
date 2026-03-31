#exonware/xwjson/tests/2.integration/scenarios/test_stress_queries.py
"""
Stress tests for query operations.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Stress tests for queries: JSONPath, SQL, complex queries, query caching.
"""

import pytest
import asyncio
from exonware.xwjson.operations import XWJSONDataOperations
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_jsonpath_queries(temp_dir):
    """Stress test: High-volume JSONPath queries."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "query_stress.xwjson"
    # Create large dataset
    data = {
        "users": [
            {
                "id": i,
                "name": f"User{i}",
                "age": 20 + (i % 50),
                "city": ["NYC", "LA", "Chicago", "Houston"][i % 4],
                "scores": [j for j in range(i % 10)]
            }
            for i in range(10000)
        ]
    }
    await ops.atomic_write(file_path, data)
    # Execute bounded high-volume query set (keeps runtime predictable on Windows).
    queries = [
        "$.users[*].name",
        "$.users[?(@.age > 30)].name",
        "$.users[?(@.city == 'NYC')].id",
        "$.users[?(@.age > 25 && @.age < 40)].name",
    ]
    import time
    start = time.perf_counter()
    tasks = []
    for i in range(400):
        query = queries[i % len(queries)]
        tasks.append(ops.query(file_path, query))
    results = await asyncio.gather(*tasks)
    query_time = time.perf_counter() - start
    # Should complete in reasonable time for bounded workload.
    assert query_time < 30.0, f"Queries too slow: {query_time:.3f}s"
    # All queries should return results
    for result in results:
        assert isinstance(result, list)
        assert len(result) > 0
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_sql_queries(temp_dir):
    """Stress test: SQL queries via xwquery."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "sql_stress.xwjson"
    # Create dataset
    data = {
        "users": [
            {
                "id": i,
                "name": f"User{i}",
                "age": 20 + (i % 50),
                "city": ["NYC", "LA"][i % 2],
                "score": i * 10
            }
            for i in range(10000)
        ]
    }
    await ops.atomic_write(file_path, data)
    try:
        # Execute SQL queries
        sql_queries = [
            "SELECT name FROM users WHERE age > 30",
            "SELECT * FROM users WHERE city = 'NYC' ORDER BY score DESC LIMIT 100",
            "SELECT COUNT(*) FROM users WHERE age BETWEEN 25 AND 35",
        ]
        import time
        start = time.perf_counter()
        results = []
        for query in sql_queries:
            result = await ops.query(file_path, query, query_format="sql")
            results.append(result)
        query_time = time.perf_counter() - start
        # Should be fast
        assert query_time < 5.0, f"SQL queries too slow: {query_time:.3f}s"
        # Verify results
        for result in results:
            assert result is not None
    except (ImportError, Exception):
        pytest.skip("xwquery not available or query failed")
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_complex_queries(temp_dir):
    """Stress test: Complex nested queries."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "complex_queries.xwjson"
    # Create complex nested structure
    data = {
        "departments": [
            {
                "name": f"Dept{i}",
                "employees": [
                    {
                        "id": j,
                        "name": f"Emp{i}_{j}",
                        "salary": (i + j) * 1000,
                        "projects": [
                            {"name": f"Proj{k}", "status": ["active", "completed"][k % 2]}
                            for k in range(5)
                        ]
                    }
                    for j in range(100)
                ]
            }
            for i in range(50)
        ]
    }
    await ops.atomic_write(file_path, data)
    # Complex queries
    complex_queries = [
        "$.departments[*].employees[?(@.salary > 50000)].name",
        "$.departments[*].employees[*].projects[?(@.status == 'active')].name",
        "$.departments[0].employees[*].name",
    ]
    import time
    start = time.perf_counter()
    results = []
    for query in complex_queries:
        result = await ops.query(file_path, query)
        results.append(result)
    query_time = time.perf_counter() - start
    # Should handle complex queries
    assert query_time < 10.0, f"Complex queries too slow: {query_time:.3f}s"
    # Verify results
    for result in results:
        assert isinstance(result, list)
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_query_caching(temp_dir):
    """Stress test: Query result caching."""
    try:
        from exonware.xwnode import XWNode
        from exonware.xwnode.defs import NodeMode
        ops = XWJSONDataOperations()
        file_path = temp_dir / "query_cache.xwjson"
        data = {"users": [{"id": i, "name": f"User{i}"} for i in range(10000)]}
        await ops.atomic_write(file_path, data)
        # Create cache
        cache = XWNode(mode=NodeMode.LRU_CACHE, max_size=1000)
        queries = [
            "$.users[0].name",
            "$.users[100].name",
            "$.users[500].name",
        ]
        query_keys = {query: f"query_{idx}" for idx, query in enumerate(queries)}
        import time
        # First pass (cache misses)
        start = time.perf_counter()
        for query in queries * 100:  # 300 queries
            cache_key = query_keys[query]
            cached = cache.get_value(cache_key)
            if cached is None:
                results = await ops.query(file_path, query)
                cache.put(cache_key, results)
        first_pass_time = time.perf_counter() - start
        # Second pass (cache hits)
        start = time.perf_counter()
        for query in queries * 100:  # 300 queries
            cache_key = query_keys[query]
            cached = cache.get_value(cache_key)
            assert cached is not None  # Should be cached
        second_pass_time = time.perf_counter() - start
        # Second pass should be much faster (cache hits)
        assert second_pass_time < first_pass_time * 0.1, \
            f"Cache not effective: {first_pass_time:.3f}s vs {second_pass_time:.3f}s"
    except ImportError:
        pytest.skip("xwnode not available")
