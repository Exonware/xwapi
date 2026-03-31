#exonware/xwjson/tests/2.integration/scenarios/test_edge_cases_comprehensive.py
"""
Comprehensive Edge Case Tests for All XWJSON Classes
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Tests edge cases and boundary conditions for all XWJSON classes:
- XWJSONSerializer: Extreme values, invalid inputs, boundary conditions
- XWJSONConverter: Format conversion edge cases
- XWJSONDataOperations: Path operations, paging, queries
- XWJSONTransaction: Concurrent transactions, rollback scenarios
- SmartBatchExecutor: Complex dependencies, conflicts
- FormatMetadata: Extraction/restoration edge cases
- XWJSONSchemaValidator: Schema validation edge cases
"""

import pytest
import math
from exonware.xwjson import XWJSONSerializer
from exonware.xwjson.operations.xwjson_ops import XWJSONDataOperations
from exonware.xwjson.formats.binary.xwjson.transactions import XWJSONTransaction, TransactionContext
from exonware.xwjson.formats.binary.xwjson.batch_operations import SmartBatchExecutor
from exonware.xwjson.formats.binary.xwjson.metadata import FormatMetadata, FormatMetadataExtractor, FormatMetadataRestorer
from exonware.xwjson.formats.binary.xwjson.schema import XWJSONSchemaValidator
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_serialization

class TestSerializerEdgeCases:
    """Edge case tests for XWJSONSerializer."""

    def test_encode_extreme_integer_values(self):
        """Test encoding extreme integer values."""
        serializer = XWJSONSerializer()
        data = {
            "max_int32": 2147483647,
            "min_int32": -2147483648,
            "max_int64": 9223372036854775807,
            "min_int64": -9223372036854775808,
            "zero": 0,
            "negative_zero": -0
        }
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        assert decoded == data

    def test_encode_extreme_float_values(self):
        """Test encoding extreme float values."""
        serializer = XWJSONSerializer()
        data = {
            "infinity": float('inf'),
            "negative_infinity": float('-inf'),
            "nan": float('nan'),
            "max_float": sys.float_info.max,
            "min_float": sys.float_info.min,
            "epsilon": sys.float_info.epsilon
        }
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        # NaN comparison needs special handling
        assert math.isnan(decoded["nan"]) == math.isnan(data["nan"])
        assert decoded["infinity"] == data["infinity"]
        assert decoded["negative_infinity"] == data["negative_infinity"]

    def test_encode_very_large_strings(self):
        """Test encoding very large strings."""
        serializer = XWJSONSerializer()
        # 1MB string
        large_string = "A" * (1024 * 1024)
        data = {"large_string": large_string}
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        assert decoded == data
        assert len(decoded["large_string"]) == 1024 * 1024

    def test_encode_deeply_nested_structures(self):
        """Test encoding deeply nested structures."""
        serializer = XWJSONSerializer()
        # Create 100 levels of nesting
        data = {}
        current = data
        for i in range(100):
            current[f"level_{i}"] = {}
            current = current[f"level_{i}"]
        current["value"] = "deep"
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        # Verify nested structure
        current = decoded
        for i in range(100):
            assert f"level_{i}" in current
            current = current[f"level_{i}"]
        assert current["value"] == "deep"

    def test_encode_very_large_arrays(self):
        """Test encoding very large arrays."""
        serializer = XWJSONSerializer()
        # 100,000 element array
        data = {"large_array": list(range(100000))}
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        assert decoded == data
        assert len(decoded["large_array"]) == 100000

    def test_encode_unicode_characters(self):
        """Test encoding unicode characters."""
        serializer = XWJSONSerializer()
        data = {
            "unicode": "Hello 世界 🌍 こんにちは مرحبا",
            "emoji": "😀😃😄😁😆😅😂🤣",
            "special": "ÀÁÂÃÄÅÆÇÈÉÊË",
            "chinese": "你好世界",
            "arabic": "مرحبا بالعالم",
            "japanese": "こんにちは世界"
        }
        encoded = serializer.encode(data)
        decoded = serializer.decode(encoded)
        assert decoded == data

    def test_encode_empty_structures(self):
        """Test encoding empty structures."""
        serializer = XWJSONSerializer()
        test_cases = [
            {},
            [],
            {"empty_dict": {}, "empty_list": []},
            {"nested": {"empty": {}}}
        ]
        for data in test_cases:
            encoded = serializer.encode(data)
            decoded = serializer.decode(encoded)
            assert decoded == data

    def test_decode_invalid_magic_bytes(self):
        """Test decoding with invalid magic bytes raises error."""
        serializer = XWJSONSerializer()
        invalid_data = b'INVALID_MAGIC_BYTES' + b'x' * 100
        with pytest.raises(SerializationError):
            serializer.decode(invalid_data)

    def test_decode_too_short_data(self):
        """Test decoding too short data raises error."""
        serializer = XWJSONSerializer()
        with pytest.raises(SerializationError):
            serializer.decode(b'XWJ')
        with pytest.raises(SerializationError):
            serializer.decode(b'XWJ1')

    def test_encode_with_invalid_options(self):
        """Test encoding with invalid options handles gracefully."""
        serializer = XWJSONSerializer()
        data = {"test": "data"}
        # Invalid options should not crash, should use defaults
        encoded = serializer.encode(data, options={"invalid_option": "value"})
        decoded = serializer.decode(encoded)
        assert decoded == data
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_operations
@pytest.mark.asyncio

