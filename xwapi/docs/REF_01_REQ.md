# Requirements Reference (REF_01_REQ)

**Project:** xwapi  
**Sponsor:** eXonware.com / eXonware Backend Team  
**Version:** 0.0.1.1  
**Last Updated:** 31-Mar-2026  
**Produced by:** [GUIDE_01_REQ.md](../guides/GUIDE_01_REQ.md)

---

## Purpose of This Document

This document is the **single source of raw and refined requirements** collected from the project sponsor and stakeholders. It is updated on every requirements-gathering run. When the **Clarity Checklist** (section 12) reaches the agreed threshold, use this content to fill REF_12_IDEA, REF_22_PROJECT, REF_13_ARCH, REF_14_DX, REF_15_API, and planning artifacts. Template structure: [GUIDE_01_REQ.md](../guides/GUIDE_01_REQ.md).

---

## 1. Vision and Goals

| Field | Content |
|-------|---------|
| One-sentence purpose | Provide **both an agent and a server**, **capitalize on xwaction**, and use **xwentity** so that in the future it is **easy to create an API server or client** (e.g. FastAPI) **on the fly**—e.g. by loading **JSON files** with OpenAPI settings for servers, and for the client a **customized version of the same**. (sponsor) |
| Primary users/beneficiaries | eXonware stack; developers building API servers or clients with minimal code; teams driving APIs from config (e.g. JSON/OpenAPI). (sponsor + REF_22) |
| Success (6 mo / 1 yr) | 6 mo: Stable API (agent + server), REF_* compliance. 1 yr: Production use, JSON/OpenAPI-driven server & client. (Refine per REF_22.) |
| Top 3–5 goals (ordered) | 1) **Provide both agent and server** in one framework. 2) **Capitalize on xwaction** (actions as first-class endpoints). 3) **Use the power of xwentity** (entities → API surface). 4) **Easy API server or client on the fly** (e.g. FastAPI)—future: load JSON with OpenAPI settings for server; for client, a customized version of the same. 5) Unified API surface, OpenAPI, middleware, Firebase-style parity. (sponsor + REF_22) |
| Problem statement | Need one place to build both API servers and API clients, driven by xwentity and xwaction, with a path to config-driven setup (JSON/OpenAPI) for creating server or client on the fly. (sponsor) |

## 2. Scope and Boundaries

| In scope | Out of scope | Dependencies | Anti-goals |
|----------|--------------|--------------|------------|
| **Agent and server** in one framework; xwaction as first-class; xwentity-driven APIs; OpenAPI generation; middleware; multi-protocol (REST, GraphQL, gRPC, WebSocket); API client/agent. **Future:** easy API server or client on the fly (e.g. load JSON files with OpenAPI settings for server; customized OpenAPI/config for client). (sponsor + REF_22, README) | Implementing auth (xwauth) or storage (xwstorage); UI. (inferred) | xwsystem, xwentity, xwschema, xwaction, FastAPI, uvicorn, requests. (from pyproject.toml) | Hard-coded runtimes; exposing engine internals as stable API. (inferred) |

### 2a. Reverse-Engineered Evidence (from codebase)

- **Facade:** `facade.py` — **XWAPI**(entities, storage, auth, actions, config); **generate_openapi()** (OpenAPI 3.1); **create_app(engine=...)**; uses XWAction for action execution; engine-agnostic (delegates to engine for app creation).
- **Server engines:** `server/engines/` — FastAPI, Flask, gRPC, GraphQL, WebSocket, http_base; email engines (SMTP, IMAP, POP3); **XWApiServer** (`xwserver.py`), **IApiServer**; **ApiServerEngineRegistry**, **api_server_engine_registry**.
- **Middleware:** `server/middleware/` — auth, observability, rate-limit, tenant, trace, pause, admin-auth, API-token metering middleware.
- **Client/agent:** `client/xwclient.py` — **XWApiAgent**; `client/engines/` — **IApiAgentEngine**, **NativeAgentEngine**, **ApiAgentEngineRegistry**; connect to external APIs (same framework).
- **Schema & OpenAPI:** `common/openapi.py` — merge_openapi_schemas, validate_openapi_schema, export_openapi_schema; `schema/generator.py`, `schema/validator.py`, `schema/graphql.py`.
- **App factory:** `common/app.py` — create_app, register_module, add_version_router, add_openapi_endpoints.
- **Governance:** `server/governance/` — lockfile, registry. **Admin/ops:** status/health/pipeline and token-management operations.
- **Pipeline:** `server/pipeline/` — outbox abstraction, in-memory outbox, singleton background worker, pipeline manager.
- **Token management:** `token_management.py`, `providers.py`, `contracts.py` — token lifecycle, usage metering, recharge and provider abstractions (`IAuthProvider`, `IStorageProvider`, `IPaymentProvider`).
- **Future (sponsor):** Easy API server or client on the fly—e.g. load **JSON files** with OpenAPI settings to spin up a server; for client, a **customized version** of the same (same config shape, client-specific options). Builds on existing OpenAPI merge/validate/export and engine registry.

