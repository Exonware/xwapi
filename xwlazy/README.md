# xwlazy

**Fewer "ModuleNotFoundError" detours.** Optional auto-install and deferred imports inside a package scope you control, with import-name → PyPI-name mappings (`bs4` → `beautifulsoup4`, etc.), PEP 668 awareness, and optional audit outputs.

[![Status](https://img.shields.io/badge/status-beta-blue.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Automation](https://img.shields.io/badge/automation-missing%20imports%20handled-6f42c1.svg)](https://github.com/exonware/xwlazy)

For Python 3.8+, xwlazy can install missing dependencies on first real use and defer heavy imports so startup stays lighter. It is built for library authors who want one-line opt-in per package, not for replacing pinned production installs.

---

## Quick start

### 1. Install

```bash
pip install exonware-xwlazy
# or
pip install xwlazy
```

`xwlazy` itself does not use `[lazy]` / `[full]` extras; install it directly (commands above) and use `[lazy]` / `[full]` on stack packages that depend on it.

- On a **system** interpreter, PEP 668 is respected: no silent installs into externally managed environments.
- Inside a **venv**, installs use that environment's `pip`.

### 2. Enable for your package (one line in `__init__.py`)

```python
try:
    from exonware.xwlazy import config_package_lazy_install_enabled
    config_package_lazy_install_enabled(__package__ or "yourorg.yourlib", enabled=True, mode="smart")
except ImportError:
    # xwlazy not installed -> normal behavior (no lazy hook)
    pass
```

Normal `import` statements stay as they are. Inside the enabled scope you get lazy install and (when policy allows) lazy loading.

### 3. Zero-code opt-in (optional)

```toml
[project]
keywords = ["xwlazy-enabled"]
```

After `pip install -e .`, lazy mode can turn on from project metadata.

---

## What you get

| Capability | What it does |
|-----------|--------------|
| **Lazy install** | First touch on a missing module can trigger `pip install` for the mapped package. |
| **Lazy loading** | Selected imports wait until use when your policy enables it. |
| **Per-package scope** | Each package opts in; others are unchanged. |
| **Keyword opt-in** | `xwlazy-enabled` in `pyproject.toml` enables without code. |
| **Two-stage behavior** | Import time: log and defer; use time: install then continue. |
| **Policy / audit** | Allow/deny lists, lockfile, SBOM hooks, PEP 668 checks. |
| **Persist to project** | Successful installs can append `requirements.txt` / `pyproject.toml`. Use `XWLAZY_PERSIST_EXTRAS` and `XWLAZY_NO_PERSIST` to control. |

Implementation: `src/exonware/xwlazy.py`; `src/xwlazy.py` re-exports. `src/_old/` is reference-only and is not shipped as the runtime entry.

---

## Built-in mappings

Curated table: `src/exonware/xwlazy_external_libs.toml` (data/ML, DL, viz, web, formats). Override or extend in your tree if you need custom rows.

---

## Benchmarks vs other lazy-import tools

We run xwlazy next to pipimport, deferred-import, lazy-loader, lazy-imports, pylazyimports, lazi, lazy-imports-lite, etc. See [benchmarks/20260209-benchmark competition/README.md](benchmarks/20260209-benchmark%20competition/README.md).

**Latest campaign (Feb 2026, representative numbers):**

- **medium_load:** ~4.06 ms (xwlazy) vs ~4.54 ms next best in that run.
- **heavy / enterprise:** ~14 ms heavy, ~41 ms enterprise with auto-install, isolation, and audit features enabled.

Many competitors only defer imports, or assume `import name == pip name`. xwlazy adds mapping-aware installs, optional lockfile/SBOM, and per-package isolation. See the feature matrix in the benchmark README.

**Common footgun without mapping:**

| You write | Pip package | Without mapping |
|-----------|-------------|-----------------|
| `import bs4` | `beautifulsoup4` | `pip install bs4` often wrong |
| `import yaml` | `PyYAML` | `pip install yaml` fails |
| `import sklearn` | `scikit-learn` | `pip install sklearn` fails |
| `import cv2` | `opencv-python` | `pip install cv2` fails |
| `import PIL` | `Pillow` | `pip install PIL` fails |
| `import attr` | `attrs` | wrong package |

---

## Modes and strategies

| Strategy | Behavior | Typical use |
|----------|----------|-------------|
| `smart` | Uses manifests + mappings | Default |
| `pip` | Plain `pip` under the hook | Explicit pip semantics |
| `wheel` | Prefer wheels | Wheel-rich envs |
| `cached` | Reuse resolved candidates | Repeat runs |

No activation → normal imports, no lazy behavior.

```python
from xwlazy import auto_enable_lazy

auto_enable_lazy("xwsystem", mode="smart")
```

---

## Security and production

- **Deny list** in `xwlazy_external_libs.toml` (`[deny_list]`).
- **Lockfile (opt-in):** with auditing, `~/.xwlazy/xwlazy.lock.toml`.
- **Persist:** writes to project `requirements.txt` / `pyproject.toml` unless disabled (`XWLAZY_NO_PERSIST=1`, `XWLAZY_PERSIST_EXTRAS=...`).
- **SBOM (opt-in):** `generate_sbom()` → `~/.xwlazy/xwlazy_sbom.toml` when auditing is on.
- **Async I/O (default):** background worker for persist/lockfile/audit. `XWLAZY_ASYNC_IO=0` forces sync.
- **PEP 668:** no installs into externally managed interpreters; use a venv.

Set `XWLAZY_AUDIT_ENABLED=1` before import if you want lockfile/SBOM writes. Auditing is **off** by default.

Production pattern: pin deps, pre-install in images, keep lazy as a safety net if you accept the trade-offs.

---

## Optional mixins (off by default)

Per-call wrapper API, AST rewrite, and type-stub helpers exist behind env flags. **We recommend leaving them off**; they add complexity and are easy to miscompose with the core hook.

| Feature | Env var |
|--------|---------|
| Per-call wrapper | `XWLAZY_PER_CALL_API=1` |
| AST lazy transform | `XWLAZY_AST_LAZY=1` |
| Type-stub tooling | `XWLAZY_TYPING_TOOLS=1` |

Prefer `config_package_lazy_install_enabled`, `auto_enable_lazy`, or `attach` for normal work.

---

## Troubleshooting

```python
from xwlazy import get_all_stats

stats = get_all_stats()
```

- **Nothing installs:** `get_lazy_install_stats("your-package")` - check `enabled` and `mode`, and allow lists.
- **First import slow:** first install cost; pre-install with `[full]` or warm caches.

---

## Docs and tests

Aligned with [docs/GUIDE_01_USAGE.md](docs/GUIDE_01_USAGE.md) and monorepo [GUIDE_63_README](../.docs/guides/GUIDE_63_README.md).

- [docs/INDEX.md](docs/INDEX.md)
- [docs/REF_01_REQ.md](docs/REF_01_REQ.md), [docs/REF_22_PROJECT.md](docs/REF_22_PROJECT.md)
- [docs/REF_15_API.md](docs/REF_15_API.md), [docs/REF_14_DX.md](docs/REF_14_DX.md), [docs/REF_13_ARCH.md](docs/REF_13_ARCH.md)
- [docs/REF_54_BENCH.md](docs/REF_54_BENCH.md), [docs/REF_51_TEST.md](docs/REF_51_TEST.md), [docs/logs/benchmarks/](docs/logs/benchmarks/)

```bash
python tests/runner.py
# or per layer: python tests/0.core/runner.py, python tests/1.unit/runner.py
```

---

## Ecosystem note

xwlazy combines lazy imports, on-demand install, mapping table, optional lockfile/SBOM, LRU + disk caching, manifests, and deny lists. That is a different shape than "defer import only" libraries.

---

## License and links

MIT - see [LICENSE](LICENSE).

- **Homepage:** https://exonware.com  
- **Repository:** https://github.com/exonware/xwlazy  
- **Contact:** connect@exonware.com · eXonware Backend Team  

## Async Support

<!-- async-support:start -->
- xwlazy is primarily synchronous in its current implementation.
- Source validation: 0 async def definitions and 0 await usages under src/.
- This module still composes with async-capable xw libraries at integration boundaries when needed.
<!-- async-support:end -->
Version: 1.0.1.67 | Updated: 31-Mar-2026

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
