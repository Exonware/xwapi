# xwjson - Advanced Usage Guide

This guide covers advanced usage patterns for xwjson.

## Lazy Loading

Lazy loading defers parsing until data is actually accessed, improving performance for large files.

```python
from exonware.xwjson import XWJSONSerializer

serializer = XWJSONSerializer()

# Load with lazy mode (default)
data = await serializer.load_file_async("large_file.xwjson", lazy=True)

# Data is parsed only when accessed
print(data["users"][0]["name"])  # Parsed on access
```

## Reference Resolution

xwjson supports format-specific references: JSON `$ref`, XML `@href`, YAML `*anchor`.

```python
from exonware.xwjson import XWJSONSerializer

serializer = XWJSONSerializer()

# Load with reference resolution
data = await serializer.load_file_async("data_with_refs.xwjson")

# References are automatically resolved
# JSON: {"$ref": "#/definitions/user"} → resolved value
# XML: <element @href="schema.xml#User"/> → resolved value
# YAML: *user_anchor → resolved value
```

## Transactions

ACID transactions with zero performance penalty.

```python
from exonware.xwjson import XWJSONSerializer

serializer = XWJSONSerializer()

async with serializer.transaction():
    # All operations in this block are atomic
    data = await serializer.load_file_async("data.xwjson")
    data["count"] = data.get("count", 0) + 1
    await serializer.save_file_async(data, "data.xwjson")
    # Commits automatically, or rolls back on error
```

## Batch Operations

Dependency-aware batch operations with parallel execution (4-5x faster).

```python
from exonware.xwjson.operations import XWJSONDataOperations

ops = XWJSONDataOperations()

# Batch save with automatic dependency resolution
files = ["file1.xwjson", "file2.xwjson", "file3.xwjson"]
data_list = [{"id": i} for i in range(3)]

# Automatically handles dependencies and parallel execution
await ops.batch_save(files, data_list)

# Batch load
loaded = await ops.batch_load(files)
```

## Path Operations (JSONPointer)

Access specific paths in data without loading entire file.

```python
from exonware.xwjson.operations import XWJSONDataOperations

ops = XWJSONDataOperations()

# Read specific path
name = await ops.read_path("data.xwjson", "/users/0/name")

# Update specific path
await ops.update_path("data.xwjson", "/users/0/age", 31)

# Delete specific path
await ops.delete_path("data.xwjson", "/users/0/email")
```

## Paging

Efficient paging with automatic indexing.

```python
from exonware.xwjson.operations import XWJSONDataOperations

ops = XWJSONDataOperations()

# Read page of records
page = await ops.read_page(
    "data.xwjson",
    page_number=1,
    page_size=10,
    path="/users"  # Optional: paginate specific path
)

# Iterate through pages
async for page in ops.iterate_pages("data.xwjson", page_size=10):
    for record in page:
        print(record)
```

## xwnode Integration

Use xwnode for dependency graphs and graph operations.

```python
from exonware.xwjson import XWJSONSerializer
from exonware.xwnode import XWNode

serializer = XWJSONSerializer()

# Load data with dependency graph
data = await serializer.load_file_async("data_with_deps.xwjson")

# Access dependency graph
graph = serializer.get_dependency_graph(data)

# Topological sort for processing order
sorted_nodes = graph.topological_sort()

# Graph operations
all_dependencies = graph.get_all_dependencies("node_id")
```

## xwschema Integration

Schema validation with fast compiled schemas.

```python
from exonware.xwjson import XWJSONSerializer

serializer = XWJSONSerializer()

# Load with schema validation
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    }
}

data = await serializer.load_file_async(
    "data.xwjson",
    schema=schema  # Validates automatically
)
```

## Next Steps

- See [Performance Guide](GUIDE_PERFORMANCE.md) for optimization tips
- See [Format Conversion Guide](GUIDE_FORMAT_CONVERSION.md) for format conversion
- See [Schema Validation Guide](GUIDE_SCHEMA_VALIDATION.md) for schema validation
