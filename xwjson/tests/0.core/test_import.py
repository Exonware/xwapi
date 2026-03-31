#exonware/xwjson/tests/0.core/test_import.py
"""
Core import tests for xwjson.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Fast, high-value core tests covering critical paths (80/20 rule).
"""

import pytest
@pytest.mark.xwjson_core


def test_import_xwjson():
    """Test that xwjson can be imported."""
    import exonware.xwjson
    assert hasattr(exonware.xwjson, '__version__')
    assert hasattr(exonware.xwjson, 'XWJSONSerializer')
@pytest.mark.xwjson_core


def test_import_serializer():
    """Test that XWJSONSerializer can be imported."""
    from exonware.xwjson import XWJSONSerializer
    assert XWJSONSerializer is not None
@pytest.mark.xwjson_core


def test_serializer_instantiation():
    """Test that XWJSONSerializer can be instantiated."""
    from exonware.xwjson import XWJSONSerializer
    serializer = XWJSONSerializer()
    assert serializer is not None
    assert serializer.codec_id == "xwjson"
@pytest.mark.xwjson_core


def test_serializer_metadata():
    """Test that XWJSONSerializer has correct metadata."""
    from exonware.xwjson import XWJSONSerializer
    serializer = XWJSONSerializer()
    assert serializer.codec_id == "xwjson"
    assert "application/x-xwjson" in serializer.media_types
    assert ".xwjson" in serializer.file_extensions
    assert serializer.is_binary_format is True
    assert serializer.supports_streaming is True
    assert serializer.supports_lazy_loading is True
@pytest.mark.xwjson_core


def test_auto_registration():
    """Test that XWJSONSerializer is auto-registered with UniversalCodecRegistry."""
    from exonware.xwsystem.io.codec.registry import get_registry
    from exonware.xwjson import XWJSONSerializer
    registry = get_registry()
    codec = registry.get_by_id("xwjson")
    assert codec is not None
    assert isinstance(codec, XWJSONSerializer)
