# Requirements Reference (REF_01_REQ)

**Project:** xwjson  
**Sponsor:** TBD  
**Version:** 0.0.1  
**Last Updated:** 11-Feb-2026 00:00:00.000  
**Produced by:** [GUIDE_01_REQ.md](../guides/GUIDE_01_REQ.md)

---

## Purpose of This Document

This document is the **single source of raw and refined requirements** collected from the project sponsor and stakeholders. It is updated on every requirements-gathering run. When the **Clarity Checklist** (section 12) reaches the agreed threshold, use this content to fill REF_12_IDEA, REF_22_PROJECT, REF_13_ARCH, REF_14_DX, REF_15_API, and planning artifacts. Template structure: [GUIDE_01_REQ.md](../guides/GUIDE_01_REQ.md).

---

## 1. Vision and Goals

| Field | Content |
|-------|---------|
| One-sentence purpose | **An amazing binary format** — faster and smaller than any other; next-generation data format with referencing, lazy loading, atomic read/write, indexing, paging; can be used as a database when one isn’t available; leverages xwdata (and stack) for high-end performance. (Sponsor confirmed.) |
| **Design principle (sponsor)** | **Use everywhere.** Pushing XWJSON everywhere means the whole eXonware stack is high-end performance. Cheaper, faster, better, more optimized—it has all the advantages. (Sponsor confirmed.) |
| Primary users/beneficiaries | **Heavily used with:** anything involving xwentity, xwmodels; local databases when a database is not available; xwdata, xwformats, xwstorage. Whole eXonware ecosystem—adoption everywhere for high-end performance. (Sponsor confirmed.) |
| Success (6 mo / 1 yr) | TBD |
| Top 3–5 goals (ordered) | 1) **Faster and smaller** than any other binary format. 2) **Advanced operations:** referencing, lazy loading, atomic access, atomic read/write, indexing, paging—everything needed for next-generation formats. 3) **Database-capable** when needed (indexing, paging). 4) **Speed** via xwdata and stack integration. 5) **Adoption everywhere** so the whole library stack is high-end performance. (Sponsor confirmed.) |
| Problem statement | Need one binary format that is faster, smaller, and more capable (references, lazy loading, atomic I/O, indexing, paging) than alternatives—usable as format and as local DB when no database is available; adoption across the stack for maximum performance. (Sponsor confirmed.) |

## 2. Scope and Boundaries

| In scope | Out of scope | Dependencies | Anti-goals |
|----------|--------------|--------------|------------|
| **Binary:** Faster and smaller than any other; MessagePack-based. **Advanced:** referencing ($ref, @href, anchors), lazy loading, **atomic read/write**, atomic access; **indexing and paging** (database-capable when no DB available). Format metadata preservation, ACID transactions, batch operations, async-first API; xwnode/xwschema integration. Next-generation capabilities throughout. (Sponsor confirmed.) | UI (xwjson-editor separate); full storage backend implementation (xwstorage). (Sponsor confirmed.) | xwsystem, xwnode; xwdata (advanced I/O/speed); optional xwschema (entry point), xwquery. (Sponsor confirmed; pyproject, REF_13) | Code execution from data; exposing raw encoder internals as stable API. (Sponsor confirmed.) |

### 2a. Features (reverse‑engineered from codebase)

Objective list of implemented capabilities, from `src/exonware/xwjson` and `formats/binary/xwjson/`:

