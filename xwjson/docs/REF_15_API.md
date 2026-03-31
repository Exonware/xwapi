<!-- docs/REF_15_API.md (output of GUIDE_15_API) -->
# xwjson — API Reference

Complete API reference for xwjson library.

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** connect@exonware.com  
**Version:** 0.0.1.0  
**Last Updated:** 07-Feb-2026

---

## Table of Contents

- [XWJSON Facade](#xwjson-facade)
- [XWJSONSerializer](#xwjsonserializer)
- [Pipeline options (encryption, archive, binary)](#pipeline-options-encryption-archive-binary)
- [XWJSONDataOperations](#xwjsondataoperations)
- [XWJSONConfig](#xwjsonconfig)
- [Errors](#errors)
- [Helpers](#helpers)

---

## XWJSON Facade

Main facade class providing simplified API for xwjson operations.

### Class: `XWJSON`

```python
from exonware.xwjson import XWJSON
```

#### Constructor

```python
XWJSON(
    max_depth: Optional[int] = None,
    max_size_mb: Optional[float] = None,
    enable_cache: bool = True,
    **options
)
```

**Parameters:** `max_depth`, `max_size_mb`, `enable_cache`, `**options`

#### Methods

- `load(path)` — Load XWJSON file asynchronously  
- `save(data, path)` — Save data to XWJSON file asynchronously  
- `encode(data, options)` — Encode data to XWJSON format  
- `decode(data, options)` — Decode data from XWJSON format  
- `serializer` — Property to access XWJSONSerializer instance  

---

## XWJSONSerializer

Main serializer class. Constructor: `max_depth`, `max_size_mb`, `read_parser`, `write_parser`, `enable_cache`. Properties: `codec_id`, `media_types`, `file_extensions`, `supports_lazy_loading`, `supports_schema_validation`. Methods: `load_file_async`, `save_file_async`, `load_file`, `save_file`, `encode`, `decode`.

### Pipeline options (encryption, archive, binary)

`save_file` and `load_file` (and async variants) accept options that are passed to the xwsystem serialization pipeline. When used, XWJSON uses single-file format (no dual-file).

| Option | Type | Description |
|--------|------|-------------|
| `password` | str | Password for encryption (KDF used). |
| `key` | bytes | Raw key for encryption (32 bytes). |
| `encryption` | dict | `{ "key" or "password", "algorithm" }` (e.g. `aes256-gcm`). |
| `encryption_algorithm` | str | Algorithm when using `key`/`password` (default `aes256-gcm`). |
| `archive` | str \| True | Compression: `"gzip"`, `"zst"`, `"lz4"`, or `True` to auto-detect on load. |
| `binary_framing` | bool | Length-prefix framing. |

**Example (encrypted save/load):**
```python
from exonware.xwjson import XWJSONSerializer, is_encrypted
ser = XWJSONSerializer()
ser.save_file(data, "out.xwjson", password="secret")
assert is_encrypted("out.xwjson")
data = ser.load_file("out.xwjson", password="secret")
```

**Example (encrypted + compressed):**
```python
ser.save_file(data, "out.xwjson.zst", password="secret", archive="zst")
```

---

## Helpers

### `is_encrypted(bytes_or_path: bytes | str) -> bool`

**Import:** `from exonware.xwjson import is_encrypted`

Returns `True` if the payload or file is an XWJE encrypted envelope (first 4 bytes `b'XWJE'`). Accepts raw bytes or a file path (peeks first 4 bytes).

---

## XWJSONDataOperations

Data operations: `atomic_read`, `read_path`, `read_page`, `iterate_pages`, `batch_save`, `batch_load`. See _archive/API_REFERENCE.md for full parameter details.

---

## XWJSONConfig

Configuration: `max_depth`, `max_size_mb`, `enable_cache`.

---

## Errors

Base: `XWJSONError` (from exonware.xwjson.errors).

---

## See Also

- [GUIDE_01_USAGE.md](GUIDE_01_USAGE.md) — Usage and how-to  
- _archive/ — Basic, advanced, performance, queries, schema, format conversion, extension guides  

---

*Output of GUIDE_15_API.*
