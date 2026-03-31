# Architecture Reference — xwapi

**Library:** exonware-xwapi  
**Last Updated:** 31-Mar-2026

## Overview

`xwapi` is the API orchestration layer in eXonware. It provides:

- engine-agnostic app/server abstractions
- route and action registration via `xwaction`
- entity-driven endpoint generation (`xwentity`)
- transport-neutral error model with framework adapters
- middleware pipeline (trace/tenant/rate-limit/auth/observability/pause/admin/API-token)
- operational admin endpoints
- outbox + singleton worker action pipeline
- API token lifecycle and usage metering with provider contracts

## Architectural layers

1. **Facade/API layer**
   - `XWAPI`
   - OpenAPI generation and app creation
2. **Server/runtime layer**
   - `XWApiServer`
   - action registration, operational lifecycle, status/health
3. **Middleware layer**
   - request guards, observability, auth, pause, API token metering
4. **Pipeline layer**
   - `AOutboxStore`, `InMemoryOutboxStore`
   - `BackgroundWorker` (singleton-per-process)
   - `ActionPipelineManager`
5. **Token/billing layer**
   - `APITokenManager`
   - provider contracts: `IAuthProvider`, `IStorageProvider`, `IPaymentProvider`
6. **Provider adapters**
   - local/in-memory adapters and library-backed adapters (`xwauth`, `xwstorage`)

## Engine and protocol agnosticism

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
