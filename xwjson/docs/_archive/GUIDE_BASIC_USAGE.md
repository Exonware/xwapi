# xwjson - Basic Usage Guide

This guide covers basic usage patterns for xwjson.

## Quick Start

### Installation

```bash
pip install exonware-xwjson
```

### Basic Save and Load

```python
import asyncio
from exonware.xwjson import XWJSONSerializer

async def main():
    # Create serializer
    serializer = XWJSONSerializer()
    
    # Sample data
    data = {
        "users": [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"},
        ]
    }
    
    # Save to XWJSON format
    await serializer.save_file_async(data, "data.xwjson")
    
    # Load from XWJSON format
    loaded = await serializer.load_file_async("data.xwjson")
    
    print(loaded)  # Same data structure

asyncio.run(main())
```

## Using the Facade API

```python
from exonware.xwjson import XWJSON

# Create XWJSON instance
xwjson = XWJSON()

# Save and load
await xwjson.save(data, "data.xwjson")
loaded = await xwjson.load("data.xwjson")

# Encode/decode to bytes
encoded = xwjson.encode(data)
decoded = xwjson.decode(encoded)
```

## Configuration Options

```python
# Create serializer with custom configuration
serializer = XWJSONSerializer(
    max_depth=100,           # Maximum nesting depth
    max_size_mb=100.0,       # Maximum file size in MB
    enable_cache=True        # Enable file caching
)
```

## Sync Wrapper (for compatibility)

```python
# Sync operations (wraps async internally)
serializer = XWJSONSerializer()

# Sync save and load
data = serializer.load_file("data.xwjson")
serializer.save_file(data, "output.xwjson")
```

## Error Handling

```python
from exonware.xwjson.errors import XWJSONError

try:
    data = await serializer.load_file_async("missing.xwjson")
except XWJSONError as e:
    print(f"Error loading file: {e}")
```

## Next Steps

- See [Advanced Usage Guide](GUIDE_ADVANCED_USAGE.md) for advanced patterns
- See [Performance Guide](GUIDE_PERFORMANCE.md) for optimization tips
- See [Format Conversion Guide](GUIDE_FORMAT_CONVERSION.md) for format conversion
- See [Schema Validation Guide](GUIDE_SCHEMA_VALIDATION.md) for schema validation
