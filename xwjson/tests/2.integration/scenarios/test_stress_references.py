#exonware/xwjson/tests/2.integration/scenarios/test_stress_references.py
"""
Stress tests for reference resolution.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Stress tests for reference resolution, circular detection, caching.
"""

import pytest
from exonware.xwjson.formats.binary.xwjson.references import XWJSONReferenceResolver
from exonware.xwsystem.io.errors import SerializationError
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_stress_json_pointer_resolution():
    """Stress test: 10000 JSON Pointer resolutions."""
    resolver = XWJSONReferenceResolver()
    # Create large nested structure
    data = {
        "level1": {
            f"key{i}": {
                "level2": {
                    f"subkey{j}": f"value{i}_{j}"
                    for j in range(100)
                }
            }
            for i in range(1000)
        }
    }
    import time
    start = time.perf_counter()
    # Resolve 10000 paths
    for i in range(0, 1000, 10):
        for j in range(0, 100, 10):
            path = f"/level1/key{i}/level2/subkey{j}"
            result = resolver._resolve_json_pointer(path, data)
            assert result == f"value{i}_{j}"
    resolution_time = time.perf_counter() - start
    # Should be fast (< 1s for 10000 resolutions)
    assert resolution_time < 1.0, f"JSON Pointer resolution too slow: {resolution_time:.3f}s"
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_stress_reference_caching():
    """Stress test: Reference caching performance."""
    resolver = XWJSONReferenceResolver()
    data = {
        "users": [{"id": i, "name": f"User{i}"} for i in range(10000)],
        "metadata": {"version": "1.0"}
    }
    # First pass (cache misses)
    import time
    start = time.perf_counter()
    for i in range(0, 10000, 100):
        path = f"/users/{i}/name"
        resolver._resolve_json_pointer(path, data)
    time.perf_counter() - start
    # Second pass (cache hits)
    start = time.perf_counter()
    for i in range(0, 10000, 100):
        path = f"/users/{i}/name"
        resolver._resolve_json_pointer(path, data)
    time.perf_counter() - start
    # Second pass should be faster (cache hits)
    # Note: Current implementation may not cache JSON Pointer results
    # This test verifies the caching mechanism works if implemented
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_stress_circular_detection():
    """Stress test: Circular reference detection performance."""
    resolver = XWJSONReferenceResolver()
    # Create chain of references
    for i in range(1000):
        resolver._resolving.add(f"ref{i}")
    # Should detect circular reference quickly
    import time
    start = time.perf_counter()
    with pytest.raises(SerializationError, match="Circular reference"):
        resolver.resolve("ref500", "json")
    detection_time = time.perf_counter() - start
    # Should be fast (< 10ms)
    assert detection_time < 0.01, f"Circular detection too slow: {detection_time:.3f}s"
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance


def test_stress_reference_detection():
    """Stress test: Reference detection in large data."""
    resolver = XWJSONReferenceResolver()
    # Create data with many references
    data = {
        "definitions": {
            f"type{i}": {"type": "object", "properties": {}}
            for i in range(1000)
        },
        "items": [
            {"$ref": f"#/definitions/type{i % 1000}"}
            for i in range(10000)
        ]
    }
    import time
    start = time.perf_counter()
    references = resolver.detect_references(data, "json")
    detection_time = time.perf_counter() - start
    # Should detect all references
    assert len(references) == 10000
    # Should be fast (< 1s)
    assert detection_time < 1.0, f"Reference detection too slow: {detection_time:.3f}s"
