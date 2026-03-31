#exonware/xwjson/tests/2.integration/scenarios/test_stress_conversion_performance.py
"""
Format Conversion Performance Stress Tests
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Stress tests for format conversion performance:
- Large data conversions
- Concurrent conversions
- Multiple format hops
- Performance benchmarks
"""

import pytest
import asyncio
import time
from exonware.xwjson.formats.binary.xwjson.converter import XWJSONConverter
from exonware.xwjson import XWJSONSerializer
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio

class TestConversionPerformance:
    """Performance stress tests for format conversions."""
    @pytest.fixture

    def converter(self):
        """Create converter instance."""
        return XWJSONConverter()
    @pytest.fixture

    def serializer(self):
        """Create serializer instance."""
        return XWJSONSerializer()
    @pytest.fixture

    def large_dataset(self):
        """Large dataset for performance testing."""
        return {
            "items": [
                {
                    "id": i,
                    "name": f"Item {i}",
                    "description": f"Description for item {i}",
                    "tags": [f"tag{j}" for j in range(50)],
                    "metadata": {
                        "created": f"2025-01-{(i % 28) + 1:02d}",
                        "score": i * 0.1,
                        "data": list(range(100))
                    }
                }
                for i in range(5000)
            ]
        }
    @pytest.mark.asyncio

    async def test_large_json_conversion_performance(self, serializer, large_dataset):
        """Test performance of large JSON encoding/decoding."""
        start_time = time.time()
        encoded = serializer.encode(large_dataset)
        decode_time = time.time()
        decoded = serializer.decode(encoded)
        end_time = time.time()
        decode_time - start_time
        total_time = end_time - start_time
        # Verify correctness
        assert decoded == large_dataset
        # Performance check (should complete in reasonable time)
        assert total_time < 5.0, f"Conversion took {total_time:.2f}s, expected < 5.0s"
    @pytest.mark.asyncio

    async def test_concurrent_conversions(self, converter):
        """Test concurrent format conversions."""
        data = {
            "test": "data",
            "items": list(range(1000))
        }
        # Run 10 conversions concurrently
        start_time = time.time()
        tasks = [
            converter.convert(data.copy(), "json", "json")
            for _ in range(10)
        ]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        # Verify all conversions succeeded
        assert len(results) == 10
        assert all(r == data for r in results)
        # Should complete in reasonable time
        assert (end_time - start_time) < 2.0
    @pytest.mark.asyncio

    async def test_multiple_format_hops_performance(self, converter):
        """Test performance of multiple format hops."""
        data = {
            "items": [
                {"id": i, "name": f"Item {i}"}
                for i in range(1000)
            ]
        }
        start_time = time.time()
        try:
            # JSON → YAML → TOML → JSON
            yaml_data = await converter.convert(data, "json", "yaml")
            toml_data = await converter.convert(yaml_data, "yaml", "toml")
            result = await converter.convert(toml_data, "toml", "json")
            end_time = time.time()
            # Verify correctness
            assert result == data
            # Should complete in reasonable time
            assert (end_time - start_time) < 3.0
        except (ImportError, SerializationError) as e:
            pytest.skip(f"Multi-format conversion not available: {e}")
    @pytest.mark.asyncio

    async def test_repeated_conversions_same_data(self, converter):
        """Test performance of repeated conversions on same data."""
        data = {
            "test": "data",
            "items": list(range(100))
        }
        start_time = time.time()
        # Convert 100 times
        for _ in range(100):
            result = await converter.convert(data, "json", "json")
            assert result == data
        end_time = time.time()
        # Should complete in reasonable time
        assert (end_time - start_time) < 5.0
    @pytest.mark.asyncio

    async def test_conversion_with_metadata_performance(self, serializer):
        """Test performance of conversions with metadata."""
        data = {
            "items": [
                {"id": i, "data": f"item_{i}"}
                for i in range(1000)
            ]
        }
        metadata = {
            "source_format": "json",
            "version": "1.0",
            "tags": ["test", "performance"]
        }
        start_time = time.time()
        # Encode with metadata
        encoded = serializer.encode(
            data,
            options={
                'metadata': metadata,
                'format_code': 0x00
            }
        )
        # Decode with metadata
        result = serializer.decode(encoded, options={'return_metadata': True})
        end_time = time.time()
        # Verify correctness
        assert result['data'] == data
        assert result.get('metadata') is not None
        # Should complete in reasonable time
        assert (end_time - start_time) < 1.0
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.asyncio

class TestConversionScalability:
    """Scalability tests for format conversions."""
    @pytest.fixture

    def converter(self):
        """Create converter instance."""
        return XWJSONConverter()
    @pytest.mark.asyncio

    async def test_scalability_increasing_data_size(self, converter):
        """Test conversion performance with increasing data sizes."""
        sizes = [100, 500, 1000, 5000]
        for size in sizes:
            data = {
                "items": [
                    {"id": i, "data": f"item_{i}"}
                    for i in range(size)
                ]
            }
            start_time = time.time()
            result = await converter.convert(data, "json", "json")
            end_time = time.time()
            elapsed = end_time - start_time
            # Verify correctness
            assert result == data
            # Performance should scale reasonably
            # Larger data takes more time, but should still be acceptable
            assert elapsed < (size / 1000) * 2.0, f"Size {size} took {elapsed:.2f}s"
    @pytest.mark.asyncio

    async def test_scalability_nesting_depth(self, converter):
        """Test conversion performance with increasing nesting depth."""
        for depth in [5, 10, 20, 50]:
            # Create nested structure
            data = {}
            current = data
            for i in range(depth):
                current[f"level_{i}"] = {}
                current = current[f"level_{i}"]
            current["value"] = "deep"
            start_time = time.time()
            result = await converter.convert(data, "json", "json")
            end_time = time.time()
            elapsed = end_time - start_time
            # Verify correctness
            assert result == data
            # Should complete in reasonable time even with deep nesting
            assert elapsed < 1.0, f"Depth {depth} took {elapsed:.2f}s"
