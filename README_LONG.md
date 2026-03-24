# xwapi (long version)

**Entity-to-Web-API Conversion Library** — Turn internal functions and entities into production-ready APIs. Connect to external APIs. Same framework, minimal boilerplate.

*This is the long version (full feature tour, architecture, examples). Short overview: [README.md](README.md).*

---

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** connect@exonware.com  
**Version:** 0.0.1.0

---

## What is xwapi?

**xwapi** is a Python framework that turns internal configuration and service functions into production-ready APIs using FastAPI, with minimal boilerplate. xwapi automatically converts xwentity classes into fully-functional FastAPI web APIs with OpenAPI documentation.

### What it does

- **API generation:** Automatically exposes existing project functions as REST endpoints.
- **Entity-to-Web conversion:** Converts xwentity classes into fully-functional FastAPI web APIs with OpenAPI documentation.
- **Bidirectional integration:** Consumes external APIs and normalizes them into callable internal functions.
- **Unified interface:** Same framework for *creating* APIs and *connecting to* other systems' APIs.
- **FastAPI-native:** Leverages FastAPI features (typing, validation, docs, async) without friction.
- **Composable by design:** Encourages modular, reusable API building blocks across services.

### Why it matters

- Eliminates duplicated API layer code.
- Accelerates integration between internal services and third-party systems.
- Keeps business logic independent from transport (API) concerns.

---

## Elevator Pitch

> **xwapi automatically converts xwentity classes and existing Python functions into production-ready REST APIs with zero boilerplate—same framework for building APIs and integrating with external services.**

---

## Architecture Overview

xwapi provides a **unified API framework** with bidirectional capabilities:

```
┌─────────────────────────────────────────────────────────────┐
│                    xwapi Framework                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────┐      ┌──────────────────────┐   │
│  │  Internal Functions  │ ───► │   API Generation     │   │
│  │  (xwaction, config)  │      │   (FastAPI Routes)   │   │
│  └──────────────────────┘      └──────────────────────┘   │
│           ▲                            │                   │
│           │                            ▼                   │
│           │                  ┌──────────────────────┐      │
│           │                  │   REST Endpoints     │      │
│           │                  │   (OpenAPI Docs)     │      │
│           │                  └──────────────────────┘      │
│           │                            │                   │
│  ┌──────────────────────┐      ┌──────────────────────┐  │
│  │  External APIs       │ ◄─── │   API Integration    │  │
│  │  (Third-party)        │      │   (Normalization)    │  │
│  └──────────────────────┘      └──────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         Unified Interface (Same Framework)          │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Key Components:**
1. **Entity-to-Web Conversion:** Automatically converts xwentity classes to FastAPI REST endpoints with OpenAPI docs.
2. **API Generation Layer:** Exposes internal functions and entities as REST endpoints.
3. **Integration Layer:** Consumes external APIs and normalizes them into callable functions.
4. **Unified Interface:** Single framework for both creating and consuming APIs.
5. **FastAPI Foundation:** Native FastAPI features (typing, validation, async, docs).
6. **Composable Architecture:** Modular building blocks for cross-service APIs.

---

## Installation

xwapi supports **3 installation modes**:

```bash
# Lite (Default) - Core dependencies only
pip install exonware-xwapi

# Lazy (Recommended for Development) - Auto-install on demand
pip install exonware-xwapi[lazy]

# Full (Recommended for Production) - All dependencies pre-installed
pip install exonware-xwapi[full]
```

| Mode  | Description |
|-------|--------------|
| **Lite** | Minimal footprint, core dependencies only |
| **Lazy** | Auto-install missing dependencies on demand (development-friendly) |
| **Full** | All dependencies pre-installed (production-ready) |

---

## Quick Start

### Basic Usage

```python
from exonware.xwapi import XWAPI
from exonware.xwentity import XWEntity
from exonware.xwstorage import XWStorage
from exonware.xwauth import XWAuth

class User(XWEntity):
    name: str
    email: str
    age: int

class Product(XWEntity):
    name: str
    price: float
    description: str

storage = XWStorage(backend='embedded')
auth = XWAuth(storage=storage)

api = XWAPI(
    entities=[User, Product],
    storage=storage,
    auth=auth,
    title="My API",
    version="1.0.0"
)

openapi_config = await api.generate_openapi()
app = api.create_fastapi_app()
# Run: uvicorn app:app --host 0.0.0.0 --port 8000
```

### OAuth 2.0 API Example

```python
from exonware.xwapi import XWAPI
from exonware.xwauth import XWUser, XWRole, XWOrganization

