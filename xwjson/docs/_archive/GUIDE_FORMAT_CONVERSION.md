# xwjson - Format Conversion Guide

This guide covers format conversion using xwjson as the intermediate format.

## Format Conversion Overview

XWJSON serves as the universal intermediate format for all format conversions. Convert between any formats via XWJSON.

## JSON to XWJSON

```python
from exonware.xwjson import XWJSONSerializer
from exonware.xwsystem.io.codec import get_codec

# Load JSON
json_codec = get_codec("json")
json_data = json_codec.load_file("data.json")

# Save as XWJSON
xwjson_serializer = XWJSONSerializer()
await xwjson_serializer.save_file_async(json_data, "data.xwjson")
```

## XWJSON to JSON

```python
from exonware.xwjson import XWJSONSerializer
from exonware.xwsystem.io.codec import get_codec

# Load XWJSON
xwjson_serializer = XWJSONSerializer()
data = await xwjson_serializer.load_file_async("data.xwjson")

# Save as JSON
json_codec = get_codec("json")
json_codec.save_file(data, "data.json")
```

## XWJSON to YAML

```python
from exonware.xwjson import XWJSONSerializer
from exonware.xwsystem.io.codec import get_codec

# Load XWJSON
xwjson_serializer = XWJSONSerializer()
data = await xwjson_serializer.load_file_async("data.xwjson")

# Save as YAML
yaml_codec = get_codec("yaml")
yaml_codec.save_file(data, "data.yaml")
```

## Format Roundtrip

```python
from exonware.xwjson import XWJSONSerializer
from exonware.xwsystem.io.codec import get_codec

# Roundtrip: JSON → XWJSON → YAML → XWJSON → JSON
json_codec = get_codec("json")
xwjson_serializer = XWJSONSerializer()
yaml_codec = get_codec("yaml")

# Load JSON
data = json_codec.load_file("input.json")

# Convert via XWJSON
await xwjson_serializer.save_file_async(data, "temp.xwjson")
xwjson_data = await xwjson_serializer.load_file_async("temp.xwjson")

# Convert to YAML
yaml_codec.save_file(xwjson_data, "output.yaml")

# Convert back to JSON via XWJSON
yaml_data = yaml_codec.load_file("output.yaml")
await xwjson_serializer.save_file_async(yaml_data, "temp.xwjson")
final_data = await xwjson_serializer.load_file_async("temp.xwjson")
json_codec.save_file(final_data, "output.json")
```

## Reference Preservation

XWJSON preserves format-specific references during conversion.

```python
# JSON with $ref
json_data = {
    "users": [{"name": "Alice"}],
    "$ref": "#/users/0"  # JSON reference
}

# Convert to XWJSON (preserves reference)
await xwjson_serializer.save_file_async(json_data, "data.xwjson")
loaded = await xwjson_serializer.load_file_async("data.xwjson")

# Convert to YAML (reference converted to YAML anchor)
yaml_codec.save_file(loaded, "data.yaml")
# Result: *user_anchor (YAML format)
```

## Format Metadata Preservation

XWJSON preserves format-specific metadata.

```python
# YAML with anchors and aliases
yaml_data = {
    "users": [{"name": "Alice"}],
    "reference": "*users_0"  # YAML anchor
}

# Convert to XWJSON (preserves metadata)
await xwjson_serializer.save_file_async(yaml_data, "data.xwjson")

# Convert to XML (metadata converted to XML namespace)
xml_codec = get_codec("xml")
xml_codec.save_file(loaded, "data.xml")
# Result: XML with preserved structure
```

## Supported Formats

XWJSON can convert to/from all xwsystem supported formats:

- JSON
- YAML
- XML
- TOML
- MessagePack
- BSON
- CSV
- And more...

## Conversion Performance

Converting via XWJSON is optimized:

1. **Binary format**: 10x faster than text formats
2. **Lazy loading**: Parse only when needed
3. **Metadata preservation**: No data loss during conversion
