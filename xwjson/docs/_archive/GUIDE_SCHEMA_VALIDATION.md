# xwjson - Schema Validation Guide

This guide covers schema validation with xwjson using xwschema integration.

## Schema Validation Overview

XWJSON integrates with xwschema for fast compiled schema validation.

## Basic Validation

```python
from exonware.xwjson import XWJSONSerializer

serializer = XWJSONSerializer()

# Define schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0}
    },
    "required": ["name"]
}

# Load with schema validation
data = await serializer.load_file_async(
    "data.xwjson",
    schema=schema  # Validates automatically
)

# If validation fails, raises XWJSONError
```

## Fast Compiled Schemas

xwschema compiles schemas for maximum performance.

```python
from exonware.xwjson import XWJSONSerializer
from exonware.xwschema import compile_schema

# Compile schema once (reusable)
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    }
}

compiled_schema = compile_schema(schema)

# Use compiled schema for faster validation
serializer = XWJSONSerializer()
data = await serializer.load_file_async(
    "data.xwjson",
    schema=compiled_schema
)
```

## Complex Schema Validation

```python
from exonware.xwjson import XWJSONSerializer

serializer = XWJSONSerializer()

# Complex schema with nested objects and arrays
schema = {
    "type": "object",
    "properties": {
        "users": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "age": {"type": "integer", "minimum": 0, "maximum": 150}
                },
                "required": ["name", "email"]
            }
        }
    },
    "required": ["users"]
}

# Validate automatically
data = await serializer.load_file_async("data.xwjson", schema=schema)
```

## Schema Validation on Save

Validate data before saving:

```python
from exonware.xwjson import XWJSONSerializer

serializer = XWJSONSerializer()

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    }
}

data = {"name": "Alice", "age": 30}

# Validate before saving
await serializer.save_file_async(data, "data.xwjson", schema=schema)

# Invalid data raises error
invalid_data = {"name": "Alice", "age": "30"}  # age should be integer
try:
    await serializer.save_file_async(invalid_data, "data.xwjson", schema=schema)
except XWJSONError as e:
    print(f"Validation error: {e}")
```

## Schema Evolution

Handle schema evolution gracefully:

```python
from exonware.xwjson import XWJSONSerializer

serializer = XWJSONSerializer()

# Old schema
old_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"}
    }
}

# New schema (added age field)
new_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}  # New field
    }
}

# Load with backward-compatible schema
data = await serializer.load_file_async("data.xwjson", schema=new_schema)
# Works even if data has old format (age is optional)
```

## Performance Tips

1. **Compile schemas once** and reuse
2. **Use schema validation** for data integrity
3. **Enable caching** for schema compilation