api = XWAPI(
    entities=[XWUser, XWRole, XWOrganization],
    storage=storage,
    auth=auth,
    enable_oauth2=True,
    oauth2_config={
        'authorization_url': '/oauth/authorize',
        'token_url': '/oauth/token',
        'userinfo_url': '/oauth/userinfo',
        'providers': ['google', 'github', 'microsoft']
    }
)
# Generated endpoints: POST /oauth/authorize, POST /oauth/token, GET /oauth/userinfo, etc.
```

---

## Key Features

### Automatic API Generation
- **Entity-to-Endpoint Mapping** — Automatic CRUD endpoints from entity classes
- **Action-to-Endpoint Mapping** — Convert xwaction functions to API endpoints
- **Schema-to-Model Mapping** — Generate Pydantic models from xwschema schemas
- **Relationship Handling** — Automatic nested resource endpoints for entity relationships

### OpenAPI Integration
- **Pre-Generation** — Generate OpenAPI JSON config before server starts
- **Complete Spec** — Full OpenAPI 3.1 specification with all endpoints
- **Schema Documentation** — Automatic schema documentation from entity definitions
- **Security Schemes** — OAuth 2.0, API key, and bearer token security schemes

### FastAPI Integration
- **Async Support** — Full async/await support for all endpoints
- **Type Safety** — Automatic type validation from entity schemas
- **Dependency Injection** — Automatic dependency injection for auth, storage, etc.
- **Middleware Support** — Trace, auth, rate limiting, tenant, observability middleware
- **WebSocket Support** — Real-time updates via WebSocket endpoints (when implemented)

### Entity Integration
- **xwentity** — Automatic API generation from XWEntity classes
- **xwaction** — Convert decorated functions to API endpoints
- **xwschema** — Request/response validation via xwschema
- **xwstorage** — Automatic persistence integration
- **xwauth** — User, role, permission management APIs
- **xwquery** — Universal query language for filtering and searching

---

## Entity-to-Endpoint Mapping

- **GET /{entity_name}** — List entities with filtering, pagination, sorting
- **GET /{entity_name}/{id}** — Get single entity by ID
- **POST /{entity_name}** — Create new entity
- **PUT /{entity_name}/{id}** — Update entity
- **PATCH /{entity_name}/{id}** — Partial update
- **DELETE /{entity_name}/{id}** — Delete entity
- **POST /{entity_name}/{id}/{action}** — Execute entity actions

---

## Design Patterns

xwapi implements:

- **Facade Pattern:** XWAPI class — unified interface to API generation subsystems.
- **Strategy Pattern:** OpenAPI generation, serialization, authentication strategies.
- **Factory Pattern:** App factory, middleware factory, endpoint factory.
- **Builder Pattern:** XWAPIConfig, OpenAPI builder.
- **Middleware Pattern:** Chain of responsibility; pluggable middleware.
- **Repository Pattern:** Entity access via xwstorage.

---

## Configuration

```python
api = XWAPI(
    entities=[User, Product],
    storage=XWStorage(backend='postgresql'),
    auth=XWAuth(storage=storage),
    enable_oauth2=True,
    oauth2_config={...},
    actions=[process_order, refund_order],
    title="My API",
    version="1.0.0",
    description="API description",
    servers=[{"url": "https://api.example.com", "description": "Production"}],
    default_security=["oauth2"],
)
```

---

## Testing

xwapi follows eXonware's hierarchical testing (4 layers):

- **0.core** — Core functionality tests (80/20 rule)
- **1.unit** — Unit tests
- **2.integration** — Integration tests
- **3.advance** — Advance tests (v1.0.0+)

```bash
python tests/runner.py
pytest tests/0.core/
pytest tests/1.unit/
pytest tests/2.integration/
```

---

## Innovation: Where does this package fit?

**Tier 3 — Strong engineering (differentiated)**

**xwapi — Entity-to-Multi-Protocol API**

Register an action once → auto-generates REST + GraphQL + gRPC + WebSocket + SMTP endpoints. Lockfile-based instance governance, engine-agnostic middleware.

FastAPI = REST only; this generates **multi-protocol** from one registration. Part of the eXonware story — vertical integration across 20+ packages.

---

## Documentation

- [docs/INDEX.md](docs/INDEX.md) — Documentation index
- [REF_22_PROJECT.md](docs/REF_22_PROJECT.md) — Project status and vision
- [REF_13_ARCH.md](docs/REF_13_ARCH.md) — Architecture
- [REF_15_API.md](docs/REF_15_API.md) — API reference
- [GUIDE_01_USAGE.md](docs/GUIDE_01_USAGE.md) — Usage guide

---

## License

MIT License — see [LICENSE](LICENSE).

---

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** connect@exonware.com
