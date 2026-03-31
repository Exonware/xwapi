# XWJSON tests

Layout follows the monorepo test guide (four layers: core, unit, integration, advance).

## Layout

```
tests/
├── 0.core/                    # Imports and basic round-trips
│   ├── test_import.py
│   └── test_basic_encoding.py
├── 1.unit/
│   ├── formats_tests/
│   │   └── binary_tests/
│   │       └── xwjson_tests/  # encoder, serializer, references, lazy, dependency graph
│   └── operations_tests/
│       └── test_xwjson_ops.py
├── 2.integration/
│   └── scenarios/             # stress: large files, concurrency, memory, xwnode, transactions, …
└── 3.advance/                 # security, usability, maintainability, performance, extensibility
```

## Running

```bash
python tests/runner.py
```

By layer:

```bash
pytest tests/0.core/ -v
pytest tests/1.unit/ -v
pytest tests/2.integration/ -v
pytest tests/3.advance/ -v
```

By marker:

```bash
pytest -m xwjson_performance -v
pytest -m xwjson_security -v
pytest -m xwjson_lazy -v
pytest -m xwjson_references -v
```

## What each layer targets

- **0.core** - import, round-trip, types, metadata, magic bytes, file helpers.
- **1.unit** - encoder/decoder (hybrid parser), serializer surface, references across JSON/XML/YAML/TOML, lazy modes, dependency graph, CRUD-style data ops.
- **2.integration** - large files, concurrency, memory, xwnode cache/index strategies, transactions, queries, batches, references under load, schema validation, lazy at scale.
- **3.advance** - security (paths, validation, cycles), API ergonomics, structure/type quality, speed, extensibility hooks.

Stress scenarios push large item counts, many concurrent operations, and lazy/streaming paths; see individual test modules for thresholds.

## xwnode

Integration tests use strategies such as `NodeMode.LRU_CACHE` and `NodeMode.HASH_MAP` for caching and O(1) lookups where configured.

## Markers

`xwjson_core`, `xwjson_unit`, `xwjson_integration`, `xwjson_advance`, `xwjson_performance`, `xwjson_security`, `xwjson_lazy`, `xwjson_references`, `xwjson_serialization`.

## Requirements

- `exonware-xwnode` (cache, index, paging)
- `exonware-xwschema` (validation)
- `exonware-xwquery` (optional, advanced queries)
- `pytest`, `pytest-asyncio`

```bash
pip install exonware-xwjson[full]
```
