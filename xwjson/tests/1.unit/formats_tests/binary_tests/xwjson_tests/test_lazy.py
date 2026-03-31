#exonware/xwjson/tests/1.unit/formats_tests/binary_tests/xwjson_tests/test_lazy.py
"""
Unit tests for lazy loading support.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import pytest
from exonware.xwjson.formats.binary.xwjson.lazy import (
    LazyFileProxy, LazySerializationProxy, LazyReferenceProxy
)
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_lazy


def test_lazy_file_proxy(temp_dir):
    """Test lazy file proxy."""
    file_path = temp_dir / "lazy_test.xwjson"
    file_path.write_bytes(b'{"test": "data"}')
    proxy = LazyFileProxy(file_path, lazy_threshold=1024)
    assert not proxy._loaded
    # Access triggers load (use __len__ or __getitem__ to trigger)
    _ = len(proxy)
    assert proxy._loaded
    proxy.close()
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_lazy


def test_lazy_serialization_proxy():
    """Test lazy serialization proxy."""
    import json
    raw_data = json.dumps({"test": "data"}).encode('utf-8')
    parser = lambda b: json.loads(b.decode('utf-8'))
    proxy = LazySerializationProxy(raw_data, parser)
    assert not proxy._parsed
    # Access triggers parse (use __getitem__ or __len__ to trigger)
    result = proxy["test"]
    assert proxy._parsed
    assert result == "data"
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_lazy


def test_lazy_reference_proxy():
    """Test lazy reference proxy."""
    resolver = lambda ref: {"resolved": ref}
    cache = {}
    proxy = LazyReferenceProxy("ref1", resolver, cache)
    assert not proxy._resolved
    # Access triggers resolve (use __getitem__ or __len__ to trigger)
    _ = proxy["resolved"]
    assert proxy._resolved
    assert "ref1" in cache
