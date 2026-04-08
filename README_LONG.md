# xwapi (long version)

**Build once, publish anywhere** — production layer for **exposable actions** and entities on the eXonware stack.

You author `xwaction` operations and optional `xwentity` models once, then **publish** over HTTP (OpenAPI-first; FastAPI default engine, Flask alternate). The same ideas extend to bots, consoles, or other adapters that call the same contracts. **Clients** use `XWApiAgent` and client engines to **consume** remote APIs symmetrically.

`xwapi` combines:
- **Publisher**: entity + action exposure, server engines (FastAPI / Flask), OpenAPI merge
- **Consumer**: agents, OAuth/session helpers, action discovery
- durable background execution (Outbox + singleton worker)
- API token lifecycle, usage metering, recharge
- provider-based auth/storage/payment
- transport-neutral error contracts

Short version: [README.md](README.md)

---

## Installation

```bash
pip install exonware-xwapi
pip install exonware-xwapi[lazy]
pip install exonware-xwapi[full]
```

---

## Core building blocks

### 1) `XWAPI` facade

Use `XWAPI` when you want entity + exposable actions turned into an HTTP app quickly (`engine="fastapi"` or `engine="flask"`).

```python
from exonware.xwapi import XWAPI
from exonware.xwentity import XWEntity


class User(XWEntity):
    name: str
    email: str


api = XWAPI(entities=[User], title="Demo API", version="1.0.0")
app = api.create_app(engine="fastapi")
```

### 2) `XWApiServer` runtime server

Use `XWApiServer` for direct server orchestration, middleware controls, admin APIs, and pipeline/token features. Pass `engine="fastapi"` for ASGI/OpenAPI defaults or `engine="flask"` for WSGI-oriented deployments — same registration model, different framework.

```python
from exonware.xwapi import XWApiServer

server = XWApiServer(engine="fastapi")
app = server.app
```

### 3) `XWApiAgent` (client / consumer)

Use `XWApiAgent` when building **clients** or bots that own `XWAction` methods and integrate with `xwauth` flows against APIs.

---

## New features added

### HTTP engines: FastAPI vs Flask

- **FastAPI** (default): async ASGI, automatic OpenAPI, dependency injection, Starlette middleware.
- **Flask**: registered alternate engine for WSGI stacks; choose at `XWAPI.create_app(...)` / `XWApiServer(...)` construction (not hot-swapping a live process).
- See [docs/REF_24_ALTERNATIVES.md](docs/REF_24_ALTERNATIVES.md) for ecosystem comparison.

### Engine/protocol agnosticism hardening

- Error model is normalized in `XWAPIError` and mapped to transport via adapters.
- `xwapi_error_to_http_parts` provides framework-neutral body/status/headers.
- Middleware imports and internals are moved toward Starlette-level primitives where applicable.

### Outbox + singleton background worker

- `AOutboxStore` + `InMemoryOutboxStore` for job persistence abstraction.
- `BackgroundWorker` enforces single active worker per process.
- `ActionPipelineManager` orchestrates handlers, enqueueing, and worker lifecycle.
- `XWApiServer` exposes:
  - `register_pipeline_handler()`
  - `enqueue_pipeline_job()`
  - `enqueue_action_job()`
  - `start_pipeline_worker()`
  - `stop_pipeline_worker()`

### API token management and billing-style metering

- `APITokenManager`:
  - create/list/revoke token lifecycle
  - usage recording with idempotency
  - recharge and balance APIs
- Provider contracts:
  - `IAuthProvider`
  - `IStorageProvider`
  - `IPaymentProvider`
- Implementations:
  - `LocalAuthProvider`, `XWAuthLibraryProvider`
  - `InMemoryStorageProvider`, `XWStorageProvider`
  - `InMemoryPaymentProvider`

### API token middleware

- `APITokenMiddleware` validates bearer API tokens.
- Optional route scope enforcement with deny-unmapped mode.
- Request metering using `Idempotency-Key` to avoid double charging.
- Admin bearer bypass and exempt path handling for operational routes.

### Production guardrails

- Environment controls:
  - `XWAPI_ENV`
  - `XWAPI_ADMIN_TOKEN`
  - `XWAPI_ADMIN_PROTECT_READ`
  - `XWAPI_ALLOW_INSECURE_ADMIN`
  - `XWAPI_API_TOKEN_MIDDLEWARE`
- In production mode, admin token guardrails are enforced unless explicitly overridden.

### Admin/ops API surface (selected)

- Server:
  - `server_status`
  - `server_health`
  - `server_health_root`
  - `server_pipeline`
- Token management:
  - `server_tokens_create`
  - `server_tokens_list`
  - `server_tokens_revoke`
  - `server_tokens_usage_record`
  - `server_tokens_usage_list`
  - `server_tokens_recharge`
  - `server_tokens_balance`

---

## eXonware stack reuse

`xwapi` reuses the ecosystem heavily:
- `xwsystem`: logging + serializers + utility primitives
- `xwaction`: action registration and engine routing
- `xwentity`: entity-first API model surface
- `xwschema`: schema and validator integration points
- `xwdata`: data/serialization paths

---

## Testing strategy

Layered test suites:
- `0.core`
- `1.unit`
- `2.integration`
- `3.advance`

Run all:

```bash
python tests/runner.py
```

Focused:

```bash
pytest tests/1.unit/
pytest tests/2.integration/
pytest tests/3.advance/
```

---

## Documentation map

- [docs/INDEX.md](docs/INDEX.md)
- [docs/REF_24_ALTERNATIVES.md](docs/REF_24_ALTERNATIVES.md)
- [docs/REF_13_ARCH.md](docs/REF_13_ARCH.md)
- [docs/REF_15_API.md](docs/REF_15_API.md)
- [docs/REF_22_PROJECT.md](docs/REF_22_PROJECT.md)
- [docs/REF_51_TEST.md](docs/REF_51_TEST.md)

---

Version: 0.9.0.3 | Updated: 05-Apr-2026
