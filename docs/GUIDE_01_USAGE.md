# xwapi — Usage Guide

**Last Updated:** 31-Mar-2026

This guide covers the current `xwapi` runtime capabilities: facade usage, server usage, action pipeline, and API token management.

## 1) Facade-first usage (`XWAPI`)

Use this path for fast entity/action to API generation.

```python
from exonware.xwapi import XWAPI
from exonware.xwentity import XWEntity


class User(XWEntity):
    name: str
    email: str


api = XWAPI(entities=[User], title="Users API", version="1.0.0")
app = api.create_app(engine="fastapi")
```

## 2) Server-first usage (`XWApiServer`)

Use this path when you need runtime controls, pipeline orchestration, and admin endpoints.

```python
from exonware.xwapi import XWApiServer

server = XWApiServer(engine="fastapi")
app = server.app
```

## 3) Register actions

`xwapi` integrates with `xwaction` so action definitions become API endpoints.

```python
from exonware.xwaction import XWAction


@XWAction(operationId="ping", profile="endpoint")
def ping() -> dict[str, str]:
    return {"status": "ok"}


server.register_action(ping, path="/ping", method="GET")
```

## 4) Pipeline (Outbox + singleton worker)

```python
def job_handler(payload: dict[str, str]) -> dict[str, bool]:
    return {"ok": True}


server.register_pipeline_handler("jobs.email", job_handler)
server.start_pipeline_worker()
server.enqueue_pipeline_job("jobs.email", {"to": "user@example.com"})
```

## 5) API token lifecycle and usage metering

```python
import asyncio


async def token_flow() -> None:
    created = await server.create_api_token(
        subject_id="customer-001",
        name="primary",
        scopes=["read", "write"],
    )
    token_id = created["token_id"]
    await server.recharge_subject(subject_id="customer-001", amount=100.0)
    await server.record_api_token_usage(
        token_id=token_id,
        amount=1.0,
        operation="inference",
        idempotency_key="req-123",
    )


asyncio.run(token_flow())
```

## 6) Production environment controls

Environment keys supported by server runtime:

- `XWAPI_ENV`
- `XWAPI_ADMIN_TOKEN`
- `XWAPI_ADMIN_PROTECT_READ`
- `XWAPI_ALLOW_INSECURE_ADMIN`
- `XWAPI_API_TOKEN_MIDDLEWARE`

## 7) Testing

Run full layered suite:

```bash
python tests/runner.py
```

Layered runs:

```bash
pytest tests/0.core/
pytest tests/1.unit/
pytest tests/2.integration/
pytest tests/3.advance/
```
