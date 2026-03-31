# Competition benchmark: xwlazy vs lazy-import libraries

**Purpose:** Compare xwlazy with other lazy-import / auto-install libraries.

**Date:** November 2025  
**Version:** 1.0.0

---

## Libraries tested

### 1. pipimport
- **PyPI:** `pipimport`
- **GitHub:** https://github.com/chaosct/pipimport
- **Notes:** pip install on import failure

### 2. deferred-import
- **PyPI:** `deferred-import`
- **GitHub:** https://github.com/orsinium-labs/deferred-import
- **Notes:** deferred import helper

### 3. lazy-loader
- **PyPI:** `lazy-loader`
- **GitHub:** https://github.com/scientific-python/lazy-loader
- **Notes:** lazy loading for scientific Python stacks

### 4. lazy-imports
- **PyPI:** `lazy-imports`
- **GitHub:** https://github.com/bachorp/lazy-imports

### 5. lazy_import
- **PyPI:** `lazy-import`
- **GitHub:** https://github.com/mnmelo/lazy_import

### 6. pylazyimports
- **PyPI:** `pylazyimports`
- **GitHub:** https://github.com/hmiladhia/lazyimports

### 7. lazi
- **PyPI:** `lazi`
- **GitHub:** https://github.com/sitbon/lazi

### 8. lazy-imports-lite
- **PyPI:** `lazy-imports-lite`
- **GitHub:** https://github.com/15r10nk/lazy-imports-lite

### 9. xwlazy
- **PyPI:** `xwlazy` / `exonware-xwlazy`
- **GitHub:** eXonware project
- **Notes:** lazy import + optional auto-install, mappings, per-package isolation

---

## Metrics

1. **Import time** - cold and warm
2. **Memory** - peak and average
3. **Package size** - on disk after install
4. **Features** - what each library actually supports

### Scenarios

1. Light - single module
2. Medium - tens of modules
3. Heavy - 100+ modules
4. Nested - deep chains
5. Circular dependencies
6. Missing dependencies / auto-install paths

---

## Usage

### Prerequisites

```bash
pip install -r requirements.txt

# Or:
pip install psutil memory-profiler
```

### Quick start

```bash
python run_benchmark.py
# or
python benchmark_competition.py
```

### One library

```bash
python benchmark_competition.py --library xwlazy
python benchmark_competition.py --library all
```

### One test

```bash
python benchmark_competition.py --test light_load
python benchmark_competition.py --test medium_load
python benchmark_competition.py --test heavy_load
python benchmark_competition.py --test all
```

### Feature comparison

```bash
python feature_comparison.py
```

### CLI

```bash
python benchmark_competition.py --help

Options:
  --library {xwlazy,pipimport,deferred-import,lazy-loader,lazy-imports,lazy_import,pylazyimports,lazi,lazy-imports-lite,all}
  --test {light_load,medium_load,heavy_load,all}
  --skip-uninstall     Skip uninstall (debugging)
```

---

## Results

Written under `output_log/` as `BENCH_YYYYMMDD_HHMM_DESCRIPTION.{json,md}`.

Example:

- `BENCH_20251117_0415_COMPETITION.json`
- `BENCH_20251117_0415_COMPETITION.md`

---

## Features exercised

**Core:** lazy import, deferred load, import hook, module cache, thread safety.

**Advanced:** auto-install on missing imports, keyword detection, per-package isolation, monitoring, leak checks, circular import handling.

---

## Notes

- Libraries are uninstalled before each run for a clean tree.
- Subprocess isolation avoids cross-talk.
- Memory via `psutil`.
- Output naming follows internal doc conventions.

---

## Extending

Edit `benchmark_competition.py`, `test_scenarios.py`, and `library_adapters.py` to add scenarios or adapters.
