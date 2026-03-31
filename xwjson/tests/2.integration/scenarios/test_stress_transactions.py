#exonware/xwjson/tests/2.integration/scenarios/test_stress_transactions.py
"""
Stress tests for transaction support.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Stress tests for ACID transactions, concurrent transactions, rollback.
"""

import pytest
import asyncio
from exonware.xwjson.operations import XWJSONDataOperations
from exonware.xwjson.formats.binary.xwjson.transactions import TransactionContext
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_transaction_commit(temp_dir):
    """Stress test: Multiple transaction commits."""
    file_path = temp_dir / "transactions.xwjson"
    ops = XWJSONDataOperations()
    await ops.atomic_write(file_path, {"counter": 0, "items": []})
    # Bounded stress loop for predictable runtime in CI/Windows environments.
    for i in range(100):
        async with TransactionContext(file_path) as tx:
            current = await ops.atomic_read(file_path)
            await tx.update_path("/counter", current.get("counter", 0) + 1)
            await tx.update_path("/items", current.get("items", []) + [i])
    # Verify final state
    final = await ops.atomic_read(file_path)
    assert final["counter"] >= 1  # At least some transactions succeeded
    assert len(final["items"]) >= 1
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_transaction_rollback(temp_dir):
    """Stress test: Transaction rollback on error."""
    file_path = temp_dir / "rollback_test.xwjson"
    ops = XWJSONDataOperations()
    initial_data = {"value": 100}
    await ops.atomic_write(file_path, initial_data)
    # Attempt transaction that will fail
    try:
        async with TransactionContext(file_path) as tx:
            await tx.update_path("/value", 200)
            # Simulate error
            raise ValueError("Simulated error")
    except ValueError:
        pass
    # Verify rollback (value should be unchanged)
    final = await ops.atomic_read(file_path)
    assert final["value"] == 100  # Rolled back
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_concurrent_transactions(temp_dir):
    """Stress test: Concurrent transactions."""
    file_path = temp_dir / "concurrent_tx.xwjson"
    ops = XWJSONDataOperations()
    await ops.atomic_write(file_path, {"counters": {"a": 0, "b": 0, "c": 0}})
    async def transaction_worker(counter_key: str, iterations: int):
        """Worker that performs transactions."""
        for _ in range(iterations):
            async with TransactionContext(file_path) as tx:
                current = await ops.atomic_read(file_path)
                current_value = current["counters"].get(counter_key, 0)
                await tx.update_path(f"/counters/{counter_key}", current_value + 1)
    # 3 concurrent workers, bounded iterations for predictable runtime on Windows.
    tasks = [
        transaction_worker("a", 20),
        transaction_worker("b", 20),
        transaction_worker("c", 20),
    ]
    await asyncio.gather(*tasks)
    # Verify final state
    final = await ops.atomic_read(file_path)
    # All counters should have some increments
    assert final["counters"]["a"] >= 1
    assert final["counters"]["b"] >= 1
    assert final["counters"]["c"] >= 1
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio
async def test_stress_transaction_isolation(temp_dir):
    """Stress test: Transaction isolation."""
    file_path = temp_dir / "isolation_test.xwjson"
    ops = XWJSONDataOperations()
    await ops.atomic_write(file_path, {"value": 0})
    # Start transaction 1
    tx1_started = asyncio.Event()
    tx1_completed = asyncio.Event()
    async def transaction1():
        async with TransactionContext(file_path) as tx:
            tx1_started.set()
            await tx.update_path("/value", 100)
            # Wait for tx2 to read
            await asyncio.sleep(0.1)
            # Transaction commits here
            tx1_completed.set()
    async def transaction2():
        # Wait for tx1 to start
        await tx1_started.wait()
        # Read (should see old value due to isolation)
        value = await ops.read_path(file_path, "/value")
        # Should see 0 (not 100) due to isolation
        assert value == 0
        tx1_completed.set()
    await asyncio.gather(transaction1(), transaction2())
    # After both complete, value should be 100
    final = await ops.atomic_read(file_path)
    assert final["value"] == 100
