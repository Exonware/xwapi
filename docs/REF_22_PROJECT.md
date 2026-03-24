# Project Reference — xwapi

**Library:** exonware-xwapi  
**Last Updated:** 07-Feb-2026

Requirements and project status (output of GUIDE_22_PROJECT). Per REF_35_REVIEW.

---

## Vision

xwapi provides the **API layer** for the eXonware ecosystem: servers, engines, middleware, OpenAPI, query integration, serialization, and xwaction integration. It is the backend surface for Firebase replacement (Hosting/Functions/API gateway role), exposing unified APIs that delegate to xwauth, xwstorage, xwquery, xwdata, and other libraries.

---

## Goals

1. **Unified API surface:** Servers and engines that expose REST/OpenAPI and query endpoints.
2. **Middleware and engines:** Pluggable middleware; engine abstraction for different runtimes.
3. **OpenAPI:** Generation and compliance for API documentation and client generation.
4. **Integration:** xwaction, xwquery, serialization; auth (xwauth) and storage (xwstorage) where used.
5. **Firebase backend parity:** API gateway and Functions hosting surface.

---

## Functional Requirements (Summary)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-001 | Server and engine abstraction | High | Done |
| FR-002 | Middleware pipeline | High | Done |
| FR-003 | OpenAPI generation and compliance | High | Done |
| FR-004 | Query and serialization integration | High | Done |
| FR-005 | xwaction integration | Medium | Done |
| FR-006 | 4-layer tests (0.core–3.advance) | High | Done |

---

## Non-Functional Requirements (5 Priorities)

1. **Security:** Auth integration, input validation (align with xwauth).
2. **Usability:** Clear API surface, PROJECT_PHASES, ENGINE_ROADMAP.
3. **Maintainability:** REF_*, logs under docs/.
4. **Performance:** Engine and middleware performance.
5. **Extensibility:** Pluggable engines and middleware.

---

## Project Status Overview

- **Current phase:** Alpha (Medium). 57+ Python files; servers, engines, middleware, OpenAPI, query, serialization, action integration; 4-layer tests.
- **Docs:** REF_22_PROJECT (this file), REF_13_ARCH, REF_35_REVIEW; PROJECT_PHASES, ENGINE_ROADMAP, FUTURE_PLANS; logs/reviews/.

---

## Milestones

| Milestone | Target | Status |
|-----------|--------|--------|
| M1 — Core servers and engines | v0.x | Done |
| M2 — OpenAPI and middleware | v0.x | Done |
| M3 — REF_* and review compliance | v0.x | Done (REF_22, REF_13, INDEX) |

---

## Traceability

- **Project → Arch:** This document → [REF_13_ARCH.md](REF_13_ARCH.md).
- **Review evidence:** [REF_35_REVIEW.md](REF_35_REVIEW.md), [logs/reviews/](logs/reviews/).

---

*See GUIDE_22_PROJECT.md for requirements process.*