class TestDataOperationsEdgeCases:
    """Edge case tests for XWJSONDataOperations."""
    @pytest.mark.asyncio

    async def test_read_path_root_level(self, temp_dir):
        """Test reading root level path."""
        ops = XWJSONDataOperations()
        file_path = temp_dir / "test.xwjson"
        data = {"root": "value"}
        await ops.atomic_write(file_path, data)
        result = await ops.read_path(file_path, "")
        assert result == data
    @pytest.mark.asyncio

    async def test_read_path_nonexistent_path(self, temp_dir):
        """Test reading nonexistent path raises error."""
        ops = XWJSONDataOperations()
        file_path = temp_dir / "test.xwjson"
        data = {"existing": "value"}
        await ops.atomic_write(file_path, data)
        with pytest.raises(SerializationError):
            await ops.read_path(file_path, "/nonexistent/path")
    @pytest.mark.asyncio

    async def test_write_path_create_nested_structure(self, temp_dir):
        """Test writing path creates nested structure."""
        ops = XWJSONDataOperations()
        file_path = temp_dir / "test.xwjson"
        data = {}
        await ops.atomic_write(file_path, data)
        await ops.write_path(file_path, "/level1/level2/level3/value", "nested")
        loaded = await ops.atomic_read(file_path)
        assert loaded["level1"]["level2"]["level3"]["value"] == "nested"
    @pytest.mark.asyncio

    async def test_read_page_empty_list(self, temp_dir):
        """Test reading page from empty list."""
        ops = XWJSONDataOperations()
        file_path = temp_dir / "test.xwjson"
        data = []
        await ops.atomic_read(file_path) if file_path.exists() else await ops.atomic_write(file_path, data)
        page = await ops.read_page(file_path, page_number=1, page_size=10)
        assert page == []
    @pytest.mark.asyncio

    async def test_read_page_beyond_available(self, temp_dir):
        """Test reading page beyond available data."""
        ops = XWJSONDataOperations()
        file_path = temp_dir / "test.xwjson"
        data = [1, 2, 3]
        await ops.atomic_write(file_path, data)
        page = await ops.read_page(file_path, page_number=10, page_size=10)
        assert page == []
    @pytest.mark.asyncio

    async def test_append_to_non_list(self, temp_dir):
        """Test append to non-list converts to list."""
        ops = XWJSONDataOperations()
        file_path = temp_dir / "test.xwjson"
        data = {"single": "value"}
        await ops.atomic_write(file_path, data)
        await ops.append(file_path, {"new": "item"})
        loaded = await ops.atomic_read(file_path)
        assert isinstance(loaded, list)
        assert len(loaded) == 2
    @pytest.mark.asyncio

    async def test_delete_path_array_index(self, temp_dir):
        """Test deleting array element by index."""
        ops = XWJSONDataOperations()
        file_path = temp_dir / "test.xwjson"
        data = {"items": ["a", "b", "c"]}
        await ops.atomic_write(file_path, data)
        await ops.delete_path(file_path, "/items/1")
        loaded = await ops.atomic_read(file_path)
        assert loaded["items"] == ["a", "c"]
    @pytest.mark.asyncio

    async def test_atomic_update_multiple_paths(self, temp_dir):
        """Test atomic update with multiple paths."""
        ops = XWJSONDataOperations()
        file_path = temp_dir / "test.xwjson"
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ]
        }
        await ops.atomic_write(file_path, data)
        updates = {
            "/users/0/age": 31,
            "/users/1/age": 26,
            "/users/0/name": "Alice Updated"
        }
        await ops.atomic_update(file_path, updates)
        loaded = await ops.atomic_read(file_path)
        assert loaded["users"][0]["age"] == 31
        assert loaded["users"][1]["age"] == 26
        assert loaded["users"][0]["name"] == "Alice Updated"
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_operations
@pytest.mark.asyncio

class TestTransactionEdgeCases:
    """Edge case tests for transactions."""
    @pytest.mark.asyncio

    async def test_concurrent_transactions_rollback(self, temp_dir):
        """Test concurrent transactions with rollback."""
        file_path = temp_dir / "test.xwjson"
        # Create initial data
        serializer = XWJSONSerializer()
        serializer.save_file({"initial": "data"}, file_path)
        # Start two transactions
        tx1 = XWJSONTransaction(file_path)
        tx2 = XWJSONTransaction(file_path)
        await tx1.write("key1", "value1")
        await tx2.write("key2", "value2")
        # Commit first, rollback second
        await tx1.commit()
        await tx2.rollback()
        # Verify only first transaction committed
        data = serializer.load_file(file_path)
        assert "key1" in data
        assert "key2" not in data
    @pytest.mark.asyncio

    async def test_transaction_context_exception_rollback(self, temp_dir):
        """Test transaction context rolls back on exception."""
        file_path = temp_dir / "test.xwjson"
        serializer = XWJSONSerializer()
        serializer.save_file({"initial": "data"}, file_path)
        try:
            async with TransactionContext(file_path) as tx:
                await tx.write("key1", "value1")
                raise ValueError("Test exception")
        except ValueError:
            pass
        # Verify changes were rolled back
        data = serializer.load_file(file_path)
        assert "key1" not in data
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_operations
@pytest.mark.asyncio

