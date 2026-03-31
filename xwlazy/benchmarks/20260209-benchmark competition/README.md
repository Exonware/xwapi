# 20260209 - Benchmark: xwlazy vs lazy-import libraries

**Campaign:** xwlazy vs competing lazy-import libraries  
**Date:** 09-Feb-2026 (updated 10-Feb-2026)  
**Project:** exonware/xwlazy  
**Guide:** [GUIDE_54_BENCH.md](../../../.docs/guides/GUIDE_54_BENCH.md)

---

## Goal

Compare **xwlazy** against common lazy-import libraries on realistic import workloads, and record how xwlazy load modes and install modes behave.

---

## Description

This campaign reuses the harness under `benchmarks/20260209-benchmark competition/scripts/competition_tests/` to benchmark:

- **Libraries:** `xwlazy`, `pipimport`, `deferred-import`, `lazy-loader`, `lazy-imports`, `lazy_import`, `pylazyimports`, `lazi`, `lazy-imports-lite`
- **Scenarios:** light / medium / heavy / enterprise import loads
- **xwlazy modes:** LITE, SMART, CLEAN, PRELOAD, BACKGROUND, AUTO, FULL, and full-feature combinations
- **Install behavior:** many tools assume `import_name == pip_name` (e.g. `pipimport`) or need manual overrides (e.g. `deferred-import(package='attrs')` for `import attr`). **xwlazy** uses `xwlazy_external_libs.toml` (plus project overrides) so `bs4` → `beautifulsoup4`, `yaml` → `PyYAML`, etc. work without per-import boilerplate.
- **Optional mixins:** per-call wrapper, AST lazy, type-stub helpers are env-gated and **off** by default; see the root [README](../../README.md) and the matrix below.

It records import time (cold/warm), memory, and which xwlazy mode wins per load level.

Results land in BENCH_* reports under this campaign's `benchmarks/` folder and can be checked against [REF_54_BENCH](../../docs/REF_54_BENCH.md) SLAs if defined.

---

## Metrics

- **Import time:** ms per scenario (min / mean / median from the harness)
- **Throughput:** derived ops/sec where applicable
- **Memory:** peak / average per run
- **Wins:** first / second / third per category

---

## Library feature comparison (vs xwlazy)

Quick matrix (✅ = supported / built-in, **✅ (opt)** = optional in xwlazy, off by default; blank = not a focus for that library):

| Library | Auto-install | Lazy import | Global import hook | Per-call wrapper API | AST rewrite | Mapping-aware install | Pyproject / build integration | Import tracing / debug | Type-stub / internal API tooling | Per-package isolation | Lockfile / SBOM | PEP 668-aware | Ignore-list cache | Tiny one-liner API |
|--------|-------------|------------|--------------------|----------------------|------------|-----------------------|------------------------------|------------------------|-----------------------------------|----------------------|-----------------|--------------|-------------------|--------------------|
| **xwlazy** | ✅ | ✅ | ✅ | ✅ (opt) | ✅ (opt) | ✅ | ✅ | ✅ | ✅ (opt) | ✅ | ✅ | ✅ | ✅ | ✅ |
| **pipimport** | ✅ |  | ✅ |  |  |  |  |  |  |  |  |  | ✅ | ✅ |
| **deferred-import** | ✅ | ✅ |  | ✅ |  |  |  |  |  |  |  |  |  | ✅ |
| **lazy-loader** |  | ✅ |  |  |  |  |  |  | ✅ |  |  |  |  |  |
| **lazy-imports** |  | ✅ | ✅ |  |  |  |  |  |  |  |  |  |  |  |
| **lazy_import** |  | ✅ |  | ✅ |  |  |  |  |  |  |  |  |  |  |
| **pylazyimports** |  | ✅ |  | ✅ |  |  | ✅ |  |  |  |  |  |  |  |
| **lazi** |  | ✅ | ✅ |  |  |  |  | ✅ |  |  |  |  |  |  |
| **lazy-imports-lite** |  | ✅ |  |  | ✅ |  | ✅ |  |  |  |  |  |  |  |

