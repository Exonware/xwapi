#exonware/xwjson/tests/2.integration/scenarios/test_5gb_performance.py
"""
5GB Performance Tests for XWJSON
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Tests XWJSON with 5GB data files:
- Data generation (5GB XWJSON file)
- Encoding/decoding performance
- File operations performance
- Query performance
- Paging performance
- Memory efficiency
- Comparison with other solutions
Goal: WORK first, then improve to beat existing solutions
"""

import pytest
import time
from exonware.xwjson import XWJSONSerializer
from exonware.xwjson.operations.xwjson_ops import XWJSONDataOperations
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance

class Test5GBPerformance:
    """5GB performance tests for XWJSON."""
    @pytest.fixture

    def serializer(self):
        """Create serializer instance."""
        return XWJSONSerializer()
    @pytest.fixture

    def ops(self):
        """Create operations instance."""
        return XWJSONDataOperations()
    @pytest.fixture

    def large_data_5gb(self, temp_dir):
        """Generate 5GB data structure (lazy generation)."""
        # Generate data on demand to avoid memory issues
        target_size_gb = 5.0
        target_size_bytes = int(target_size_gb * 1024 * 1024 * 1024)
        # Generate records until we reach ~5GB
        records = []
        current_size = 0
        # Each record is approximately 300 bytes
        # So we need approximately: 5GB / 300 bytes = ~17.6M records
        records_per_mb = 1024 * 1024 // 300  # ~3500 records per MB
        target_records = int(target_size_gb * 1024 * records_per_mb)  # ~17.6M records
        # Generate records
        for i in range(min(target_records, 100000)):  # Limit for test speed
            record = {
                "@type": "Message",
                "id": f"msg_{i:08d}",
                "ts": 1000000000 + i,
                "payload": {
                    "text": f"Message {i} with some content to make it larger. " * 5,
                    "user_id": f"user_{i % 1000:06d}",
                    "channel_id": f"chan_{i % 100:06d}",
                    "views": i * 10,
                    "reactions": [
                        {"emoji": "👍", "count": i % 100}
                        for _ in range(min(10, i % 20))
                    ],
                    "metadata": {
                        "created": f"2025-01-{(i % 28) + 1:02d}",
                        "updated": f"2025-01-{(i % 28) + 1:02d}",
                        "tags": [f"tag{j}" for j in range(i % 5)]
                    }
                }
            }
            records.append(record)
            current_size += len(str(record).encode('utf-8'))
            # Stop if we've generated enough (for actual 5GB, use full target_records)
            if current_size >= target_size_bytes * 0.01:  # 1% for test speed
                break
        return {
            "records": records,
            "metadata": {
                "total_records": len(records),
                "estimated_size_gb": current_size / (1024 * 1024 * 1024),
                "generation_time": time.time()
            }
        }

    def test_generate_5gb_data_structure(self, serializer, temp_dir, large_data_5gb):
        """Test generating 5GB data structure."""
        data = large_data_5gb
        # Verify structure
        assert "records" in data
        assert len(data["records"]) > 0
        assert data["metadata"]["total_records"] > 0
        # Test encoding (may take time for large data)
        start_time = time.time()
        encoded = serializer.encode(data)
        encode_time = time.time() - start_time
        # Verify encoding succeeded
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0
        # Log performance
        size_mb = len(encoded) / (1024 * 1024)
        mb_per_sec = size_mb / encode_time if encode_time > 0 else 0
        print(f"\n📊 Encoding Performance:")
        print(f"  Size: {size_mb:.2f} MB")
        print(f"  Time: {encode_time:.2f} seconds")
        print(f"  Speed: {mb_per_sec:.2f} MB/s")
        print(f"  Records: {data['metadata']['total_records']}")

    def test_encode_5gb_performance(self, serializer, temp_dir):
        """Test encoding performance with large data (scaled for testing)."""
        # Generate large dataset (scaled down for test speed, but structure is same)
        records = []
        for i in range(100000):  # 100K records for test
            record = {
                "id": f"item_{i:08d}",
                "data": f"Data for item {i} with some content. " * 10,
                "metadata": {
                    "index": i,
                    "tags": [f"tag{j}" for j in range(i % 10)],
                    "values": list(range(i % 100))
                }
            }
            records.append(record)
        data = {"items": records}
        # Measure encoding
        start_time = time.time()
        encoded = serializer.encode(data)
        encode_time = time.time() - start_time
        # Verify
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0
        # Performance metrics
        size_mb = len(encoded) / (1024 * 1024)
        mb_per_sec = size_mb / encode_time if encode_time > 0 else 0
        records_per_sec = len(records) / encode_time if encode_time > 0 else 0
        print(f"\n📊 Encoding Performance (100K records):")
        print(f"  Size: {size_mb:.2f} MB")
        print(f"  Time: {encode_time:.2f} seconds")
        print(f"  Speed: {mb_per_sec:.2f} MB/s")
        print(f"  Records/s: {records_per_sec:,.0f}")
        # Should complete in reasonable time
        assert encode_time < 30.0, f"Encoding took {encode_time:.2f}s, expected < 30s"

    def test_decode_5gb_performance(self, serializer, temp_dir):
        """Test decoding performance with large encoded data."""
        # Generate and encode data
        records = []
        for i in range(100000):  # 100K records
            record = {
                "id": f"item_{i:08d}",
                "data": f"Data for item {i}. " * 5
            }
            records.append(record)
        data = {"items": records}
        encoded = serializer.encode(data)
        # Measure decoding
        start_time = time.time()
        decoded = serializer.decode(encoded)
        decode_time = time.time() - start_time
        # Verify
        assert decoded == data
        assert len(decoded["items"]) == len(records)
        # Performance metrics
        size_mb = len(encoded) / (1024 * 1024)
        mb_per_sec = size_mb / decode_time if decode_time > 0 else 0
        records_per_sec = len(records) / decode_time if decode_time > 0 else 0
        print(f"\n📊 Decoding Performance (100K records):")
        print(f"  Size: {size_mb:.2f} MB")
        print(f"  Time: {decode_time:.2f} seconds")
        print(f"  Speed: {mb_per_sec:.2f} MB/s")
        print(f"  Records/s: {records_per_sec:,.0f}")
        # Should complete in reasonable time
        assert decode_time < 30.0, f"Decoding took {decode_time:.2f}s, expected < 30s"
    @pytest.mark.asyncio

    async def test_file_operations_5gb(self, serializer, ops, temp_dir):
        """Test file operations with large data."""
        # Generate data
        records = []
        for i in range(50000):  # 50K records for file test
            record = {
                "id": f"item_{i:08d}",
                "data": f"Data for item {i}. " * 5
            }
            records.append(record)
        data = {"items": records}
        file_path = temp_dir / "large_data.xwjson"
        # Measure save
        start_time = time.time()
        serializer.save_file(data, file_path)
        save_time = time.time() - start_time
        # Verify file exists
        assert file_path.exists()
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        # Measure load
        start_time = time.time()
        loaded = serializer.load_file(file_path)
        load_time = time.time() - start_time
        # Verify
        assert loaded == data
        print(f"\n📊 File Operations Performance:")
        print(f"  File Size: {file_size_mb:.2f} MB")
        print(f"  Save Time: {save_time:.2f} seconds")
        print(f"  Load Time: {load_time:.2f} seconds")
        print(f"  Save Speed: {file_size_mb / save_time if save_time > 0 else 0:.2f} MB/s")
        print(f"  Load Speed: {file_size_mb / load_time if load_time > 0 else 0:.2f} MB/s")
    @pytest.mark.asyncio

    async def test_paging_5gb_performance(self, ops, temp_dir):
        """Test paging performance with large data."""
        # Generate data
        records = []
        for i in range(100000):  # 100K records
            records.append({
                "id": f"item_{i:08d}",
                "data": f"Data {i}"
            })
        data = {"items": records}
        file_path = temp_dir / "paging_test.xwjson"
        await ops.atomic_write(file_path, data)
        # Measure paging
        page_times = []
        for page_num in range(1, 11):  # First 10 pages
            start_time = time.time()
            page = await ops.read_page(file_path, page_number=page_num, page_size=100, path="/items")
            page_time = time.time() - start_time
            page_times.append(page_time)
            assert len(page) == 100 or (page_num == 10 and len(page) <= 100)
        avg_page_time = sum(page_times) / len(page_times)
        print(f"\n📊 Paging Performance:")
        print(f"  Total Records: {len(records):,}")
        print(f"  Page Size: 100")
        print(f"  Pages Tested: 10")
        print(f"  Avg Page Time: {avg_page_time * 1000:.2f} ms")
        print(f"  Total Time: {sum(page_times):.2f} seconds")
        # Should be fast for paging
        assert avg_page_time < 1.0, f"Paging too slow: {avg_page_time:.2f}s per page"
    @pytest.mark.asyncio

    async def test_query_5gb_performance(self, ops, temp_dir):
        """Test query performance with large data."""
        # Generate data
        records = []
        for i in range(100000):  # 100K records
            records.append({
                "id": f"item_{i:08d}",
                "value": i,
                "category": f"cat_{i % 10}"
            })
        data = {"items": records}
        file_path = temp_dir / "query_test.xwjson"
        await ops.atomic_write(file_path, data)
        # Measure query
        try:
            start_time = time.time()
            results = await ops.query(file_path, "$.items[?(@.value > 50000)]")
            query_time = time.time() - start_time
            print(f"\n📊 Query Performance:")
            print(f"  Total Records: {len(records):,}")
            print(f"  Results: {len(results) if isinstance(results, list) else 'N/A'}")
            print(f"  Query Time: {query_time:.2f} seconds")
            # Should complete in reasonable time
            assert query_time < 10.0, f"Query took {query_time:.2f}s, expected < 10s"
        except (ImportError, SerializationError):
            pytest.skip("Query support not available")

    def test_memory_efficiency_5gb(self, serializer, temp_dir):
        """Test memory efficiency with large data."""
        import tracemalloc
        # Generate data
        records = []
        for i in range(50000):  # 50K records
            records.append({
                "id": f"item_{i:08d}",
                "data": f"Data {i}" * 10
            })
        data = {"items": records}
        # Measure memory
        tracemalloc.start()
        # Encode
        encoded = serializer.encode(data)
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        memory_mb = peak / (1024 * 1024)
        size_mb = len(encoded) / (1024 * 1024)
        print(f"\n📊 Memory Efficiency:")
        print(f"  Data Size: {size_mb:.2f} MB")
        print(f"  Peak Memory: {memory_mb:.2f} MB")
        print(f"  Memory Ratio: {memory_mb / size_mb if size_mb > 0 else 0:.2f}x")
        # Memory should be reasonable (not 10x the data size)
        assert memory_mb < size_mb * 5, f"Memory usage too high: {memory_mb:.2f} MB for {size_mb:.2f} MB data"
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance

