# xwjson

**Binary JSON plus local data-engine behavior for real workloads.** `.xwjson` is powered by the `xwsystem` parser engine for high-throughput reads/writes, lazy and path-scoped access, schema-aware validation, encrypted payload support, and **atomic-first ACID-style transaction flows with WAL**. In this repo, performance/stress suites include large-file scenarios validated up to 20GB, stdlib JSON comparisons, and conversion stress runs.

*Longer tour, examples, and troubleshooting: [README_LONG.md](README_LONG.md).*

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com  

[![Status](https://img.shields.io/badge/status-beta-blue.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Install

```bash
pip install exonware-xwjson
pip install exonware-xwjson[lazy]
pip install exonware-xwjson[full]
```

---

## Quick start

```python
from exonware.xwjson import XWJSONSerializer

serializer = XWJSONSerializer()
# Async (recommended)
data = await serializer.load_file_async("data.xwjson")
await serializer.save_file_async(data, "output.xwjson")
# Sync
data = serializer.load_file("data.xwjson")
serializer.save_file(data, "output.xwjson")
```

See [docs/](docs/) for REF_*, guides, and examples.

---

## What you get

| Area | What's in it |
|------|----------------|
| **Binary engine** | `xwsystem` parser-driven binary encoding with fast serialization paths and metadata-aware payloads. |
| **Lazy + path I/O** | Parse on access, stream/paging support, and path-level operations without full materialization. |
| **References** | `$ref`, `@href`, `*anchor` preserved and resolved. |
| **Security** | Password-based encrypted file support and encrypted payload detection helpers. |
| **Atomic operations** | Atomic read/write/update/delete paths for safe state transitions under concurrent workloads. |
| **Transactions** | ACID-style flows with WAL-backed transaction components, rollback support, and dependency-aware batch work. |
| **Index/cache acceleration** | xwnode strategy integrations for faster lookups and cache-assisted repeated access. |
| **Integration** | xwnode, xwschema, xwquery, xwdata, xwstorage; format metadata carried through. |

---

## Atomic operations - core strength

- `xwjson` is designed around atomic state changes, not best-effort updates.
- Single-file and path-level operations are built to commit safely or fail safely.
- Transaction flows combine atomic steps with WAL-backed durability mechanics.
- For local data-engine workloads, this is a headline capability: **atomic operations are first-class, not optional**.

---

## Performance and benchmark posture

- Built-in performance guidance and benchmark methodology: `docs/_archive/GUIDE_PERFORMANCE.md`.
- Repo test artifacts include conversion/performance stress suites and large-file scenarios in `tests/2.integration/scenarios/`.
- File size note: no hard file-size cap is enforced by `xwjson`; largest documented test scenario in this repo is 20GB.
- Test summaries in `tests/FINAL_TEST_SUMMARY.md` and `tests/TEST_SUMMARY.md` document speed-oriented targets (including stdlib JSON comparison paths and cache/index speedups).
- Positioning: `xwjson` can act like a **database-like local data layer** for many workloads; external database claims should stay workload-specific and benchmark-backed.

---

## Docs and tests

- **Start:** [docs/INDEX.md](docs/INDEX.md) or [docs/](docs/).
- **Guides:** Basic/advanced usage, performance, conversion, schema validation under `docs/` when present.
- **Tests:** From repo root, follow this package's runner or pytest layout.

---

## License and links

MIT - see [LICENSE](LICENSE). **Homepage:** https://exonware.com · **Repository:** https://github.com/exonware/xwjson  

## Async Support

<!-- async-support:start -->
- xwjson includes asynchronous execution paths in production code.
- Source validation: 46 async def definitions and 50 await usages under src/.
- Use async APIs for I/O-heavy or concurrent workloads to improve throughput and responsiveness.
<!-- async-support:end -->
Version: 0.9.0.11 | Updated: 31-Mar-2026

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
