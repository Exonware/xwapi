# Architecture Reference — xwapi

**Library:** exonware-xwapi  
**Last Updated:** 07-Feb-2026

Architecture and design (output of GUIDE_13_ARCH). Per REF_35_REVIEW.

---

## Overview

xwapi provides the **API layer**: server and engine abstraction, middleware pipeline, OpenAPI generation, and integration with xwquery, serialization, and xwaction. It does not implement auth or storage itself; it delegates to xwauth and xwstorage where required.

---

## Boundaries

- **Public API:** Server/engine facades; API routes and middleware registration.
- **Servers / engines:** Pluggable server implementations (e.g. ASGI/WSGI); engine types for different runtimes.
- **Middleware:** Request/response pipeline; auth, logging, validation hooks.
- **OpenAPI:** Generation from routes and schemas; documentation and client tooling.
- **Query / serialization:** Delegation to xwquery and xwsystem serialization.

---

## Layering

1. **Facade:** High-level API and server bootstrap.
2. **Engines:** Runtime-specific engine implementations.
3. **Middleware:** Ordered middleware stack.
4. **Routes:** Endpoint registration and OpenAPI exposure.

---

## Delegation

- **xwauth:** Authentication and authorization for protected routes.
- **xwstorage:** Storage operations when API exposes storage-backed resources.
- **xwquery:** Query execution when API exposes query endpoints.
- **xwaction:** Action/workflow decoration and validation.
- **xwsystem:** Serialization and utilities.

---

*See ENGINE_ROADMAP.md and PROJECT_PHASES.md for roadmap. Requirements: REF_22_PROJECT.md.*
