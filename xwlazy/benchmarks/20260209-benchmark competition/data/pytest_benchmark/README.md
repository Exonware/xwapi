# pytest-benchmark storage (merged from `.benchmarks/`)

Historical runs from **pytest-benchmark** (`--benchmark-save` / compare) for **Windows, CPython 3.12, 64-bit** live in `Windows-CPython-3.12-64bit/`.

**Use this directory as storage** (from xwlazy root):

```bash
pytest "benchmarks/20260209-benchmark competition/scripts/test_lazy_benchmarks.py" --benchmark-only ^
  --benchmark-storage="benchmarks/20260209-benchmark competition/data/pytest_benchmark"
```

pytest-benchmark will create additional `<Machine>-<Implementation>-<Bits>/` subfolders for other environments; commit only what you intend to keep as evidence.
