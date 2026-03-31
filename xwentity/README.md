# xwentity

**Unified entity layer.** Ties schema (xwschema), actions (xwaction), and data (xwdata) together with metadata, caching, state, and XWNode. Used by xwmodels, xwbase, and the rest of the eXonware stack. Details live in `docs/`.

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com  

[![Status](https://img.shields.io/badge/status-beta-blue.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Install

```bash
pip install exonware-xwentity
pip install exonware-xwentity[lazy]
# Full stack used by xwentity flows
pip install exonware-xwentity[full]
```

`[full]` pulls the full variants of: `xwsystem`, `xwaction`, `xwdata`, `xwquery`, `xwschema`, and `xwnode`.

---

## Quick start

```python
from exonware.xwentity import XWEntity
from exonware.xwschema import XWSchema

schema = XWSchema({"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}})
entity = XWEntity(schema=schema, data={"name": "Alice", "age": 30})
print(entity.data["name"])
```

See [docs/](docs/) for metadata, state, and REF_* files.

---

## What you get

| Area | What's in it |
|------|----------------|
| **Entity** | One class for schema, actions, data, metadata, caching. |
| **Integration** | xwschema, xwaction, xwdata, XWNode. |
| **Lifecycle** | State and property discovery. |

## Core model (explicit roles)

- **XWEntity** (`entity.py`) composes `XWSchema` + `XWAction` + `XWData`: validation contract, entity-scoped behavior, and multi-format data payloads.
- **XWCollection** (`collection.py`) is a logical, storage-agnostic collection of entities of the same type, with collection-level actions (search/bulk operations).
- **XWGroup** (`group.py`) manages multiple collections and supports nested parent/child groups, forming a tree structure for organization.
- **Shared foundation:** `XWCollection` and `XWGroup` directly extend `XWObject` (`xwsystem`), and `XWEntity` extends `AEntity` which extends `XWObject`, so all core entity types inherit the same lightweight identity/object base.

---

## Docs and tests

- **Start:** [docs/INDEX.md](docs/INDEX.md) or [docs/](docs/).
- **Tests:** From repo root, follow the layout in this package (pytest or project runner).

---

## License and links

MIT - see [LICENSE](LICENSE). **Homepage:** https://exonware.com · **Repository:** https://github.com/exonware/xwentity  


## Async Support

<!-- async-support:start -->
- xwentity includes asynchronous execution paths in production code.
- Source validation: 4 async def definitions and 1 await usages under src/.
- Use async APIs for I/O-heavy or concurrent workloads to improve throughput and responsiveness.
<!-- async-support:end -->
Version: 0.6.0.5 | Updated: 31-Mar-2026

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
