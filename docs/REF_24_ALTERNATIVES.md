# Alternatives, engines, and positioning — xwapi

**Last Updated:** 05-Apr-2026

## How xwapi fits

`xwapi` is **entity- and action-centric**: you define **exposable actions** (via `xwaction`) and domain **entities**; the library helps you **publish** them over transports (HTTP/OpenAPI first) and **consume** them from the other side with **client/agent** building blocks (`XWApiAgent`, client engines).

**Tagline:** *Build once, publish anywhere* — one action/entity surface; multiple ways to expose it (REST/OpenAPI today; bots, consoles, and other adapters align with the same contracts). *Publish everywhere* means the same logical API can target different HTTP engines or future protocol engines without rewriting business logic.

## Bidirectional design

| Direction | Role in xwapi |
|-----------|----------------|
| **Server / publisher** | `XWAPI`, `XWApiServer`, server engines, middleware, OpenAPI |
| **Client / consumer** | `XWApiAgent`, OAuth/session helpers, discovery of `XWAction` methods |

Peers in the wider ecosystem usually pick **either** a server framework **or** an HTTP client — xwapi is intentionally **both** for Exonware-shaped services.

## HTTP engines: FastAPI and Flask

- **FastAPI** is the default engine: OpenAPI, async, Starlette ASGI, dependency injection, and the ecosystem you already know stay available; `exonware.xwapi.http` centralizes common FastAPI imports so sibling packages depend on `xwapi`, not scattered `fastapi` imports.
- **Flask** is a first-class **alternate server engine** in the registry. Choose `engine="flask"` when creating an app or constructing `XWApiServer` so you can align with WSGI deployments, legacy stacks, or A/B experimentation **without** abandoning the same action registration and error contracts (feature parity varies by engine; HTTP remains the primary interchange).

“Switch on the fly” in practice means **selecting the engine at app/server construction** (and consistent use of engine-agnostic helpers). Runtime hot-swapping the framework on a live process is not a goal; **configuration-time** switching is.

## Comparable and adjacent libraries

These are useful references, not drop-in replacements for the full xwapi stack.

| Library / stack | Overlap with xwapi | Difference |
|-----------------|-------------------|------------|
| **FastAPI** (+ **Starlette**) | ASGI apps, OpenAPI, typing | No built-in Exonware action/entity pipeline, agents, or shared `http` facade for monorepo libs |
| **Flask** (+ **Flask-Smorest** etc.) | WSGI, optional OpenAPI | Manual composition; no native `xwaction` wiring |
| **Django REST framework** | CRUD-ish REST, browsable API | Django-centric; different action/entity model |
| **Litestar** | Modern ASGI, OpenAPI, plugins | Different integration story; no xwaction/xwauth/xwstorage contracts |
| **SQLModel** + FastAPI | Typed models → API shapes | DB-first; not action-registry + multi-engine server |
| **Connexion** | OpenAPI-first HTTP | Spec-driven vs code-first actions |
| **Strawberry / Ariadne** | GraphQL servers | GraphQL vs OpenAPI REST default |
| **gRPC** (grpcio, **Connect**) | RPC, codegen, binary protocols | Different IDL and ops model; xwapi exposes gRPC-oriented engine hooks as part of multi-protocol direction |

## When xwapi is the stronger default

- You want **one** place for **server + client** patterns around **exposable actions**.
- You want **OpenAPI** merged from actions plus optional **entity CRUD** scaffolding.
- You want **production** middleware, admin, pipeline, and token surfaces shared across services.
- You want to **standardize on FastAPI** while keeping **Flask** (or other registered engines) as a **switchable** deployment option.

## Traceability

- Architecture: [REF_13_ARCH.md](REF_13_ARCH.md)
- Project vision: [REF_22_PROJECT.md](REF_22_PROJECT.md)
- Public API: [REF_15_API.md](REF_15_API.md)
