# xwapi — Usage Guide

**Last Updated:** 05-Apr-2026

**Build once, publish anywhere:** define *exposable actions* (`xwaction`) and entities, then publish over HTTP. Default engine is **FastAPI**; use `engine="flask"` on `create_app` / `XWApiServer` for WSGI. For the **consumer** side, use `XWApiAgent` (see §4). Comparables and engine notes: [REF_24_ALTERNATIVES.md](REF_24_ALTERNATIVES.md).

This guide covers facade usage, server usage, client agents, action registration, pipeline, and API tokens.

## 1) Facade-first usage (`XWAPI`)

Fast path from entity + action lists to an HTTP app.

```python
from exonware.xwapi import XWAPI
from exonware.xwentity import XWEntity


class User(XWEntity):
    name: str
    email: str


api = XWAPI(entities=[User], title="Users API", version="1.0.0")
app = api.create_app(engine="fastapi")
# WSGI / Flask stack: api.create_app(engine="flask")
```

## 2) Server-first usage (`XWApiServer`)

Use when you need runtime controls, pipeline orchestration, and admin endpoints. Same `engine=` switch as the facade.

```python
from exonware.xwapi import XWApiServer

server = XWApiServer(engine="fastapi")
app = server.app
```

## 3) Register actions

`xwapi` integrates with `xwaction` so exposable action definitions become HTTP endpoints (engine-specific binding).

```python
from exonware.xwaction import XWAction


@XWAction(operationId="ping", profile="endpoint")
def ping() -> dict[str, str]:
    return {"status": "ok"}


server.register_action(ping, path="/ping", method="GET")
```

## 4) Client usage (`XWApiAgent`)

Mirror of the server: agents discover `XWAction` methods and integrate `xwauth` flows when **calling** APIs.

```python
from exonware.xwapi import XWApiAgent
from exonware.xwaction import XWAction


class DemoAgent(XWApiAgent):
    @XWAction(operationId="local_echo", profile="endpoint")
    def echo(self, text: str = "hi") -> dict[str, str]:
        return {"text": text}


agent = DemoAgent()
# Register onto a server or use client patterns against remote exposable actions.
```

## 5) Pipeline (Outbox + singleton worker)

```python
def job_handler(payload: dict[str, str]) -> dict[str, bool]:
    return {"ok": True}


server.register_pipeline_handler("jobs.email", job_handler)
server.start_pipeline_worker()
server.enqueue_pipeline_job("jobs.email", {"to": "user@example.com"})
```

## 6) API token lifecycle and usage metering

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

## 7) Production environment controls

Environment keys supported by server runtime:

- `XWAPI_ENV`
- `XWAPI_ADMIN_TOKEN`
- `XWAPI_ADMIN_PROTECT_READ`
- `XWAPI_ALLOW_INSECURE_ADMIN`
- `XWAPI_API_TOKEN_MIDDLEWARE`

## 8) Testing

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
