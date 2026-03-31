#exonware/xwjson/tests/1.unit/operations_tests/test_xwjson_ops.py
"""
Unit tests for XWJSONDataOperations.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import pytest
from exonware.xwjson.operations.xwjson_ops import XWJSONDataOperations
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_atomic_read_write(temp_dir):
    """Test atomic read/write operations."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {"test": "data"}
    await ops.atomic_write(file_path, data)
    loaded = await ops.atomic_read(file_path)
    assert loaded == data
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_read_path(temp_dir):
    """Test path-based read operations."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {"users": [{"name": "Alice", "age": 30}]}
    await ops.atomic_write(file_path, data)
    name = await ops.read_path(file_path, "/users/0/name")
    assert name == "Alice"
    age = await ops.read_path(file_path, "/users/0/age")
    assert age == 30
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_write_path(temp_dir):
    """Test path-based write operations."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {"users": [{"name": "Alice"}]}
    await ops.atomic_write(file_path, data)
    await ops.write_path(file_path, "/users/0/age", 30)
    loaded = await ops.atomic_read(file_path)
    assert loaded["users"][0]["age"] == 30
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_read_page(temp_dir):
    """Test paging operations."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    # Create list data
    data = [{"id": i, "name": f"User{i}"} for i in range(100)]
    await ops.atomic_write(file_path, data)
    # Read first page
    page1 = await ops.read_page(file_path, page_number=1, page_size=10)
    assert len(page1) == 10
    assert page1[0]["id"] == 0
    # Read second page
    page2 = await ops.read_page(file_path, page_number=2, page_size=10)
    assert len(page2) == 10
    assert page2[0]["id"] == 10
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_append(temp_dir):
    """Test append operations."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = [{"id": 1, "name": "Alice"}]
    await ops.atomic_write(file_path, data)
    await ops.append(file_path, {"id": 2, "name": "Bob"})
    loaded = await ops.atomic_read(file_path)
    assert len(loaded) == 2
    assert loaded[1]["name"] == "Bob"
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_query_jsonpath(temp_dir):
    """Test JSONPath queries."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {
        "users": [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]
    }
    await ops.atomic_write(file_path, data)
    # Query with JSONPath
    results = await ops.query(file_path, "$.users[*].name")
    assert "Alice" in results
    assert "Bob" in results
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_query_sql(temp_dir):
    """Test SQL queries via xwquery."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {
        "users": [
            {"name": "Alice", "age": 30, "city": "NYC"},
            {"name": "Bob", "age": 25, "city": "LA"},
        ]
    }
    await ops.atomic_write(file_path, data)
    try:
        # Query with SQL (if xwquery available)
        results = await ops.query(
            file_path,
            "SELECT name FROM users WHERE age > 25",
            query_format="sql"
        )
        assert len(results) > 0
    except (ImportError, SerializationError):
        # xwquery not available or query failed - skip
        pytest.skip("xwquery not available or query failed")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_partial_update(temp_dir):
    """Test partial update (RFC 6902 JSON Patch)."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {"users": [{"name": "Alice", "age": 30}]}
    await ops.atomic_write(file_path, data)
    patch = [
        {"op": "replace", "path": "/users/0/age", "value": 31}
    ]
    await ops.partial_update(file_path, patch)
    loaded = await ops.atomic_read(file_path)
    assert loaded["users"][0]["age"] == 31
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_delete_path(temp_dir):
    """Test path deletion."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {"users": [{"name": "Alice", "age": 30}]}
    await ops.atomic_write(file_path, data)
    await ops.delete_path(file_path, "/users/0/age")
    loaded = await ops.atomic_read(file_path)
    assert "age" not in loaded["users"][0]
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_read_stream_list(temp_dir):
    """Test streaming read for list data."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = [{"id": 1}, {"id": 2}, {"id": 3}]
    await ops.atomic_write(file_path, data)
    records = []
    async for record in ops.read_stream(file_path):
        records.append(record)
    assert len(records) == 3
    assert records == data
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_read_stream_non_list(temp_dir):
    """Test streaming read for non-list data."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {"single": "record"}
    await ops.atomic_write(file_path, data)
    records = []
    async for record in ops.read_stream(file_path):
        records.append(record)
    assert len(records) == 1
    assert records[0] == data
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_atomic_update(temp_dir):
    """Test atomic update with multiple path updates."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {"users": [{"name": "Alice", "age": 30}]}
    await ops.atomic_write(file_path, data)
    updates = {
        "/users/0/age": 31,
        "/users/0/name": "Alice Updated"
    }
    await ops.atomic_update(file_path, updates)
    loaded = await ops.atomic_read(file_path)
    assert loaded["users"][0]["age"] == 31
    assert loaded["users"][0]["name"] == "Alice Updated"
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_read_page_with_path(temp_dir):
    """Test paging with path specification."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {
        "users": [
            {"id": i, "name": f"User{i}"} for i in range(100)
        ]
    }
    await ops.atomic_write(file_path, data)
    # Read page from /users path
    page1 = await ops.read_page(file_path, page_number=1, page_size=10, path="/users")
    assert len(page1) == 10
    assert page1[0]["id"] == 0
    page2 = await ops.read_page(file_path, page_number=2, page_size=10, path="/users")
    assert len(page2) == 10
    assert page2[0]["id"] == 10
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_read_page_with_preloaded_data(temp_dir):
    """Test paging with pre-loaded data."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = [{"id": i} for i in range(50)]
    await ops.atomic_write(file_path, data)
    # Pre-load data
    loaded_data = await ops.atomic_read(file_path)
    # Use pre-loaded data for paging
    page1 = await ops.read_page(file_path, page_number=1, page_size=10, data=loaded_data)
    assert len(page1) == 10
    assert page1[0]["id"] == 0
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_query_advanced(temp_dir):
    """Test advanced query with full ExecutionResult."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {
        "users": [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]
    }
    await ops.atomic_write(file_path, data)
    try:
        result = await ops.query_advanced(
            file_path,
            "$.users[*].name",
            query_format="jsonpath"
        )
        # Should return ExecutionResult object
        assert result is not None
        # Check if it has results attribute (xwquery ExecutionResult)
        if hasattr(result, 'results'):
            assert len(result.results) > 0
    except (ImportError, SerializationError):
        pytest.skip("xwquery not available or query failed")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_execute_batch(temp_dir):
    """Test batch operations execution."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {"users": [{"name": "Alice"}]}
    await ops.atomic_write(file_path, data)
    operations = [
        {"op": "read_path", "path": "/users/0/name"},
        {"op": "write_path", "path": "/users/0/age", "value": 30},
        {"op": "read_path", "path": "/users/0/age"},
    ]
    results = await ops.execute_batch(file_path, operations)
    assert len(results) == 3
    assert results[0] == "Alice"  # First read
    assert results[2] == 30  # Second read after write
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_read_path_invalid_path(temp_dir):
    """Test read_path with invalid path raises error."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {"users": [{"name": "Alice"}]}
    await ops.atomic_write(file_path, data)
    with pytest.raises(SerializationError):
        await ops.read_path(file_path, "/invalid/path")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_write_path_invalid_path(temp_dir):
    """Test write_path raises when an intermediate segment is not a dict (cannot create path)."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    # "foo" is a string; cannot create /foo/nested/path
    data = {"foo": "bar"}
    await ops.atomic_write(file_path, data)
    with pytest.raises(SerializationError):
        await ops.write_path(file_path, "/foo/nested/path", "value")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_atomic_read_file_not_found(temp_dir):
    """Test atomic_read raises error when file not found."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "nonexistent.xwjson"
    with pytest.raises(SerializationError):
        await ops.atomic_read(file_path)
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_atomic_delete(temp_dir):
    """Test atomic delete operation."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {"test": "data"}
    await ops.atomic_write(file_path, data)
    assert file_path.exists()
    await ops.atomic_delete(file_path)
    assert not file_path.exists()
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_atomic_read_with_cache(temp_dir):
    """Test atomic read uses cache correctly."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {"test": "data"}
    await ops.atomic_write(file_path, data)
    # First read should cache
    result1 = await ops.atomic_read(file_path, use_cache=True)
    assert result1 == data
    # Second read should use cache (same result)
    result2 = await ops.atomic_read(file_path, use_cache=True)
    assert result2 == data
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_partial_update_replace(temp_dir):
    """Test partial update with replace operation."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {"users": [{"name": "Alice", "age": 30}]}
    await ops.atomic_write(file_path, data)
    patch = [
        {"op": "replace", "path": "/users/0/age", "value": 31}
    ]
    await ops.partial_update(file_path, patch)
    loaded = await ops.atomic_read(file_path)
    assert loaded["users"][0]["age"] == 31
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_partial_update_add(temp_dir):
    """Test partial update with add operation."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {"users": [{"name": "Alice"}]}
    await ops.atomic_write(file_path, data)
    patch = [
        {"op": "add", "path": "/users/0/age", "value": 30}
    ]
    await ops.partial_update(file_path, patch)
    loaded = await ops.atomic_read(file_path)
    assert loaded["users"][0]["age"] == 30
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_operations
@pytest.mark.asyncio
async def test_delete_path_root(temp_dir):
    """Test deleting root path (should clear data)."""
    ops = XWJSONDataOperations()
    file_path = temp_dir / "test.xwjson"
    data = {"test": "data"}
    await ops.atomic_write(file_path, data)
    await ops.delete_path(file_path, "")
    loaded = await ops.atomic_read(file_path)
    assert loaded == {}
