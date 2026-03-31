# xwapi — API Reference

**Last Updated:** 31-Mar-2026

This reference summarizes the current public surface and operational feature set.

## Primary exports

From `exonware.xwapi`:

- Facade/runtime:
  - `XWAPI`
  - `XWApiServer`
- Pipeline:
  - `ActionPipelineManager`
  - `BackgroundWorker`
  - `InMemoryOutboxStore`
- Token management:
  - `APITokenManager`
- Providers:
  - `LocalAuthProvider`
  - `XWAuthLibraryProvider`
  - `InMemoryStorageProvider`
  - `XWStorageProvider`
  - `InMemoryPaymentProvider`
- Provider interfaces:
  - `IAuthProvider`
  - `IStorageProvider`
  - `IPaymentProvider`
- Error/HTTP helpers:
  - `XWAPIError` and typed variants
  - `xwapi_error_to_http_parts`
  - `http_status_to_xwapi_error`
  - `create_error_response`
  - `get_error_headers`

## `XWAPI` facade methods

- `generate_openapi()`
- `create_app(engine="fastapi")`
- `start(...)`
- `stop()`
- `restart()`

## `XWApiServer` operational methods (selected)

- `register_action(...)`
- `register_actions(...)`
- `status()`
- `health()`
- `pause_endpoint(...)`
- `resume_endpoint(...)`

### Pipeline methods

- `register_pipeline_handler(job_type, handler)`
- `enqueue_pipeline_job(job_type, payload, ...)`
- `enqueue_action_job(action_name, payload, ...)`
- `start_pipeline_worker()`
- `stop_pipeline_worker()`

### Token methods

- `create_api_token(...)`
- `record_api_token_usage(...)`
- `recharge_subject(...)`
- `get_subject_balance(subject_id)`

## Admin operations (action endpoints)

Server operations include:

- `server_status`
- `server_health`
- `server_health_root`
- `server_pipeline`
- `server_pause`
- `server_resume`

Token operations include:

- `server_tokens_create`
- `server_tokens_list`
- `server_tokens_revoke`
- `server_tokens_usage_record`
- `server_tokens_usage_list`
- `server_tokens_recharge`
- `server_tokens_balance`

## API token middleware behavior

When enabled:

- validates bearer API tokens
- supports route scope enforcement
- supports deny-unmapped scope policy
- meters successful requests and honors `Idempotency-Key`
- bypasses/permits configured exempt/admin paths

## Environment controls

- `XWAPI_ENV`
- `XWAPI_ADMIN_TOKEN`
- `XWAPI_ADMIN_PROTECT_READ`
- `XWAPI_ALLOW_INSECURE_ADMIN`
- `XWAPI_API_TOKEN_MIDDLEWARE`