| Area | Implemented features |
|------|----------------------|
| **Binary format** | MessagePack-based encoding (XWJSONEncoder/XWJSONDecoder); magic bytes `XWJ1`, versioned header; format codes (JSON, YAML, XML, TOML); flags: HAS_METADATA, HAS_INDEX, COMPRESSED, ENCRYPTED, STREAMING, SCHEMA_INCLUDED. Hybrid parser: msgspec (read), orjson (write); single-file and dual-file (data + meta/index) layouts; record-level streaming with `record_offsets` index; parallel encoding for large record sets. |
| **Lazy loading** | LazyFileProxy (defer file read; mmap for large files); LazySerializationProxy (defer parse until access); LazyXWNodeProxy; LazyReferenceProxy. Configurable lazy threshold. |
| **References** | XWJSONReferenceResolver: JSON `$ref` (JSON Reference, JSON Pointer), XML `@href` (XLink, XPointer), YAML `*anchor`/`&anchor`, TOML inline, xwformats/xwsyntax. Circular detection, resolution cache, path validation. |
| **Transactions** | XWJSONTransaction: ACID semantics; write-ahead logging (WAL); atomic commit/rollback; `write`, `update_path`, `commit`; TransactionContext. |
| **Batch operations** | SmartBatchExecutor: dependency graph (XWJSONDependencyGraph, uses xwnode); conflict detection (path-based); topological sort; parallel execution of independent operations (4–5x for independent ops); sequential for dependent; zero conflicts guaranteed. |
| **Indexing & paging** | Encoder: optional index in payload; dual-file format for large data; record_offsets for streaming. Serializer: file cache (< 10MB), index cache (all files), mtime invalidation; `get_record_page(page_number, page_size)`. XWJSONDataOperations: `atomic_read`, `atomic_write`, `read_page(page_number, page_size, path)`; path-level caching (LRU via xwnode); JSON index–style access. |
| **Atomic I/O** | Serializer: `atomic_update_path`, `atomic_read_path`; save via temp file + atomic rename. Ops: `atomic_read`, `atomic_write`, `atomic_update`, `atomic_delete`, `atomic_update_path`; transaction-safe file updates. |
| **Format metadata** | FormatMetadata: YAML (anchors, aliases, tags, comments, multi-doc), XML (namespaces, attributes, PI, CDATA, DOCTYPE), TOML (table arrays, inline tables, date/time, comments), JSON (comments, trailing commas, refs), xwformats/xwsyntax. FormatMetadataExtractor, FormatMetadataRestorer for lossless round-trip. |
| **Schema** | XWJSONSchemaValidator; xwschema entry point for validation and compiled schemas. |
| **Conversion** | XWJSONConverter: source format → XWJSON → target format; lossless; metadata preserved. |
| **API surface** | XWJSONSerializer (load_file_async, save_file_async, load_file, save_file; decode with optional metadata/index/header_info); XWJSON facade; XWJSONDataOperations (streaming, path-based ops, query via xwquery); contracts IXWJSONSerializer, IXWJSONOperations, IXWJSONConverter. |
| **Caching & perf** | File cache (small files), index cache (all files), mtime tracking; dual-file cache invalidation; LRU path cache in ops; optional enable_cache in serializer. |
| **Errors** | XWJSONError, XWJSONSerializationError, XWJSONEncodingError, XWJSONDecodingError, XWJSONLazyLoadingError, XWJSONTransactionError, XWJSONReferenceError, XWJSONSchemaError. |

*Source: encoder.py, serializer.py, lazy.py, references.py, transactions.py, batch_operations.py, dependency_graph.py, metadata.py, schema.py, converter.py, operations/xwjson_ops.py, defs.py, errors.py, contracts.py.*

## 3. Stakeholders and Sponsor

| Sponsor (name, role, final say) | Main stakeholders | External customers/partners | Doc consumers |
|----------------------------------|-------------------|-----------------------------|---------------|
| TBD | Project sponsor / eXonware | TBD | xwdata, xwformats, xwstorage; devs using XWJSON. |

## 4. Compliance and Standards

| Regulatory/standards | Security & privacy | Certifications/evidence |
|----------------------|--------------------|--------------------------|
| Per GUIDE_00_MASTER, GUIDE_11_COMP. (inferred) | Input validation, no code execution from data, safe ref resolution. (from REF_22) | TBD |

## 5. Product and User Experience

