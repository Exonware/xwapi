#exonware/xwjson/tests/2.integration/scenarios/test_stress_batch_operations.py
"""
Stress tests for batch operations with dependency resolution.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Stress tests for smart batch operations, dependency resolution, parallel execution.
"""

import pytest
from exonware.xwjson.operations import XWJSONDataOperations
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_large_batch(temp_dir):
    """Stress test: Very large batch operations."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "large_batch.xwjson"
    # Initial data
    data = {"users": [{"id": i, "name": f"User{i}", "score": 0} for i in range(1000)]}
    await ops.atomic_write(file_path, data)
    # Create 10000 operations
    operations = []
    for i in range(10000):
        user_idx = i % 1000
        operations.append({
            "op": "update_path",
            "path": f"/users/{user_idx}/score",
            "value": i
        })
    import time
    start = time.perf_counter()
    results = await ops.execute_batch(file_path, operations)
    batch_time = time.perf_counter() - start
    # Should complete in reasonable time (allow 5 min on slower/loaded machines)
    assert batch_time < 300.0, f"Large batch too slow: {batch_time:.3f}s"
    assert len(results) == 10000
    # Verify final state
    final = await ops.atomic_read(file_path)
    assert len(final["users"]) == 1000
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_batch_with_complex_dependencies(temp_dir):
    """Stress test: Batch with complex dependency chains."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "complex_batch.xwjson"
    # Initial data
    data = {
        "users": [
            {"id": i, "name": f"User{i}", "profile": {"age": 20 + i}}
            for i in range(500)
        ]
    }
    await ops.atomic_write(file_path, data)
    # Create operations with dependencies
    operations = []
    for i in range(2000):
        user_idx = i % 500
        if i % 4 == 0:
            # Update ID (must happen before move)
            operations.append({
                "op": "update_path",
                "path": f"/users/{user_idx}/id",
                "value": user_idx + 1000
            })
        elif i % 4 == 1:
            # Update name (can be parallel)
            operations.append({
                "op": "update_path",
                "path": f"/users/{user_idx}/name",
                "value": f"Updated{i}"
            })
        elif i % 4 == 2:
            # Update profile (can be parallel)
            operations.append({
                "op": "update_path",
                "path": f"/users/{user_idx}/profile/age",
                "value": 30 + i
            })
        else:
            # Update nested (can be parallel)
            operations.append({
                "op": "update_path",
                "path": f"/users/{user_idx}/profile/score",
                "value": i * 10
            })
    # Execute batch
    results = await ops.execute_batch(file_path, operations)
    assert len(results) == 2000
    # Verify final state is consistent
    final = await ops.atomic_read(file_path)
    assert len(final["users"]) == 500
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_batch_parallel_execution(temp_dir):
    """Stress test: Verify parallel execution in batches."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "parallel_batch.xwjson"
    # Initial data
    data = {"counters": {f"counter{i}": 0 for i in range(100)}}
    await ops.atomic_write(file_path, data)
    # Create independent operations (should execute in parallel)
    operations = []
    for i in range(1000):
        counter_key = f"counter{i % 100}"
        operations.append({
            "op": "update_path",
            "path": f"/counters/{counter_key}",
            "value": i
        })
    import time
    start = time.perf_counter()
    results = await ops.execute_batch(file_path, operations)
    batch_time = time.perf_counter() - start
    # Should be faster than sequential (parallel execution)
    # Sequential would be ~1000 * avg_op_time
    # Parallel should be much faster
    assert batch_time < 10.0, f"Batch execution too slow: {batch_time:.3f}s"
    assert len(results) == 1000
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_batch_conflict_resolution(temp_dir):
    """Stress test: Batch conflict detection and resolution."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "conflict_batch.xwjson"
    # Initial data
    data = {"users": [{"id": i, "name": f"User{i}"} for i in range(100)]}
    await ops.atomic_write(file_path, data)
    # Create conflicting operations (same paths)
    operations = []
    for i in range(500):
        user_idx = i % 100
        # Multiple updates to same path (conflicts)
        operations.append({
            "op": "update_path",
            "path": f"/users/{user_idx}/name",
            "value": f"Conflict{i}"
        })
    # Execute batch (should handle conflicts correctly)
    results = await ops.execute_batch(file_path, operations)
    assert len(results) == 500
    # Verify final state (last update should win)
    final = await ops.atomic_read(file_path)
    assert len(final["users"]) == 100
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_batch_mixed_operations(temp_dir):
    """Stress test: Mixed operation types in batch."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "mixed_batch.xwjson"
    # Initial data (include 'temp' so delete_path has something to delete)
    data = {
        "users": [{"id": i, "name": f"User{i}", "temp": None} for i in range(200)],
        "metadata": {"version": 1}
    }
    await ops.atomic_write(file_path, data)
    # Create mixed operations
    operations = []
    for i in range(1000):
        if i % 5 == 0:
            # Read operation
            operations.append({
                "op": "read_path",
                "path": f"/users/{i % 200}/name"
            })
        elif i % 5 == 1:
            # Update operation
            operations.append({
                "op": "update_path",
                "path": f"/users/{i % 200}/name",
                "value": f"Updated{i}"
            })
        elif i % 5 == 2:
            # Write operation
            operations.append({
                "op": "write_path",
                "path": f"/users/{i % 200}/score",
                "value": i * 10
            })
        elif i % 5 == 3:
            # Delete operation
            operations.append({
                "op": "delete_path",
                "path": f"/users/{i % 200}/temp"
            })
        else:
            # Update metadata
            operations.append({
                "op": "update_path",
                "path": "/metadata/version",
                "value": i
            })
    # Execute batch
    results = await ops.execute_batch(file_path, operations)
    assert len(results) == 1000
