# xwapi

Engine-agnostic API framework for the eXonware stack. `xwapi` exposes `xwentity` and `xwaction` as HTTP endpoints, standardizes error contracts, supports production middleware, and now includes a durable action pipeline plus API token lifecycle/metering.

*Longer guide: [README_LONG.md](README_LONG.md).*

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com

[![Status](https://img.shields.io/badge/status-beta-blue.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Install

| Install | When to use |
|---------|-------------|
| `pip install exonware-xwapi` | Core runtime |
| `pip install exonware-xwapi[lazy]` | Lazy dependency loading |
| `pip install exonware-xwapi[full]` | Full production dependency set |

---

## Quick start

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

## New production features

- **Engine-agnostic error contract:** `xwapi_error_to_http_parts` plus adapters keeps `XWAPIError` transport-neutral.
- **Outbox + singleton worker pipeline:** `ActionPipelineManager`, `AOutboxStore`/`InMemoryOutboxStore`, and `BackgroundWorker`.
- **API token lifecycle:** create/list/revoke tokens, usage tracking, balance/recharge, idempotent metering.
- **Provider abstractions:** `IAuthProvider`, `IStorageProvider`, `IPaymentProvider` with in-memory and library adapters.
- **API token middleware:** bearer verification, optional scope enforcement, deny-unmapped policy, usage metering via `Idempotency-Key`.
- **Admin/operations endpoints:** server status/health/pipeline controls and token admin endpoints.
- **Production guardrails:** environment-based admin token enforcement and admin read-protection support.

---

## eXonware integration

`xwapi` now explicitly integrates with:

- `xwsystem` (serialization, logging/utilities)
- `xwaction` (action registration and execution)
- `xwentity` (entity-driven API surfaces)
- `xwschema` (schema validation/generation integration points)
- `xwdata` (data/serialization integration paths)

---

## Docs and tests

- Start at [docs/INDEX.md](docs/INDEX.md).
- API and architecture references: [docs/REF_15_API.md](docs/REF_15_API.md), [docs/REF_13_ARCH.md](docs/REF_13_ARCH.md).
- Test layers: `0.core`, `1.unit`, `2.integration`, `3.advance`.
- Full run: `python tests/runner.py`

---

## Async support

- Core runtime includes async methods across facade, token manager, middleware paths, and server actions.
- Async APIs are recommended for I/O-heavy and concurrent workloads.

---

MIT - see [LICENSE](LICENSE). Homepage: https://exonware.com
Version: 0.9.0.2 | Updated: 01-Apr-2026

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