| Main user journeys/use cases | Developer persona & 1–3 line tasks | Usability/accessibility | UX/DX benchmarks |
|-----------------------------|------------------------------------|--------------------------|------------------|
| Load/save XWJSON (sync/async); lazy parse; resolve refs; atomic read/write; indexing and paging; use as local DB when no database available; validate with schema; transactions and batch. (Sponsor confirmed.) | **Same usage as xwsystem JSON serialization** — create serializer, load/save by path; plus one-liners and any-format→any-format below. (Sponsor confirmed.) | Clear API, docs; adoption everywhere = high-end performance for the stack. (Sponsor confirmed.) | Faster, smaller, cheaper, more optimized; next-generation capabilities. (Sponsor confirmed.) |

### 5a. Usage: same as xwsystem serialization + one-liners and conversion

**XWJSON is used exactly the same way as JSON serialization from xwsystem** — create a serializer, call load/save (or encode/decode) by path or bytes. Same mental model; drop-in style.

| Use case | Example (intended DX) |
|----------|------------------------|
| **One-liner load** | `data = XWJSONSerializer().load_file("data.xwjson")` (sync) or `data = await XWJSONSerializer().load_file_async("data.xwjson")` (async). Simple: give path, get data. |
| **Load from any format → save to XWJSON** | Load JSON/YAML/TOML/XML with the same pattern as xwsystem (e.g. load from file or bytes), then save to .xwjson: `data = load_from_yaml("in.yaml")  # or xwsystem serializer`; `XWJSONSerializer().save_file(data, "out.xwjson")`. Or use XWJSONConverter to go from any supported format into XWJSON and write. |
| **Convert anything → anything** | `converter = XWJSONConverter()`; `result = await converter.convert(source_data, "yaml", "json")` (or "json"→"toml", "xml"→"xwjson", etc.). Source → XWJSON → target; one code path for all format pairs; lossless metadata where supported. |

*Sponsor: one-liner load; show load from any format → save to xwjson; show convert anything to anything.*

## 6. API and Surface Area

| Main entry points / "key code" | Easy (1–3 lines) vs advanced | Integration/existing APIs | Not in public API |
|--------------------------------|------------------------------|---------------------------|-------------------|
| **Facade:** XWJSON, XWJSONSerializer. **Load/save:** load_file_async, save_file_async, load_file, save_file (sync wrappers). **Atomic/paging:** atomic_read_path, atomic_update_path, get_record_page(page_number, page_size). **Options:** create_index_file, atomic, return_metadata. (Reverse‑engineered: serializer.py, __init__.py.) | **Same as xwsystem serialization:** create serializer, load_file/save_file (or load_file_async/save_file_async). **One-liner:** `data = XWJSONSerializer().load_file("data.xwjson")`. **Load from any format → save to xwjson:** load JSON/YAML/TOML/XML (same API as xwsystem), then `serializer.save_file(data, "out.xwjson")`. **Anything → anything:** `await XWJSONConverter().convert(source_data, source_format, target_format)`. **Advanced:** XWJSONDataOperations, XWJSONTransaction, SmartBatchExecutor; lazy proxies; reference resolution. (Sponsor + reverse‑engineered.) | xwnode (dependency graph, LRU cache); xwschema (entry point, validation); xwquery (optional, in ops); UniversalCodecRegistry (xwsystem, auto-register). (Reverse‑engineered.) | XWJSONEncoder/XWJSONDecoder internals; _encode_* / _decode_*; dependency_graph internal state; LazyFileProxy/LazySerializationProxy implementation details; raw encoder flags/struct layout. (Reverse‑engineered.) |

## 7. Architecture and Technology

| Required/forbidden tech | Preferred patterns | Scale & performance | Multi-language/platform |
|-------------------------|--------------------|----------------------|-------------------------|
| Python 3.12+; xwsystem, xwnode; msgspec, orjson; nest-asyncio. (pyproject.toml, encoder.py) | Facade (XWJSON, XWJSONSerializer); contracts (IXWJSONSerializer, IXWJSONOperations, IXWJSONConverter); abstract bases (AXWJSON*); hybrid parser (read/write); dual-file and single-file strategies; class-level cache (file + index). (Reverse‑engineered.) | Encoder: 150MB/s+ target, parallel encoding above record threshold; batch: 4–5x for independent ops; lazy + mmap for large files; index cache for all files; file cache for &lt;10MB. (encoder.py, batch_operations.py, serializer.py.) | Python only. (inferred) |

