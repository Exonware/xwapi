# xwjson - Performance Guide

This guide covers performance optimization tips for xwjson.

## Binary Format Performance

XWJSON uses MessagePack-based encoding, providing 10x faster serialization than JSON text.

```python
from exonware.xwjson import XWJSONSerializer

serializer = XWJSONSerializer()

# Binary format is 10x faster than JSON
await serializer.save_file_async(data, "data.xwjson")  # Fast binary format
```

## Lazy Loading Performance

Enable lazy loading to defer parsing until access, improving initial load time.

```python
from exonware.xwjson import XWJSONSerializer

serializer = XWJSONSerializer()

# Lazy loading: parse only when accessed
data = await serializer.load_file_async("large_file.xwjson", lazy=True)

# Parsed on access
print(data["users"][0])  # Only this part is parsed
```

## Caching Performance

Enable file caching for repeated access.

```python
from exonware.xwjson import XWJSONSerializer

# Enable caching (default: True)
serializer = XWJSONSerializer(enable_cache=True)

# First load: reads from disk
data1 = await serializer.load_file_async("data.xwjson")

# Second load: reads from cache (much faster)
data2 = await serializer.load_file_async("data.xwjson")
```

## Batch Operations Performance

Use batch operations for 4-5x faster processing with parallel execution.

```python
from exonware.xwjson.operations import XWJSONDataOperations

ops = XWJSONDataOperations()

# Batch operations use parallel execution automatically
files = [f"file{i}.xwjson" for i in range(100)]
data_list = [{"id": i} for i in range(100)]

# 4-5x faster than sequential operations
await ops.batch_save(files, data_list)
```

## Path Operations Performance

Use path operations to access specific data without loading entire file.

```python
from exonware.xwjson.operations import XWJSONDataOperations

ops = XWJSONDataOperations()

# Only loads and parses the specific path
name = await ops.read_path("large_file.xwjson", "/users/0/name")

# Much faster than loading entire file
# all_data = await serializer.load_file_async("large_file.xwjson")
# name = all_data["users"][0]["name"]
```

## Paging Performance

Use paging with automatic indexing for efficient large file access.

```python
from exonware.xwjson.operations import XWJSONDataOperations

ops = XWJSONDataOperations()

# Paging uses path-level caching for optimal performance
page = await ops.read_page(
    "large_file.xwjson",
    page_number=1,
    page_size=10,
    path="/users"  # Only loads this path
)

# Subsequent pages use cached index (instant access)
page2 = await ops.read_page("large_file.xwjson", page_number=2, page_size=10, path="/users")
```

## Memory-Mapped I/O

For large files, xwjson automatically uses memory-mapped I/O.

```python
# Automatically uses mmap for files > 1MB
data = await serializer.load_file_async("large_file.xwjson")  # Uses mmap automatically
```

## Performance Best Practices

1. **Use lazy loading** for large files
2. **Enable caching** for repeated access
3. **Use batch operations** for multiple files
4. **Use path operations** instead of loading entire files
5. **Use paging** for large datasets
6. **Use transactions** (zero performance penalty)

## Benchmarking

Compare performance with JSON:

```python
import time
from exonware.xwjson import XWJSONSerializer

serializer = XWJSONSerializer()

# Benchmark XWJSON
start = time.time()
await serializer.save_file_async(data, "data.xwjson")
xwjson_time = time.time() - start

# Benchmark JSON (standard library)
import json
start = time.time()
with open("data.json", "w") as f:
    json.dump(data, f)
json_time = time.time() - start

print(f"XWJSON: {xwjson_time:.3f}s")
print(f"JSON: {json_time:.3f}s")
print(f"Speedup: {json_time / xwjson_time:.1f}x")
```
