# xwapi

**Entity-to-Web-API.** Turn xwentity classes and internal functions into production-ready REST APIs (FastAPI, OpenAPI); connect to external APIs; same framework, minimal boilerplate. Per project docs.

*Full feature tour, architecture, and examples: [README_LONG.md](README_LONG.md).*

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com  
**Version:** See [version.py](src/exonware/xwapi/version.py) or PyPI. · **Updated:** See [version.py](src/exonware/xwapi/version.py) (`__date__`)

[![Status](https://img.shields.io/badge/status-beta-blue.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Install

| Install | When to use |
|---------|-------------|
| `pip install exonware-xwapi` | **Lite** — core only |
| `pip install exonware-xwapi[lazy]` | **Lazy** — auto-install on first import |
| `pip install exonware-xwapi[full]` | **Full** — production, all deps |

---

## Quick start

```python
from exonware.xwapi import XWAPI
from exonware.xwentity import XWEntity
from exonware.xwstorage import XWStorage

class User(XWEntity):
    name: str
    email: str
    age: int

storage = XWStorage(backend='embedded')
api = XWAPI(entities=[User], storage=storage, title="My API", version="1.0.0")
openapi_config = await api.generate_openapi()
app = api.create_fastapi_app()
# Run: uvicorn app:app --host 0.0.0.0 --port 8000
```

See [docs/](docs/) for OAuth2, actions, middleware, and REF_*.

---

## What you get

| Area | What's in it |
|------|----------------|
| **API generation** | Entity → CRUD endpoints; xwaction → endpoints; OpenAPI 3.1. |
| **Integration** | xwentity, xwauth, xwstorage, xwschema, xwquery; FastAPI-native. |
| **Security** | OAuth 2.0, API key, bearer; rate limit, tenant, observability middleware. |
| **Multi-protocol** | REST; GraphQL/gRPC/WebSocket when implemented. |

---

## Docs and tests

- **Start:** [docs/INDEX.md](docs/INDEX.md) or [docs/](docs/).
- **Tests:** `python tests/runner.py` or pytest per project layout (0.core, 1.unit, 2.integration, 3.advance).

---

## License and links

MIT — see [LICENSE](LICENSE). **Homepage:** https://exonware.com · **Repository:** https://github.com/exonware/xwapi  

Contributing → CONTRIBUTING.md · Security → SECURITY.md (when present).

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
