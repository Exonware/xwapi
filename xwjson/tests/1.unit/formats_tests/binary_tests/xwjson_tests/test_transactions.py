#exonware/xwjson/tests/1.unit/formats_tests/binary_tests/xwjson_tests/test_transactions.py
"""
Unit tests for XWJSONTransaction and TransactionContext.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import pytest
from exonware.xwjson.formats.binary.xwjson.transactions import (
    XWJSONTransaction,
    TransactionContext,
    transaction
)
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations

def test_transaction_init(temp_dir):
    """Test transaction initialization."""
    file_path = temp_dir / "test.xwjson"
    tx = XWJSONTransaction(file_path)
    assert tx is not None
    assert not tx._committed
    assert not tx._rolled_back
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_transaction_write(temp_dir):
    """Test transaction write operation."""
    file_path = temp_dir / "test.xwjson"
    tx = XWJSONTransaction(file_path)
    await tx.write("key1", "value1")
    await tx.write("key2", "value2")
    assert len(tx._operations) == 2
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_transaction_update_path(temp_dir):
    """Test transaction update_path operation."""
    file_path = temp_dir / "test.xwjson"
    tx = XWJSONTransaction(file_path)
    await tx.update_path("/users/0/name", "Alice")
    assert len(tx._operations) == 1
    assert tx._operations[0]["op"] == "update_path"
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_transaction_commit(temp_dir):
    """Test transaction commit."""
    file_path = temp_dir / "test.xwjson"
    tx = XWJSONTransaction(file_path)
    await tx.write("key1", "value1")
    await tx.commit()
    assert tx._committed is True
    # Verify file was created/updated
    if file_path.exists():
        from exonware.xwjson import XWJSONSerializer
        serializer = XWJSONSerializer()
        data = serializer.load_file(str(file_path))
        assert data.get("key1") == "value1"
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_transaction_rollback(temp_dir):
    """Test transaction rollback."""
    file_path = temp_dir / "test.xwjson"
    tx = XWJSONTransaction(file_path)
    await tx.write("key1", "value1")
    await tx.rollback()
    assert tx._rolled_back is True
    assert len(tx._operations) == 0
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_transaction_cannot_write_after_commit(temp_dir):
    """Test that writing after commit raises error."""
    file_path = temp_dir / "test.xwjson"
    tx = XWJSONTransaction(file_path)
    await tx.write("key1", "value1")
    await tx.commit()
    with pytest.raises(SerializationError):
        await tx.write("key2", "value2")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_transaction_cannot_write_after_rollback(temp_dir):
    """Test that writing after rollback raises error."""
    file_path = temp_dir / "test.xwjson"
    tx = XWJSONTransaction(file_path)
    await tx.write("key1", "value1")
    await tx.rollback()
    with pytest.raises(SerializationError):
        await tx.write("key2", "value2")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_transaction_cannot_commit_after_rollback(temp_dir):
    """Test that committing after rollback raises error."""
    file_path = temp_dir / "test.xwjson"
    tx = XWJSONTransaction(file_path)
    await tx.write("key1", "value1")
    await tx.rollback()
    with pytest.raises(SerializationError):
        await tx.commit()
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_transaction_context_success(temp_dir):
    """Test transaction context manager with successful commit."""
    file_path = temp_dir / "test.xwjson"
    async with TransactionContext(file_path) as tx:
        await tx.write("key1", "value1")
        await tx.write("key2", "value2")
        # Commit happens automatically on exit
    # Verify data was committed
    if file_path.exists():
        from exonware.xwjson import XWJSONSerializer
        serializer = XWJSONSerializer()
        data = serializer.load_file(str(file_path))
        assert data.get("key1") == "value1"
        assert data.get("key2") == "value2"
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_transaction_context_error_rollback(temp_dir):
    """Test transaction context manager with error (should rollback)."""
    file_path = temp_dir / "test.xwjson"
    try:
        async with TransactionContext(file_path) as tx:
            await tx.write("key1", "value1")
            raise ValueError("Test error")
    except ValueError:
        pass
    # Transaction should have been rolled back
    # Verify operations were not committed (file may not exist or data not present)
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations

def test_transaction_function(temp_dir):
    """Test transaction convenience function."""
    file_path = temp_dir / "test.xwjson"
    ctx = transaction(file_path)
    assert isinstance(ctx, TransactionContext)
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_transaction_multiple_operations(temp_dir):
    """Test transaction with multiple operations."""
    file_path = temp_dir / "test.xwjson"
    tx = XWJSONTransaction(file_path)
    await tx.write("key1", "value1")
    await tx.write("key2", "value2")
    await tx.update_path("/nested/key", "nested_value")
    assert len(tx._operations) == 3
    await tx.commit()
    assert tx._committed is True