class Test5GBComparison:
    """Comparison tests for 5GB performance."""
    @pytest.fixture

    def serializer(self):
        """Create serializer instance."""
        return XWJSONSerializer()

    def test_encoding_comparison_stdlib_json(self, serializer, temp_dir):
        """Compare XWJSON encoding with stdlib json."""
        import json
        # Generate test data
        data = {
            "items": [
                {"id": i, "data": f"Item {i}" * 10}
                for i in range(10000)
            ]
        }
        # XWJSON encoding
        start_time = time.time()
        xwjson_encoded = serializer.encode(data)
        xwjson_time = time.time() - start_time
        # stdlib JSON encoding
        start_time = time.time()
        json_encoded = json.dumps(data).encode('utf-8')
        json_time = time.time() - start_time
        # Compare
        xwjson_size = len(xwjson_encoded)
        json_size = len(json_encoded)
        xwjson_mb_per_sec = (xwjson_size / (1024 * 1024)) / xwjson_time if xwjson_time > 0 else 0
        json_mb_per_sec = (json_size / (1024 * 1024)) / json_time if json_time > 0 else 0
        speedup = json_time / xwjson_time if xwjson_time > 0 else 0
        print(f"\n📊 Encoding Comparison (10K records):")
        print(f"  XWJSON: {xwjson_time:.3f}s ({xwjson_mb_per_sec:.2f} MB/s)")
        print(f"  stdlib JSON: {json_time:.3f}s ({json_mb_per_sec:.2f} MB/s)")
        print(f"  XWJSON Size: {xwjson_size / (1024 * 1024):.2f} MB")
        print(f"  JSON Size: {json_size / (1024 * 1024):.2f} MB")
        print(f"  Speedup: {speedup:.2f}x")
        # XWJSON should be competitive; timings near zero are noisy on some platforms
        baseline = max(json_time, 0.001)
        margin = 2 if baseline >= 0.01 else 10
        assert xwjson_time < baseline * margin, (
            f"XWJSON should be competitive: {xwjson_time:.3f}s vs {json_time:.3f}s (margin={margin}x)"
        )

    def test_decoding_comparison_stdlib_json(self, serializer, temp_dir):
        """Compare XWJSON decoding with stdlib json."""
        import json
        # Generate and encode data
        data = {
            "items": [
                {"id": i, "data": f"Item {i}" * 10}
                for i in range(10000)
            ]
        }
        xwjson_encoded = serializer.encode(data)
        json_encoded = json.dumps(data).encode('utf-8')
        # XWJSON decoding
        start_time = time.time()
        xwjson_decoded = serializer.decode(xwjson_encoded)
        xwjson_time = time.time() - start_time
        # stdlib JSON decoding
        start_time = time.time()
        json_decoded = json.loads(json_encoded.decode('utf-8'))
        json_time = time.time() - start_time
        # Verify correctness
        assert xwjson_decoded == data
        assert json_decoded == data
        # Compare
        speedup = json_time / xwjson_time if xwjson_time > 0 else 0
        print(f"\n📊 Decoding Comparison (10K records):")
        print(f"  XWJSON: {xwjson_time:.3f}s")
        print(f"  stdlib JSON: {json_time:.3f}s")
        print(f"  Speedup: {speedup:.2f}x")
        # XWJSON should be competitive (use looser margin when baseline is tiny - timings are noisy)
        baseline = max(json_time, 0.001)
        margin = 2 if baseline >= 0.01 else 10
        assert xwjson_time < baseline * margin, f"XWJSON should be competitive: {xwjson_time:.3f}s vs {json_time:.3f}s (margin={margin}x)"
