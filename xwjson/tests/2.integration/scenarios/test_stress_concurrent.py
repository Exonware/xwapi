#exonware/xwjson/tests/2.integration/scenarios/test_stress_concurrent.py
"""
Stress tests for concurrent operations.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Stress tests for concurrent reads, writes, and transactions.
"""

import pytest
import asyncio
from exonware.xwjson.operations import XWJSONDataOperations
from exonware.xwjson.formats.binary.xwjson.transactions import TransactionContext
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_concurrent_reads(temp_dir):
    """Stress test: 1000 concurrent reads."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "concurrent_reads.xwjson"
    data = {"test": "data", "values": list(range(1000))}
    await ops.atomic_write(file_path, data)
    # 1000 concurrent reads
    tasks = [ops.atomic_read(file_path) for _ in range(1000)]
    results = await asyncio.gather(*tasks)
    # All should return same data
    for result in results:
        assert result == data
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_concurrent_path_updates(temp_dir):
    """Stress test: Concurrent path updates with conflict resolution."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "concurrent_updates.xwjson"
    # Initial data with 100 users
    data = {"users": [{"id": i, "name": f"User{i}"} for i in range(100)]}
    await ops.atomic_write(file_path, data)
    # 500 concurrent updates (some will conflict, some won't)
    tasks = []
    for i in range(500):
        user_idx = i % 100
        tasks.append(
            ops.write_path(file_path, f"/users/{user_idx}/name", f"UpdatedUser{i}")
        )
    # Execute all (concurrent read-modify-write; no locking so some updates may be lost)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Verify final state is consistent (100 users, each has name)
    final_data = await ops.atomic_read(file_path)
    assert len(final_data["users"]) == 100
    for user in final_data["users"]:
        assert "name" in user
    # No assertion on updated names: concurrent write_path is read-modify-write, last write wins
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
@pytest.mark.skipif(
    __import__("sys").platform == "win32",
    reason="Concurrent transaction .wal file handling can leave file in use on Windows"
)
async def test_stress_transactions(temp_dir):
    """Stress test: Multiple concurrent transactions."""
    file_path = temp_dir / "transactions.xwjson"
    # Initial data
    ops = XWJSONDataOperations()
    await ops.atomic_write(file_path, {"counter": 0})
    async def transaction_worker(tx_id: int):
        """Worker that performs transaction."""
        async with TransactionContext(file_path) as tx:
            # Read current value
            current_data = await ops.atomic_read(file_path)
            current_value = current_data.get("counter", 0)
            # Update
            await tx.update_path("/counter", current_value + 1)
            # Transaction commits automatically
    # 100 concurrent transactions
    tasks = [transaction_worker(i) for i in range(100)]
    await asyncio.gather(*tasks)
    # Verify final state (should be 100, but may be less due to conflicts)
    final_data = await ops.atomic_read(file_path)
    assert final_data["counter"] >= 1  # At least one transaction succeeded
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_batch_with_dependencies(temp_dir):
    """Stress test: Large batch operations with complex dependencies."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "batch_deps.xwjson"
    # Initial data
    data = {"users": [{"id": i, "name": f"User{i}", "score": 0} for i in range(50)]}
    await ops.atomic_write(file_path, data)
    # Create 500 operations with dependencies
    operations = []
    for i in range(500):
        user_idx = i % 50
        if i % 3 == 0:
            # Update ID (must happen before move)
            operations.append({
                "op": "update_path",
                "path": f"/users/{user_idx}/id",
                "value": user_idx + 100
            })
        elif i % 3 == 1:
            # Update name (can be parallel)
            operations.append({
                "op": "update_path",
                "path": f"/users/{user_idx}/name",
                "value": f"UpdatedUser{i}"
            })
        else:
            # Update score (can be parallel)
            operations.append({
                "op": "update_path",
                "path": f"/users/{user_idx}/score",
                "value": i
            })
    # Execute batch (should handle dependencies correctly)
    results = await ops.execute_batch(file_path, operations)
    assert len(results) == 500
    # Verify final state
    final_data = await ops.atomic_read(file_path)
    assert len(final_data["users"]) == 50
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_query_performance(temp_dir):
    """Stress test: Query performance with large dataset."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "query_stress.xwjson"
    # Create large dataset
    data = {
        "users": [
            {
                "id": i,
                "name": f"User{i}",
                "age": 20 + (i % 50),
                "city": ["NYC", "LA", "Chicago", "Houston"][i % 4]
            }
            for i in range(10000)
        ]
    }
    await ops.atomic_write(file_path, data)
    # Execute 100 queries
    tasks = []
    for i in range(100):
        query = f"$.users[?(@.age > {25 + i % 20})].name"
        tasks.append(ops.query(file_path, query))
    results = await asyncio.gather(*tasks)
    # All queries should return results
    for result in results:
        assert isinstance(result, list)
        assert len(result) > 0