class TestBatchOperationsEdgeCases:
    """Edge case tests for batch operations."""
    @pytest.mark.asyncio

    async def test_batch_complex_dependencies(self, temp_dir):
        """Test batch with complex dependency chain."""
        executor = SmartBatchExecutor()
        file_path = temp_dir / "test.xwjson"
        operations = [
            {"op": "write", "key": "step1", "value": "value1"},
            {"op": "update_path", "path": "/step1", "value": "updated1", "depends_on": ["step1"]},
            {"op": "update_path", "path": "/step2", "value": "value2", "depends_on": ["step1"]},
            {"op": "update_path", "path": "/final", "value": "final_value", "depends_on": ["step2"]}
        ]
        results = await executor.execute_batch(str(file_path), operations)
        assert len(results) == 4
    @pytest.mark.asyncio

    async def test_batch_conflicting_operations(self, temp_dir):
        """Test batch with conflicting operations."""
        executor = SmartBatchExecutor()
        file_path = temp_dir / "test.xwjson"
        operations = [
            {"op": "write", "key": "conflict", "value": "value1"},
            {"op": "write", "key": "conflict", "value": "value2"}  # Conflict
        ]
        # Should handle conflicts (detection and resolution)
        results = await executor.execute_batch(str(file_path), operations)
        assert len(results) == 2
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_serialization

class TestMetadataEdgeCases:
    """Edge case tests for metadata extraction/restoration."""

    def test_extract_metadata_empty_data(self):
        """Test extracting metadata from empty data."""
        extractor = FormatMetadataExtractor()
        metadata = extractor.extract({}, "json")
        assert metadata.source_format == "json"

    def test_extract_metadata_complex_references(self):
        """Test extracting complex reference structures."""
        extractor = FormatMetadataExtractor()
        data = {
            "definitions": {
                "User": {"type": "object"},
                "Profile": {"type": "object"}
            },
            "user": {"$ref": "#/definitions/User"},
            "profile": {"$ref": "#/definitions/Profile"},
            "nested": {
                "ref": {"$ref": "#/definitions/User"}
            }
        }
        metadata = extractor.extract(data, "json")
        assert len(metadata.json_references) > 0

    def test_restore_metadata_complex_structure(self):
        """Test restoring metadata to complex structure."""
        restorer = FormatMetadataRestorer()
        data = {"complex": {"nested": {"structure": "value"}}}
        metadata = FormatMetadata(source_format="json")
        metadata.json_references["/complex/nested/structure"] = "#/definitions/Structure"
        result = restorer.restore(data, metadata, "json")
        assert isinstance(result, dict)
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_serialization

class TestSchemaValidatorEdgeCases:
    """Edge case tests for schema validation."""

    def test_validate_empty_schema(self):
        """Test validation with empty schema (should accept all)."""
        validator = XWJSONSchemaValidator()
        # Empty schema should accept all data
        assert validator.validate({"any": "data"}) is True
        assert validator.validate(123) is True
        assert validator.validate([1, 2, 3]) is True

    def test_validate_strict_schema(self):
        """Test validation with very strict schema."""
        strict_schema = {
            "type": "object",
            "required": ["required_field"],
            "properties": {
                "required_field": {"type": "string"},
                "optional_field": {"type": "integer"}
            },
            "additionalProperties": False
        }
        try:
            validator = XWJSONSchemaValidator(strict_schema)
            # Should reject data without required field
            assert validator.validate({}) is False
            # Should reject data with extra fields
            assert validator.validate({"required_field": "value", "extra": "field"}) is False
            # Should accept valid data
            assert validator.validate({"required_field": "value"}) is True
        except ImportError:
            pytest.skip("Schema validation libraries not available")

    def test_validate_nested_schemas(self):
        """Test validation with deeply nested schemas."""
        nested_schema = {
            "type": "object",
            "properties": {
                "level1": {
                    "type": "object",
                    "properties": {
                        "level2": {
                            "type": "object",
                            "properties": {
                                "level3": {
                                    "type": "object",
                                    "properties": {
                                        "value": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        try:
            validator = XWJSONSchemaValidator(nested_schema)
            valid_data = {
                "level1": {
                    "level2": {
                        "level3": {
                            "value": "deep"
                        }
                    }
                }
            }
            assert validator.validate(valid_data) is True
        except ImportError:
            pytest.skip("Schema validation libraries not available")
import sys
