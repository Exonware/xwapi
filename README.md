# xwapi

**Build once, publish anywhere.** `xwapi` is the entity- and **exposable-action** layer for eXonware: define `xwaction` operations and `xwentity` models once, then **publish** them over HTTP/OpenAPI (bots, consoles, and other adapters align to the same contracts). It also supports the **other direction** — **clients and agents** that **consume** those actions via `XWApiAgent` and related client engines.

Default HTTP engine is **FastAPI** (full OpenAPI/async ecosystem); **Flask** is a registered alternate so you can swap ASGI vs WSGI at app construction without rewriting actions. See [docs/REF_24_ALTERNATIVES.md](docs/REF_24_ALTERNATIVES.md) for comparable libraries and engine notes.

Beyond HTTP wiring: standardized errors, production middleware, durable action pipeline, API token lifecycle/metering.

*Longer guide: [README_LONG.md](README_LONG.md).*

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com

[![Status](https://img.shields.io/badge/status-beta-blue.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

---

## 📦 Install

| Install | When to use |
|---------|-------------|
| `pip install exonware-xwapi` | Core runtime |
| `pip install exonware-xwapi[lazy]` | Lazy dependency loading |
| `pip install exonware-xwapi[full]` | Full production dependency set |
| `pip install exonware-xwapi[engines-http]` | Optional HTTP engines (Starlette, Quart, Sanic, aiohttp, BlackSheep, Litestar, Django, Mangum) |

---

## 🚀 Quick start

```python
from exonware.xwapi import XWAPI
from exonware.xwentity import XWEntity


class User(XWEntity):
    name: str
    email: str
    age: int


api = XWAPI(entities=[User], title="My API", version="1.0.0")
app = api.create_app(engine="fastapi")
```

---

## 🆕 New production features

- **Engine-agnostic error contract:** `xwapi_error_to_http_parts` plus adapters keeps `XWAPIError` transport-neutral.
- **Outbox + singleton worker pipeline:** `ActionPipelineManager`, `AOutboxStore`/`InMemoryOutboxStore`, and `BackgroundWorker`.
- **API token lifecycle:** create/list/revoke tokens, usage tracking, balance/recharge, idempotent metering.
- **Provider abstractions:** `IAuthProvider`, `IStorageProvider`, `IPaymentProvider` with in-memory and library adapters.
- **API token middleware:** bearer verification, optional scope enforcement, deny-unmapped policy, usage metering via `Idempotency-Key`.
- **Admin/operations endpoints:** server status/health/pipeline controls and token admin endpoints.
- **Production guardrails:** environment-based admin token enforcement and admin read-protection support.

---

## 💻 Client side

Use **`XWApiAgent`** (and client engines) to discover `XWAction` methods, attach auth/session flows, and treat remote APIs as the consumer half of the same exposable-action model.

---

## 🔗 eXonware integration

`xwapi` now explicitly integrates with:

- `xwsystem` (serialization, logging/utilities)
- `xwaction` (action registration and execution)
- `xwentity` (entity-driven API surfaces)
- `xwschema` (schema validation/generation integration points)
- `xwdata` (data/serialization integration paths)

---

## 🌐 Ecosystem functional contributions

For `xwapi`, each XW library covers a specific feature and requirement boundary rather than acting as a generic dependency layer.
You can use `xwapi` standalone with its core install and existing non-XW components.
Adding more XW packages is optional and mainly useful when you want full enterprise and mission-critical infrastructure patterns under your own control.

| Supporting XW lib | What it provides to xwapi | Functional requirement it satisfies |
|------|----------------|----------------|
| **XWAction** | Metadata, registration, execution, and engine adapters for *exposable actions* (HTTP, and other surfaces). | Same business action from server publish to client consume; reusable across FastAPI/Flask engines. |
| **XWEntity** | Entity-first domain surface that xwapi can expose directly as API resources. | Stable domain contracts and lower boilerplate for CRUD/API scaffolding. |
| **XWSystem** | Shared error and runtime foundations (logging, config, async/helpers, transport-neutral utility layers). | Uniform API behavior across FastAPI/Flask/GraphQL/gRPC and predictable ops behavior in production. |
| **XWSchema** | Validation and schema integration points for request/response shaping and API contracts. | Strong input/output contract enforcement and safer API evolution. |
| **XWStorage** | Persistence abstraction used by server pipeline components and token/admin paths where durable state is needed. | Durable action/outbox/token workflows instead of in-memory-only behavior. |
| **XWAuth** | Authentication/authorization provider integrations used by middleware and protected routes. | API security requirements (token validation, authz boundaries, tenant-safe access). |
| **XWData** | Data transformation/serialization support for mixed payloads and format conversion paths. | Multi-format payload handling without duplicating conversion logic in endpoint code. |

This is the practical edge: one place composes **publish** (server) and **consume** (agent/client) paths around the same exposable actions, instead of stitching unrelated libraries per service.

---

## 📖 Docs and tests

- Start at [docs/INDEX.md](docs/INDEX.md).
- Alternatives + FastAPI/Flask engines: [docs/REF_24_ALTERNATIVES.md](docs/REF_24_ALTERNATIVES.md).
- Full engine registry: [docs/REF_25_ENGINES.md](docs/REF_25_ENGINES.md).
- API and architecture references: [docs/REF_15_API.md](docs/REF_15_API.md), [docs/REF_13_ARCH.md](docs/REF_13_ARCH.md).
- Test layers: `0.core`, `1.unit`, `2.integration`, `3.advance`.
- Full run: `python tests/runner.py`

---

## ⏱️ Async support

- Core runtime includes async methods across facade, token manager, middleware paths, and server actions.
- Async APIs are recommended for I/O-heavy and concurrent workloads.

---

Apache-2.0 - see [LICENSE](LICENSE). Homepage: https://exonware.com
Version: 0.9.0.11 | Updated: 18-Apr-2026

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
