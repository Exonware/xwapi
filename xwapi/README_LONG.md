# xwapi (long version)

Production-focused, engine-agnostic API layer for eXonware services.

`xwapi` now combines:
- entity and action exposure (`xwentity`, `xwaction`)
- durable background action execution (Outbox + singleton worker)
- API token generation, usage metering, and recharge
- provider-based auth/storage/payment integration
- consistent transport-neutral error contracts

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

Use `XWAPI` when you want entity/action to API generation quickly.

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

Use `XWApiServer` for direct server orchestration, middleware controls, admin APIs, and pipeline/token features.

```python
from exonware.xwapi import XWApiServer

server = XWApiServer(engine="fastapi")
app = server.app
```

---

## New features added

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
- [docs/REF_13_ARCH.md](docs/REF_13_ARCH.md)
- [docs/REF_15_API.md](docs/REF_15_API.md)
- [docs/REF_22_PROJECT.md](docs/REF_22_PROJECT.md)
- [docs/REF_51_TEST.md](docs/REF_51_TEST.md)

---

Version: 0.0.1.1 | Updated: 31-Mar-2026