## 8. Non-Functional Requirements (Five Priorities)

| Security | Usability | Maintainability | Performance | Extensibility |
|----------|-----------|-----------------|-------------|---------------|
| Input validation, no code execution from data, safe ref resolution. (from REF_22) | Clear API, docs; use everywhere = stack high-end performance. (Sponsor confirmed.) | Contracts/base/facade, 4-layer tests, REF_*. (from REF_22) | **Faster and smaller than any other;** lazy parsing, batch speed, atomic I/O, indexing/paging; xwdata integration. (Sponsor confirmed.) | Extension points, format conversion pipeline; database-capable. (Sponsor confirmed.) |

## 9. Milestones and Timeline

| Major milestones | Definition of done (first) | Fixed vs flexible |
|------------------|----------------------------|-------------------|
| M1–M3 Done (core format, refs/xwnode/xwschema, REF_* compliance); M4 xwjson-editor scope future. (from REF_22) | M3: REF_* and review compliance. (from REF_22) | TBD |

## 10. Risks and Assumptions

| Top risks | Assumptions | Kill/pivot criteria |
|-----------|-------------|----------------------|
| TBD | xwschema via entry point (no direct dep to avoid circular); xwjson-editor scope clarified in REF_35. (from REF_22, pyproject) | TBD |

## 11. Workshop / Session Log (Optional)

| Date | Type | Participants | Outcomes |
|------|------|---------------|----------|
| 11-Feb-2026 | Reverse‑engineer + Q&A | User + Agent | Draft from code/docs (REF_22, REF_13, README, pyproject, src); user to confirm. |
| 11-Feb-2026 | Q&A Batch A (Vision) | Sponsor + Agent | Vision: amazing binary—faster/smaller than any other; advanced ops (references, lazy load, atomic R/W, indexing, paging); database-capable; use everywhere (xwentity, xwmodels, local DB); whole stack high-end performance; cheaper, faster, better, optimized. |
| 11-Feb-2026 | Reverse‑engineer features | Agent | Section 2a added: objective feature list from codebase (binary format, lazy loading, references, transactions, batch, indexing/paging, atomic I/O, metadata, schema, converter, API, caching, errors). Sections 6 and 7 updated with reverse‑engineered entry points and patterns. |
| 11-Feb-2026 | Usage (xwsystem parity + one-liners) | Sponsor + Agent | XWJSON used exactly like xwsystem JSON serialization. Added 5a: one-liner `data = XWJSONSerializer().load_file("data.xwjson")`; load from any format → save to xwjson; convert anything→anything via XWJSONConverter. Section 6 Easy row updated. |

## 12. Clarity Checklist

| # | Criterion | ☐ |
|---|-----------|---|
| 1 | Vision and one-sentence purpose filled and confirmed | ☑ |
| 2 | Primary users and success criteria defined | ☑ |
| 3 | Top 3–5 goals listed and ordered | ☑ |
| 4 | In-scope and out-of-scope clear | ☑ |
| 5 | Dependencies and anti-goals documented | ☑ |
| 6 | Sponsor and main stakeholders identified | ☑ |
| 7 | Compliance/standards stated or deferred | ☑ |
| 8 | Main user journeys / use cases listed | ☑ |
| 9 | API / "key code" expectations captured | ☑ |
| 10 | Architecture/technology constraints captured | ☑ |
| 11 | NFRs (Five Priorities) addressed | ☑ |
| 12 | Milestones and DoD for first milestone set | ☑ |
| 13 | Top risks and assumptions documented | ☑ |
| 14 | Sponsor confirmed vision, scope, priorities | ☑ |

**Clarity score:** 14 / 14. **Ready to fill downstream docs?** ☑ Yes

---

*Inferred content is marked; sponsor confirmation required. Per GUIDE_01_REQ.*
