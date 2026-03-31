# Idea Reference — exonware-xwjson

**Company:** eXonware.com  
**Producing guide:** GUIDE_12_IDEA  
**Last Updated:** 07-Feb-2026

---

## Overview

xwjson provides an **extended binary JSON format** as the single version of truth for format conversions in the eXonware ecosystem. This document captures product direction and ideas that shape xwjson; approved ideas flow to [REF_22_PROJECT.md](REF_22_PROJECT.md) and [REF_13_ARCH.md](REF_13_ARCH.md).

### Alignment with eXonware 5 Priorities

- **Security:** Input validation, no code execution from data, safe ref resolution.
- **Usability:** Clear API, docs (usage, performance, schema, queries), extension guides.
- **Maintainability:** Contracts/base/facade, 4-layer tests, REF_* and logs.
- **Performance:** Benchmarks, lazy parsing, batch speed (4–5x).
- **Extensibility:** Extension points, format conversion pipeline.

**Related Documents:**
- [REF_22_PROJECT.md](REF_22_PROJECT.md) — Requirements
- [REF_13_ARCH.md](REF_13_ARCH.md) — Architecture
- [REF_35_REVIEW.md](REF_35_REVIEW.md) — Review summary

---

## Product Direction (from REF_22)

### ✅ [IDEA-001] Binary-first extended JSON

**Status:** ✅ Approved → Implemented  
**Date:** 07-Feb-2026

**Problem:** Text JSON is slow and does not preserve references or metadata needed for Firebase-style storage and xwdata/xwformats conversions.

**Proposed Solution:** MessagePack-based XWJSON with lazy loading, reference support ($ref, @href, YAML anchors), and transaction/batch semantics.

**Outcome:** Implemented in xwjson (encoder, serializer, references, transactions, batch, xwnode/xwschema integration). See REF_22_PROJECT FR-001–FR-008.

---

### ✅ [IDEA-002] Universal intermediate for conversions

**Status:** ✅ Approved → Implemented  
**Date:** 07-Feb-2026

**Problem:** Multiple format converters need a single canonical shape to avoid N² conversions.

**Proposed Solution:** XWJSON as the single source of truth; xwdata/xwformats convert to/from XWJSON.

**Outcome:** Implemented; Firebase alignment when used with xwstorage/xwdata.

---

### 🔍 [IDEA-003] xwjson-editor and tooling

**Status:** 🔍 Exploring  
**Date:** 07-Feb-2026

**Problem:** Developers need to view and edit .xwjson files in IDE and potentially web/other platforms.

**Proposed Solution:** xwjson-editor (VS Code/Cursor extension + reusable TypeScript core); Python codec via exonware-xwjson.

**Next Steps:** Clarify scope (REF_22 M4); link REF_22 to xwjson-editor REF_22.

---

## Idea Catalog

| ID       | Title                          | Status   | Links        |
|----------|--------------------------------|----------|--------------|
| IDEA-001 | Binary-first extended JSON     | Approved | REF_22 FR-*  |
| IDEA-002 | Universal intermediate         | Approved | REF_22       |
| IDEA-003 | xwjson-editor and tooling      | Exploring| REF_22 M4    |

---

*See GUIDE_12_IDEA.md for idea process. Requirements: REF_22_PROJECT.md.*
