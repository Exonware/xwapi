# Server engine registry — xwapi

**Last Updated:** 05-Apr-2026

Engines are **lazy-registered** when `api_server_engine_registry` is first used. Each engine is optional except the default HTTP stack (FastAPI) when dependencies are present.

## Built-in (already registered before optional set)

| Engine name | Protocol / stack | Notes |
|-------------|------------------|--------|
| `fastapi` | HTTP REST / ASGI | Default engine; OpenAPI, middleware, `XWAction` FastAPI engine. |
| `flask` | HTTP REST / WSGI | `FlaskActionEngine` integration. |
| `grpc` | gRPC | Requires `grpcio`. |
| `graphql` | HTTP GraphQL | Strawberry + FastAPI. |
| `websocket` | WebSocket | FastAPI-based. |
| `smtp` | SMTP | Email receive. |
| `pop3` | POP3 | Email. |
| `imap` | IMAP | Email. |

## Optional HTTP frameworks (`optional_http_engines.py`)

Install the framework, or install all optional HTTP adapters at once:

`pip install exonware-xwapi[engines-http]`

If a dependency is missing, the registry skips that engine (debug log only).

| Engine name | Package | Binding strategy |
|-------------|---------|-------------------|
| `starlette` | `starlette` | ASGI routes + `NativeActionEngine` bridge. |
| `quart` | `quart` | Async Flask-like ASGI; uvicorn. |
| `sanic` | `sanic` | Sanic `app.run` or compatible runner. |
| `aiohttp` | `aiohttp` | `web.Application` + `web.run_app`. |
| `blacksheep` | `blacksheep` | ASGI; uvicorn. |
| `litestar` | `litestar` | Catch-all dispatch table + `HTTPException`. |
| `django` | `django` | Minimal `ROOT_URLCONF` on this module (**one `create_app` per process** if settings unconfigured). |
| `mangum` | `mangum` | Wraps inner FastAPI app for **AWS Lambda**; `start_server` is a no-op. |

## Client agent engines

See `exonware.xwapi.client.engines` — currently centered on `native` agent discovery; not the same registry as server engines.

## Traceability

- Alternatives / competitors: [REF_24_ALTERNATIVES.md](REF_24_ALTERNATIVES.md)
- Architecture: [REF_13_ARCH.md](REF_13_ARCH.md)
