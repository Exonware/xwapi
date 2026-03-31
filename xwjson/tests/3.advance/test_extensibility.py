#exonware/xwjson/tests/3.advance/test_extensibility.py
"""
Extensibility excellence tests (Priority #5).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Extensibility tests: plugin system, hooks, customization points.
"""

import pytest
from exonware.xwjson import XWJSONSerializer
from exonware.xwjson.formats.binary.xwjson.metadata import FormatMetadata, FormatMetadataExtractor
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_extensibility


def test_metadata_extensibility():
    """Test metadata system is extensible."""
    metadata = FormatMetadata(source_format="json")
    # Should support custom metadata
    metadata.custom["custom_field"] = "custom_value"
    assert metadata.custom["custom_field"] == "custom_value"
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_extensibility


def test_format_extensibility():
    """Test format system is extensible."""
    extractor = FormatMetadataExtractor()
    # Should support custom formats
    metadata = extractor.extract({"test": "data"}, source_format="custom_format")
    assert metadata.source_format == "custom_format"
@pytest.mark.xwjson_advance
@pytest.mark.xwjson_extensibility


def test_serializer_subclassing():
    """Test serializer can be subclassed."""
    class CustomXWJSONSerializer(XWJSONSerializer):
        """Custom serializer extension."""
        @property
        def codec_id(self) -> str:
            return "custom_xwjson"
    custom_serializer = CustomXWJSONSerializer()
    assert custom_serializer.codec_id == "custom_xwjson"
    # Should still work
    data = {"test": "data"}
    encoded = custom_serializer.encode(data)
    decoded = custom_serializer.decode(encoded)
    assert decoded == data
