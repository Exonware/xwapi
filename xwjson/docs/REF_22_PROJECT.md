# Project Reference — xwjson

**Library:** exonware-xwjson  
**Last Updated:** 07-Feb-2026

Requirements and project status (output of GUIDE_22_PROJECT). Per REF_35_REVIEW.

---

## Vision

xwjson provides an **extended binary JSON format** as the single version of truth for format conversions in the eXonware ecosystem. It delivers MessagePack-based encoding, lazy loading, reference support, xwnode/xwschema integration, and transaction support—aligning with Firebase-style storage format needs when used with xwstorage/xwdata.

---

## Goals

1. **Binary-first, fast:** MessagePack-based encoding; 10x faster than text JSON where applicable.
2. **Lazy loading:** Defer parsing until access for performance.
3. **Reference support:** Format-specific refs ($ref, @href, YAML anchors) preserved.
4. **Universal intermediate:** Single source of truth for xwdata/xwformats conversions.
5. **Async-first:** All I/O async by default with sync wrappers.
6. **Transactions and batch:** ACID semantics and dependency-aware batch operations.

---

## Functional Requirements (Summary)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-001 | XWJSON encoder/serializer, lazy loading | High | Done |
| FR-002 | Reference support and resolution | High | Done |
| FR-003 | xwnode integration (graphs, topological sort) | High | Done |
| FR-004 | xwschema validation, compiled schemas | High | Done |
| FR-005 | Format metadata preservation (YAML, XML, TOML) | Medium | Done |
| FR-006 | Transaction support (ACID) | Medium | Done |
| FR-007 | Batch operations (dependency-aware, parallel) | Medium | Done |
| FR-008 | Async-first API | High | Done |

---

## Non-Functional Requirements (5 Priorities)

1. **Security:** Input validation, no code execution from data, safe ref resolution.
2. **Usability:** Clear API, docs (usage, performance, schema, queries), extension guides.
3. **Maintainability:** Contracts/base/facade, 4-layer tests, REF_* and logs.
4. **Performance:** Benchmarks, lazy parsing, batch speed (4–5x).
5. **Extensibility:** Extension points, format conversion pipeline.

---

## Project Status Overview

- **Current phase:** Beta (High). Encoder, serializer, references, transactions, batch, schema, XWNode integration; 0.core, 1.unit, 2.integration, 3.advance.
- **Docs:** docs/ with API, usage, performance, schema, queries, extension; REF_22_PROJECT (this file), REF_35_REVIEW; logs/reviews/.
- **Firebase alignment:** Storage format role when used with xwstorage/xwdata.

---

## Milestones

| Milestone | Target | Status |
|-----------|--------|--------|
| M1 — Core format and serializer | v0.0.1 | Done |
| M2 — References, xwnode, xwschema | v0.0.1 | Done |
| M3 — REF_* and review compliance | v0.0.1 | Done (REF_22 added) |
| M4 — xwjson-editor (if separate) | Future | Clarify scope (REF_35) |

---

## Traceability

- **Project → Arch:** This document → [REF_13_ARCH.md](REF_13_ARCH.md). **Ideas:** [REF_12_IDEA.md](REF_12_IDEA.md).
- **Review evidence:** [REF_35_REVIEW.md](REF_35_REVIEW.md), [logs/reviews/REVIEW_20260207_PROJECT_STATUS.md](logs/reviews/REVIEW_20260207_PROJECT_STATUS.md).

---

*See GUIDE_22_PROJECT.md for requirements process.*
