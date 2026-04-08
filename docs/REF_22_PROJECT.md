# Project Reference — xwapi

**Library:** exonware-xwapi  
**Last Updated:** 05-Apr-2026

## Vision

`xwapi` is the control plane for **exposable actions** and entities: **build once, publish anywhere** (HTTP/OpenAPI first; bots/consoles map to the same contracts). It hosts **both** sides — **servers** that publish APIs and **clients/agents** that consume them — with low engine coupling (FastAPI default, Flask alternate) and production primitives (pipeline, token lifecycle, governance middleware).

See [REF_24_ALTERNATIVES.md](REF_24_ALTERNATIVES.md) for ecosystem comparison and engine notes.

## Major completed capabilities

| Capability | Status |
|-----------|--------|
| Server/engine abstraction | Done |
| Middleware stack and operational controls | Done |
| OpenAPI generation and schema integration | Done |
| Engine-agnostic error contract + adapters | Done |
| Outbox + singleton background worker pipeline | Done |
| API token lifecycle/usage/recharge management | Done |
| Provider interfaces (auth/storage/payment) and adapters | Done |
| Scope-aware API token middleware + idempotent metering | Done |
| Production admin guardrails | Done |
| 4-layer testing (`0.core`..`3.advance`) | Done |

## Scope and boundaries

- `xwapi` orchestrates API/runtime concerns.
- `xwapi` does not own full auth/storage/payment implementations; it uses provider contracts and adapters.
- Reuse is explicit across `xwsystem`, `xwaction`, `xwentity`, `xwschema`, and `xwdata`.

## Current priorities

1. Reliability under load and long-run soak coverage.
2. Continued engine/protocol-agnostic hardening.
3. Provider-backed production integrations (beyond in-memory defaults).
4. Documentation alignment with evolving runtime/admin surfaces.

## Remaining roadmap items (known)

- Concrete durable outbox backends (Oracle AQ / DB scheduler adapters).
- Production payment provider adapters.
- Expanded scope-policy mapping strategies from action security metadata.
- Additional audit/event sinks for compliance-heavy deployments.

## Traceability

- Architecture: [REF_13_ARCH.md](REF_13_ARCH.md)
- Alternatives / engines: [REF_24_ALTERNATIVES.md](REF_24_ALTERNATIVES.md)
- API surface: [REF_15_API.md](REF_15_API.md)
- Testing: [REF_51_TEST.md](REF_51_TEST.md)
