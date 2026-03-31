#exonware/xwjson/tests/1.unit/formats_tests/binary_tests/xwjson_tests/test_batch_operations.py
"""
Unit tests for SmartBatchExecutor.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import pytest
from exonware.xwjson.formats.binary.xwjson.batch_operations import SmartBatchExecutor
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations

def test_batch_executor_init():
    """Test batch executor initialization."""
    executor = SmartBatchExecutor()
    assert executor is not None
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_execute_batch_simple_operations(temp_dir):
    """Test executing simple batch operations."""
    executor = SmartBatchExecutor()
    file_path = temp_dir / "test.xwjson"
    operations = [
        {"op": "write", "key": "key1", "value": "value1"},
        {"op": "write", "key": "key2", "value": "value2"},
    ]
    results = await executor.execute_batch(str(file_path), operations)
    assert len(results) == 2
    assert all(r.get("status") == "success" for r in results)
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_execute_batch_with_dependencies(temp_dir):
    """Test batch operations with dependencies (should order correctly)."""
    executor = SmartBatchExecutor()
    file_path = temp_dir / "test.xwjson"
    operations = [
        {"op": "write", "key": "key1", "value": "value1"},
        {"op": "update_path", "path": "/key1", "value": "updated_value1"},
    ]
    results = await executor.execute_batch(str(file_path), operations)
    assert len(results) == 2
    # Operations should execute in dependency order
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_execute_batch_update_path(temp_dir):
    """Test batch operation with path updates."""
    executor = SmartBatchExecutor()
    file_path = temp_dir / "test.xwjson"
    operations = [
        {"op": "update_path", "path": "/users/0/name", "value": "Alice"},
    ]
    results = await executor.execute_batch(str(file_path), operations)
    assert len(results) == 1
    assert results[0].get("status") == "success"
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_execute_batch_delete_path(temp_dir):
    """Test batch operation with path deletion."""
    executor = SmartBatchExecutor()
    file_path = temp_dir / "test.xwjson"
    # First create data
    operations_create = [
        {"op": "write", "key": "test_key", "value": "test_value"},
    ]
    await executor.execute_batch(str(file_path), operations_create)
    # Then delete it
    operations_delete = [
        {"op": "delete_path", "path": "/test_key"},
    ]
    results = await executor.execute_batch(str(file_path), operations_delete)
    assert len(results) == 1
    assert results[0].get("status") == "success"
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_execute_batch_move_operation(temp_dir):
    """Test batch operation with move."""
    executor = SmartBatchExecutor()
    file_path = temp_dir / "test.xwjson"
    # First create source
    operations_create = [
        {"op": "write", "key": "source", "value": "source_value"},
    ]
    await executor.execute_batch(str(file_path), operations_create)
    # Then move
    operations_move = [
        {"op": "move", "from": "/source", "to": "/destination"},
    ]
    results = await executor.execute_batch(str(file_path), operations_move)
    assert len(results) == 1
    assert results[0].get("status") == "success"
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_execute_batch_invalid_operation(temp_dir):
    """Test batch execution with invalid operation."""
    executor = SmartBatchExecutor()
    file_path = temp_dir / "test.xwjson"
    operations = [
        {"op": "invalid_operation", "key": "key1"},
    ]
    with pytest.raises(SerializationError):
        await executor.execute_batch(str(file_path), operations)
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_execute_batch_empty_list(temp_dir):
    """Test batch execution with empty operations list."""
    executor = SmartBatchExecutor()
    file_path = temp_dir / "test.xwjson"
    results = await executor.execute_batch(str(file_path), [])
    assert len(results) == 0
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_execute_batch_with_custom_executor(temp_dir):
    """Test batch execution with custom executor."""
    executor = SmartBatchExecutor()
    file_path = temp_dir / "test.xwjson"
    # Custom executor that just returns success
    class CustomExecutor:
        async def execute(self, operation):
            return {"status": "custom_success", "op": operation.get("op")}
    custom_exec = CustomExecutor()
    operations = [
        {"op": "write", "key": "key1", "value": "value1"},
    ]
    results = await executor.execute_batch(str(file_path), operations, executor=custom_exec)
    assert len(results) == 1
    assert results[0].get("status") == "custom_success"
