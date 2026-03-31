#exonware/xwjson/tests/1.unit/formats_tests/binary_tests/xwjson_tests/test_metadata.py
"""
Unit tests for FormatMetadata, FormatMetadataExtractor, and FormatMetadataRestorer.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import pytest
from exonware.xwjson.formats.binary.xwjson.metadata import (
    FormatMetadata,
    FormatMetadataExtractor,
    FormatMetadataRestorer
)
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_format_metadata_init():
    """Test FormatMetadata initialization."""
    metadata = FormatMetadata()
    assert metadata.source_format == "json"
    assert metadata.source_version is None
    assert isinstance(metadata.yaml_anchors, dict)
    assert isinstance(metadata.json_references, dict)
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_format_metadata_custom_source():
    """Test FormatMetadata with custom source format."""
    metadata = FormatMetadata(source_format="yaml", source_version="1.2")
    assert metadata.source_format == "yaml"
    assert metadata.source_version == "1.2"
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_format_metadata_extractor_init():
    """Test FormatMetadataExtractor initialization."""
    extractor = FormatMetadataExtractor()
    assert extractor is not None
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_extract_json_metadata():
    """Test extracting metadata from JSON data."""
    extractor = FormatMetadataExtractor()
    data = {
        "user": {
            "$ref": "#/definitions/User"
        },
        "profile": {
            "$ref": "#/definitions/Profile"
        }
    }
    metadata = extractor.extract(data, "json")
    assert metadata.source_format == "json"
    assert len(metadata.json_references) > 0
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_extract_yaml_metadata():
    """Test extracting metadata from YAML data."""
    extractor = FormatMetadataExtractor()
    data = {"name": "test", "value": 123}
    metadata = extractor.extract(data, "yaml")
    assert metadata.source_format == "yaml"
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_extract_xml_metadata():
    """Test extracting metadata from XML data."""
    extractor = FormatMetadataExtractor()
    try:
        import xml.etree.ElementTree as ET
        root = ET.Element("root")
        root.set("xmlns:ns", "http://example.com")
        child = ET.SubElement(root, "child")
        child.set("attr", "value")
        metadata = extractor.extract(root, "xml", source_path=None)
        assert metadata.source_format == "xml"
    except ImportError:
        pytest.skip("XML support not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_extract_toml_metadata():
    """Test extracting metadata from TOML data."""
    extractor = FormatMetadataExtractor()
    data = {
        "name": "test",
        "nested": {
            "value": 123
        },
        "array": [1, 2, 3]
    }
    metadata = extractor.extract(data, "toml")
    assert metadata.source_format == "toml"
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_extract_json_references():
    """Test extracting JSON $ref references."""
    extractor = FormatMetadataExtractor()
    data = {
        "definitions": {
            "User": {"type": "object"}
        },
        "user": {
            "$ref": "#/definitions/User"
        }
    }
    metadata = FormatMetadata()
    extractor._extract_json_references(data, metadata, "")
    assert len(metadata.json_references) > 0
    assert any("#/definitions/User" in ref for ref in metadata.json_references.values())
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_format_metadata_restorer_init():
    """Test FormatMetadataRestorer initialization."""
    restorer = FormatMetadataRestorer()
    assert restorer is not None
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_restore_json_metadata():
    """Test restoring metadata to JSON data."""
    restorer = FormatMetadataRestorer()
    data = {"name": "test"}
    metadata = FormatMetadata(source_format="json")
    metadata.json_references["/user"] = "#/definitions/User"
    result = restorer.restore(data, metadata, "json")
    assert isinstance(result, dict)
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_restore_json_references():
    """Test restoring JSON $ref references."""
    restorer = FormatMetadataRestorer()
    data = {"user": {"name": "Alice"}}
    metadata = FormatMetadata()
    metadata.json_references["/user"] = "#/definitions/User"
    result = restorer._restore_json_references(data, metadata, "")
    # References should be restored to data structure
    assert isinstance(result, dict)
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_restore_yaml_metadata():
    """Test restoring metadata to YAML data."""
    restorer = FormatMetadataRestorer()
    data = {"name": "test"}
    metadata = FormatMetadata(source_format="yaml")
    result = restorer.restore(data, metadata, "yaml")
    assert isinstance(result, dict)
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_restore_xml_metadata():
    """Test restoring metadata to XML data."""
    restorer = FormatMetadataRestorer()
    try:
        data = {"tag": "root", "children": []}
        metadata = FormatMetadata(source_format="xml")
        metadata.xml_namespaces["ns"] = "http://example.com"
        result = restorer.restore(data, metadata, "xml")
        # Should return Element or dict
        assert result is not None
    except ImportError:
        pytest.skip("XML support not available")
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_restore_toml_metadata():
    """Test restoring metadata to TOML data."""
    restorer = FormatMetadataRestorer()
    data = {"name": "test"}
    metadata = FormatMetadata(source_format="toml")
    result = restorer.restore(data, metadata, "toml")
    assert isinstance(result, dict)
@pytest.mark.xwjson_unit
@pytest.mark.xwjson_serialization

def test_restore_unknown_format():
    """Test restoring metadata to unknown format returns data as-is."""
    restorer = FormatMetadataRestorer()
    data = {"name": "test"}
    metadata = FormatMetadata()
    result = restorer.restore(data, metadata, "unknown_format")
    assert result == data
