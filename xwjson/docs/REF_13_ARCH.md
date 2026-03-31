# Architecture Reference — exonware-xwjson

**Library:** exonware-xwjson  
**Producing guide:** GUIDE_13_ARCH  
**Last Updated:** 07-Feb-2026

---

## Overview

xwjson provides an **extended binary JSON format** (MessagePack-based) as the single version of truth for format conversions. Architecture follows eXonware contracts/base/facade patterns and async-first I/O.

**Design Philosophy:** Binary-first, lazy loading, reference preservation, transaction and batch support; integration with xwnode and xwschema.

---

## High-Level Structure

```
xwjson/
+-- contracts.py      # Interfaces (IClass)
+-- base.py            # Abstract bases (AClass)
+-- facade.py          # Public API (XWJSON, entry points)
+-- errors.py          # Exceptions
+-- defs.py            # Constants, enums
+-- config.py          # Configuration
+-- version.py
+-- common/            # Shared utilities (e.g. benchmarking)
+-- formats/
|   +-- binary/
|       +-- xwjson/    # Core XWJSON implementation
|           +-- encoder.py
|           +-- serializer.py
|           +-- lazy.py
|           +-- references.py
|           +-- metadata.py
|           +-- schema.py
|           +-- transactions.py
|           +-- batch_operations.py
|           +-- dependency_graph.py
|           +-- converter.py
+-- operations/        # High-level operations
    +-- xwjson_ops.py
```

---

## Boundaries

- **Public API:** Facade exposes XWJSON encode/decode, lazy loading, references, transactions, batch operations. Entry points used by xwdata, xwformats, xwstorage.
- **Formats:** Binary XWJSON format lives under `formats/binary/xwjson/`; encoder, serializer, lazy, references, transactions, batch, dependency graph, converter.
- **Operations:** `operations/xwjson_ops.py` provides high-level ops; common utilities (e.g. benchmarking) in `common/`.

---

## Design Patterns

- **Strategy:** Format handling (encoder, serializer, converter).
- **Facade:** Single public API; internals modular.
- **Lazy loading:** Defer parsing until access (see `lazy.py`).
- **Contract/base:** Interfaces in `contracts.py`, abstract bases in `base.py`.

---

## Delegation

- **xwsystem:** Serialization/codec base, validation, security.
- **xwnode:** Graph structures, topological sort (REF_22 FR-003).
- **xwschema:** Validation, compiled schemas (REF_22 FR-004).
- **xwdata / xwformats:** Consume XWJSON as universal intermediate; format conversion pipeline.

---

## Layering

1. **Contracts:** Encoder/serializer/ref/transaction interfaces.
2. **Base:** Abstract implementations and shared logic.
3. **Facade:** Public XWJSON API.
4. **Formats:** XWJSON binary implementation and converter.

---

## Async and Performance

- Async-first I/O with sync wrappers (REF_22 FR-008).
- Lazy parsing for performance; batch operations 4–5x (REF_22).
- Benchmarks and lazy behaviour documented in usage/performance docs.

---

## Traceability

- **Requirements:** [REF_22_PROJECT.md](REF_22_PROJECT.md)
- **Ideas:** [REF_12_IDEA.md](REF_12_IDEA.md)
- **API:** [REF_15_API.md](REF_15_API.md)

---

*See GUIDE_13_ARCH.md for architecture process.*