**xwlazy (opt):** Per-call wrapper, AST lazy, and type-stub tooling via `XWLAZY_PER_CALL_API=1`, `XWLAZY_AST_LAZY=1`, `XWLAZY_TYPING_TOOLS=1`. Leave them off unless you have a specific need; prefer `hook` / `auto_enable_lazy` / `attach`.

This run compares xwlazy's install modes, mapping table, isolation, and audit hooks against libraries that are narrower (AST-only, pyproject-only, import-only, etc.).

---

## Layout

- **scripts/** - `run_competition_benchmarks.py` (wrapper around `scripts/competition_tests/benchmark_competition.py`, syncs outputs).
- **data/** - `BENCH_*.json` and raw outputs from `scripts/competition_tests/output_log/`; **`data/pytest_benchmark/`** stores pytest-benchmark history (merged from repo-root `.benchmarks/`; see that README).
- **benchmarks/** - BENCH_* reports, `INDEX.md`, `BENCHMARK_SUMMARY.md`, `BENCHMARK_WINS_SUMMARY.md`, `COMPETITION_SUMMARY.md`.

---

## How to run

From **xwlazy** project root:

```bash
# 1) Install competition harness dependencies (once)
pip install -r "benchmarks/20260209-benchmark competition/scripts/competition_tests/requirements.txt"

# 2) Run full competition (all libraries, all tests)
python "benchmarks/20260209-benchmark competition/scripts/run_competition_benchmarks.py"

# 3) Optional: limit libraries or tests
python "benchmarks/20260209-benchmark competition/scripts/run_competition_benchmarks.py" --library xwlazy --test medium_load
python "benchmarks/20260209-benchmark competition/scripts/run_competition_benchmarks.py" --library all --test light_load
```

The wrapper:

1. Calls `benchmarks/20260209-benchmark competition/scripts/competition_tests/benchmark_competition.py`.  
2. Detects new `BENCH_*.md` / `BENCH_*.json` in `scripts/competition_tests/output_log/`.  
3. Copies Markdown into this campaign's `benchmarks/` and JSON into `data/`.

---

## Results

**Latest competition (2026-02-10, `BENCH_20260210_2011_COMPETITION`, AUTO mode, standard tests):**

| Load level      | xwlazy (ms)          | Best other library (ms)         |
|-----------------|----------------------|---------------------------------|
| `light_load`    | 2.15                 | lazy-imports-lite - 0.73        |
| `medium_load`   | **4.06 (fastest)**   | lazy-imports-lite - 4.54        |
| `heavy_load`    | 14.46                | pylazyimports - 13.70           |
| `enterprise_load` | 41.37             | pylazyimports - 34.60           |

- Per-library detail: `benchmarks/BENCH_20260210_2011_COMPETITION.md`.
- Aggregated rankings: `benchmarks/BENCHMARK_SUMMARY.md`, `benchmarks/BENCHMARK_WINS_SUMMARY.md`, `benchmarks/COMPETITION_SUMMARY.md`.
- Raw JSON: `data/BENCH_*.json`.

---

## Conclusion (from that run)

- **Production (deps pre-installed):** `mode="lite"` for lowest overhead on lazy imports.
- **Development / CI (on-demand installs):** `mode="smart"` to pull missing deps on first use while staying close on medium/heavy loads.
- **Cleanup-focused runs:** `mode="clean"` (install + auto-uninstall) or PRELOAD/BACKGROUND when setup/teardown dominates.
- **Raw speed only:** **lazi** and others can win micro-benchmarks; they do not ship xwlazy's mode matrix, per-package isolation, or audit hooks. Pick xwlazy when you need those together, not when you only need the smallest possible import shim.

After each new campaign, refresh the date, table above, and links to the primary BENCH_* file and key JSON under `data/`.

---

## Related

- [GUIDE_54_BENCH.md](../../../.docs/guides/GUIDE_54_BENCH.md) - benchmarking guide (structure, runs, docs, SLAs)  
- [REF_54_BENCH.md](../../docs/REF_54_BENCH.md) - xwlazy performance SLAs / NFRs (if defined)  
- [../INDEX.md](../INDEX.md) - benchmarks index for xwlazy
