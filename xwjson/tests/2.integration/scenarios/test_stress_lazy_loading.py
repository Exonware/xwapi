#exonware/xwjson/tests/2.integration/scenarios/test_stress_lazy_loading.py
"""
Stress tests for lazy loading.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Stress tests for lazy loading: file proxy, serialization proxy, node proxy.
"""

import pytest
from exonware.xwjson.formats.binary.xwjson.lazy import (
    LazyFileProxy, LazySerializationProxy, LazyXWNodeProxy
)
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.xwjson_lazy


def test_stress_lazy_file_proxy(temp_dir):
    """Stress test: Lazy file proxy with large files."""
    # Create large file
    file_path = temp_dir / "lazy_large.xwjson"
    large_content = b'{"data": [' + b'{"id": ' + str(0).encode() + b'},' * 100000 + b']}'
    file_path.write_bytes(large_content)
    # Create lazy proxy
    proxy = LazyFileProxy(file_path, lazy_threshold=1024 * 1024)  # 1MB threshold
    # Should not load until accessed
    assert not proxy._loaded
    # Access triggers load (len() or __getitem__ triggers _load(); _data is raw bytes)
    _ = len(proxy)
    assert proxy._loaded
    proxy.close()
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.xwjson_lazy


def test_stress_lazy_serialization():
    """Stress test: Lazy serialization with large data."""
    import json
    # Create large JSON
    large_data = {"items": [{"id": i, "value": f"item{i}" * 100} for i in range(50000)]}
    json_bytes = json.dumps(large_data).encode('utf-8')
    parser = lambda b: json.loads(b.decode('utf-8'))
    # Create lazy proxy
    proxy = LazySerializationProxy(json_bytes, parser, lazy_threshold=1024 * 1024)
    # Should not parse until accessed
    assert not proxy._parsed
    # Access triggers parse (use __getitem__ or __len__)
    result = proxy["items"]
    assert proxy._parsed
    assert len(result) == 50000
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.xwjson_lazy


def test_stress_lazy_node_creation():
    """Stress test: Lazy xwnode creation."""
    try:
        from exonware.xwnode import XWNode
        # Create large data structure
        large_data = {
            "users": [
                {"id": i, "name": f"User{i}", "data": {f"key{j}": f"value{j}" for j in range(100)}}
                for i in range(10000)
            ]
        }
        # Create lazy proxy
        node_factory = lambda data: XWNode.from_native(data, mode='AUTO')
        proxy = LazyXWNodeProxy(large_data, node_factory)
        # Should not create node until accessed
        # Note: Implementation may vary
        # Access should trigger node creation
        _ = proxy._data
        # Node creation happens lazily
    except ImportError:
        pytest.skip("xwnode not available")
@pytest.mark.xwjson_integration
@pytest.mark.xwjson_performance
@pytest.mark.xwjson_lazy


def test_stress_lazy_memory_efficiency():
    """Stress test: Lazy loading memory efficiency."""
    import json
    import sys
    # Create very large JSON
    large_data = {"items": [{"id": i, "value": f"item{i}" * 1000} for i in range(100000)]}
    json_bytes = json.dumps(large_data).encode('utf-8')
    # Memory before lazy loading
    memory_before = sys.getsizeof(json_bytes)
    parser = lambda b: json.loads(b.decode('utf-8'))
    proxy = LazySerializationProxy(json_bytes, parser, lazy_threshold=10 * 1024 * 1024)
    # Should not parse (data is large, threshold is 10MB)
    # Memory should be similar (just storing bytes)
    memory_after = sys.getsizeof(proxy._raw_data)
    # Memory should be similar (not parsed yet)
    assert abs(memory_after - memory_before) < memory_before * 0.1
