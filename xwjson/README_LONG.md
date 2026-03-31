# exonware-xwjson (long version)

Extended binary JSON for eXonware: a stable intermediate representation for conversions, with lazy loading, references, and transactions.

*Short overview: [README.md](README.md).*

---

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** connect@exonware.com  
**Version:** 0.9.0.7

---

## What it is

**xwjson** is a separate package (like xwformats) that extends xwsystem-style serialization with a binary, metadata-rich format. It is meant as the hub format when you convert between JSON, YAML, XML, and friends without throwing away anchors, namespaces, or schema hints.

---

## Quick start

### Installation

```bash
pip install exonware-xwjson[full]

# Or minimal (install heavy deps yourself as needed)
pip install exonware-xwjson
```

### Basic usage

```python
from exonware.xwjson import XWJSONSerializer

serializer = XWJSONSerializer()

# Async (recommended)
data = await serializer.load_file_async("data.xwjson")
await serializer.save_file_async(data, "output.xwjson")

# Sync wrappers
data = serializer.load_file("data.xwjson")
serializer.save_file(data, "output.xwjson")
```

### Facade API

```python
from exonware.xwjson import XWJSON

xwjson = XWJSON()

await xwjson.save(data, "data.xwjson")
loaded = await xwjson.load("data.xwjson")

encoded = xwjson.encode(data)
decoded = xwjson.decode(encoded)
```

---

## Capabilities

### Binary-first I/O

MessagePack-based files are typically much faster than parsing large text JSON. Exact numbers depend on data and hardware; see archived performance guides under `docs/_archive/` if present.

```python
from exonware.xwjson import XWJSONSerializer

serializer = XWJSONSerializer()
await serializer.save_file_async(data, "data.xwjson")
```

### Lazy loading

```python
data = await serializer.load_file_async("large_file.xwjson", lazy=True)
print(data["users"][0]["name"])  # parses along the access path
```

### References

JSON `$ref`, XML `@href`, YAML `*anchor` style references are carried and resolved according to the serializer configuration.

```python
data = await serializer.load_file_async("data_with_refs.xwjson")
```

### Transactions

```python
async with serializer.transaction():
    data = await serializer.load_file_async("data.xwjson")
    data["count"] += 1
    await serializer.save_file_async(data, "data.xwjson")
```

### Batch operations

```python
from exonware.xwjson.operations import XWJSONDataOperations

ops = XWJSONDataOperations()
await ops.batch_save(files, data_list)
```

### Format conversion

Use XWJSON as the middle format when chaining conversions (e.g. JSON → XWJSON → YAML) so metadata survives the hop where the codecs support it.

---

## Documentation

### Guides (`docs/` and `docs/_archive/`)

- Basic usage - `docs/_archive/GUIDE_BASIC_USAGE.md`
- Advanced usage - `docs/_archive/GUIDE_ADVANCED_USAGE.md`
- Performance - `docs/_archive/GUIDE_PERFORMANCE.md`
- Format conversion - `docs/_archive/GUIDE_FORMAT_CONVERSION.md`
- Schema validation - `docs/_archive/GUIDE_SCHEMA_VALIDATION.md`

### Examples

See `examples/` for serialization, lazy loading, references, transactions, batch work, conversion, schema validation, performance, and xwnode integration samples.

### API

- [REF_15_API.md](docs/REF_15_API.md)
- [REF_22_PROJECT.md](docs/REF_22_PROJECT.md)
- [GUIDE_01_USAGE.md](docs/GUIDE_01_USAGE.md)

---

## Performance (high level)

Benchmarks belong in project docs; expect large wins on binary I/O vs raw JSON text on big payloads, and strong gains on batch paths when parallelism applies. See `docs/_archive/GUIDE_PERFORMANCE.md` for methodology and numbers.

---

## Troubleshooting

- **File not found** - Check paths; use absolute paths if the cwd is unclear.
- **Schema validation errors** - Verify schema and payload shape.
- **Large files feel slow** - Try lazy loading and path-scoped reads instead of materializing everything.
- **Reference errors** - Ensure targets exist and reference syntax matches the source format.

**Help:** [docs/](docs/), `examples/`, or connect@exonware.com for project contact.

---

## Where it fits

xwjson adds binary storage, lazy trees, WAL-backed transactions, reference resolution across formats, and batch orchestration on top of the same serialization ecosystem as xwsystem/xwformats. That combination is the differentiator versus "just use MessagePack or JSON."

---

## License

MIT License

---

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** connect@exonware.com
