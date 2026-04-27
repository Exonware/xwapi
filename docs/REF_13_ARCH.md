# Architecture Reference — xwapi

**Library:** exonware-xwapi  
**Last Updated:** 05-Apr-2026

## Overview

`xwapi` orchestrates **exposable actions** and entities for eXonware: **build once, publish anywhere** (HTTP/OpenAPI today; bots/consoles follow the same action contracts). It is intentionally **bidirectional** — servers **publish**, `XWApiAgent` and client engines **consume** remote APIs.

It provides:

- engine-agnostic app/server abstractions (**FastAPI** default ASGI/OpenAPI; **Flask** WSGI engine in the registry)
- route and action registration via `xwaction`
- entity-driven HTTP surfaces (`xwentity`)
- transport-neutral error model with framework adapters
- middleware pipeline (trace/tenant/rate-limit/auth/observability/pause/admin/API-token)
- operational admin endpoints
- outbox + singleton worker action pipeline
- API token lifecycle and usage metering with provider contracts

## Architectural layers

1. **Facade / publisher**
   - `XWAPI`
   - OpenAPI generation and app creation (`engine=` selects FastAPI, Flask, …)
2. **Client / consumer**
   - `XWApiAgent`, client engine registry
3. **Server/runtime layer**
   - `XWApiServer`
   - action registration, operational lifecycle, status/health
4. **Middleware layer**
   - request guards, observability, auth, pause, API token metering
5. **Pipeline layer**
   - `AOutboxStore`, `InMemoryOutboxStore`
   - `BackgroundWorker` (singleton-per-process)
   - `ActionPipelineManager`
6. **Token/billing layer**
   - `APITokenManager`
   - provider contracts: `IAuthProvider`, `IStorageProvider`, `IPaymentProvider`
7. **Provider adapters**
   - local/in-memory adapters and library-backed adapters (`xwauth`, `xwstorage`)

## Engine and protocol agnosticism

- **HTTP:** `fastapi` is the default engine (OpenAPI, async ASGI); `flask` is registered for WSGI. Select at `create_app` / `XWApiServer` construction; actions and errors stay engine-agnostic where possible.
- Core errors are represented as `XWAPIError` variants.
- Mapping to HTTP responses is handled by adapters (`xwapi_error_to_http_parts`, Starlette response adapter).
- Middleware and request/response handling avoid unnecessary engine-specific coupling where possible.

## Outbox + worker model

- API thread enqueues jobs through outbox abstraction.
- Single worker instance claims and executes jobs.
- Retries, leasing, dead-letter transitions, and safe stop behavior are included in runtime behavior and tests.

## Token management architecture

- Token identity and metadata storage are abstracted through providers.
- Usage metering supports idempotency keys to avoid duplicate debit.
- Scope checks are optional and route-driven in API token middleware.
- Recharge/balance capabilities are delegated to payment provider interface.

## Dependencies and reuse

`xwapi` intentionally reuses:

- `xwsystem` (logging/serialization/core utils)
- `xwaction` (registration/execution contracts)
- `xwentity` (entity model surface)
- `xwschema` (schema and validation integration points)
- `xwdata` (data-format/serialization integration points)

## Notable runtime controls (env)

- `XWAPI_ENV`
- `XWAPI_ADMIN_TOKEN`
- `XWAPI_ADMIN_PROTECT_READ`
- `XWAPI_ALLOW_INSECURE_ADMIN`
- `XWAPI_API_TOKEN_MIDDLEWARE`