## 3. Stakeholders and Sponsor

| Sponsor (name, role, final say) | Main stakeholders | External customers/partners | Doc consumers |
|----------------------------------|-------------------|-----------------------------|---------------|
| eXonware (company); eXonware Backend Team (author, maintainer, final say). Vision: agent + server, xwaction, xwentity; future: JSON/OpenAPI for server & client on the fly. | Project sponsor / eXonware; downstream REF owners. | None currently. Future: open-source adopters. | Downstream REF_22/REF_13 owners; devs building APIs; AI agents (Cursor). |

## 4. Compliance and Standards

| Regulatory/standards | Security & privacy | Certifications/evidence |
|----------------------|--------------------|--------------------------|
| Per GUIDE_00_MASTER, GUIDE_11_COMP. (inferred) | Auth integration, input validation (align with xwauth). (from REF_22) | TBD |

## 5. Product and User Experience

| Main user journeys/use cases | Developer persona & 1–3 line tasks | Usability/accessibility | UX/DX benchmarks |
|-----------------------------|------------------------------------|--------------------------|------------------|
| Expose entities (xwentity) as REST/OpenAPI; register xwaction endpoints; run server or use agent as client. **Future:** Load JSON (OpenAPI settings) → create server or client on the fly. (sponsor + REF_22) | Developer: XWAPI(entities=[User], storage=storage, actions=[...]), generate_openapi(), create_app(engine="fastapi"); or XWApiAgent for client. Runtime path: XWApiServer with pipeline/token admin operations. (README, sponsor) | Clear API surface, PROJECT_PHASES, ENGINE_ROADMAP. (from REF_22) | TBD |

## 6. API and Surface Area

| Main entry points / "key code" | Easy (1–3 lines) vs advanced | Integration/existing APIs | Not in public API |
|--------------------------------|------------------------------|---------------------------|-------------------|
| XWAPI; entities, storage, title, version; generate_openapi(), create_app(). XWApiServer runtime methods for pipeline and token management. | Easy: XWAPI(entities=[...], storage=...), create_app(engine="fastapi"). Advanced: middleware policy, engine adapters, outbox pipeline, API token controls. | xwentity, xwstorage, xwaction, xwsystem, xwschema, xwdata, OpenAPI. (from REF_22) | Engine/middleware internals. (inferred) |

## 7. Architecture and Technology

| Required/forbidden tech | Preferred patterns | Scale & performance | Multi-language/platform |
|-------------------------|--------------------|----------------------|-------------------------|
| Python 3.12+; xwsystem, xwentity, xwschema; FastAPI, uvicorn. (from pyproject.toml) | Server/engine abstraction, middleware pipeline, OpenAPI; lite/lazy/full. (from REF_22) | Engine and middleware performance. (from REF_22) | Python; REST/OpenAPI surface. (inferred) |

## 8. Non-Functional Requirements (Five Priorities)

| Security | Usability | Maintainability | Performance | Extensibility |
|----------|-----------|-----------------|-------------|---------------|
| Auth integration, input validation. (from REF_22) | Clear API, PROJECT_PHASES, ENGINE_ROADMAP. (from REF_22) | REF_*, logs under docs/. (from REF_22) | Engine and middleware performance. (from REF_22) | Pluggable engines and middleware. (from REF_22) |

## 9. Milestones and Timeline

| Major milestones | Definition of done (first) | Fixed vs flexible |
|------------------|----------------------------|-------------------|
| M1–M3 Done (core servers/engines, OpenAPI/middleware, REF_* compliance). (from REF_22) | M3: REF_22, REF_13, INDEX. (from REF_22) | TBD |

## 10. Risks and Assumptions

| Top risks | Assumptions | Kill/pivot criteria |
|-----------|-------------|----------------------|
| TBD | Firebase backend parity as API gateway/Functions surface. (from REF_22) | TBD |

## 11. Workshop / Session Log (Optional)

| Date | Type | Participants | Outcomes |
|------|------|---------------|----------|
| 11-Feb-2026 | Reverse‑engineer + Q&A | User + Agent | Sponsor vision: provide both agent and server; capitalize on xwaction; use xwentity; future = easy API server or client on the fly (e.g. load JSON with OpenAPI settings for server, customized version for client). REF_01 updated. |

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
