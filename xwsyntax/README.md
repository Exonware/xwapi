# xwsyntax

Bidirectional grammars: parse text to an AST, emit text again, or hop formats by reusing the same tree (for example JSON in, SQL out). 100+ grammars (300+ files) covering query languages, data formats, and code. Used by xwquery and editor/Monaco flows.

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com  

[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Install

```bash
pip install exonware-xwsyntax
pip install exonware-xwsyntax[lazy]
pip install exonware-xwsyntax[full]
```

Runtime deps are declared in `pyproject.toml` (`lark`, `exonware-xwsystem`, `exonware-xwnode`, `exonware-xwlazy` wiring). See [docs/GUIDE_01_USAGE.md](docs/GUIDE_01_USAGE.md) for modes and troubleshooting.

---

## Quick start

```python
from exonware.xwsyntax import BidirectionalGrammar

grammar = BidirectionalGrammar.load('json')
ast = grammar.parse('{"name": "Alice", "age": 30}')
json_str = grammar.generate(ast)

sql_grammar = BidirectionalGrammar.load('sql')
sql = sql_grammar.generate(ast)
```

Facade: `XWSyntax().parse(text, format_name)` or `validate(text, format_name)`.  
Discovery: `list_grammars_quick()`, `load_grammar_quick(name)`.  
More code paths: [REF_14_DX](docs/REF_14_DX.md), API: [REF_15_API](docs/REF_15_API.md).

---

## Examples

### Facade parse/validate

```python
from exonware.xwsyntax import XWSyntax

engine = XWSyntax()
ast = engine.parse("a = 1 + 2", format_name="python")
is_valid = engine.validate("a = 1 + 2", format_name="python")
```

### List and load grammars

```python
from exonware.xwsyntax import list_grammars_quick, load_grammar_quick

names = list_grammars_quick()
grammar = load_grammar_quick(names[0])
```

### JSON to SQL via shared AST

```python
from exonware.xwsyntax import BidirectionalGrammar

ast = BidirectionalGrammar.load("json").parse('{"name": "Alice", "age": 30}')
sql = BidirectionalGrammar.load("sql").generate(ast)
```

---

## What you get

| Area | Contents |
|------|----------|
| **Read/write** | Grammar-driven parse and generate; avoid hand-maintained per-format maps. |
| **Bidirectional** | Round-trip or cross-syntax by swapping grammars on the same AST. |
| **Large grammar set** | SQL, Cypher, GraphQL, xwqueryscript, configs, programming languages, markup, storage dialects; 300+ `.lark` / `.json` assets. |
| **Downstream** | xwquery parsing; Monaco export and codec hooks via xwsystem. |

Phase: **Alpha**. Milestones: [REF_22_PROJECT](docs/REF_22_PROJECT.md#project-status-overview).

---

## Docs and tests

- **Start:** [docs/INDEX.md](docs/INDEX.md)
- **Usage:** [docs/GUIDE_01_USAGE.md](docs/GUIDE_01_USAGE.md)
- **Requirements / status:** [REF_01_REQ](docs/REF_01_REQ.md), [REF_22_PROJECT](docs/REF_22_PROJECT.md)
- **API / design:** [REF_15_API](docs/REF_15_API.md), [REF_13_ARCH](docs/REF_13_ARCH.md), [REF_14_DX](docs/REF_14_DX.md)
- **Tests:** [REF_51_TEST](docs/REF_51_TEST.md). Run: `python tests/runner.py` from repo root.

---

## License and links

MIT - [LICENSE](LICENSE).  
**Homepage:** https://exonware.com · **Repository:** https://github.com/exonware/xwsyntax  

## Async Support

<!-- async-support:start -->
- xwsyntax is primarily synchronous in its current implementation.
- Source validation: 0 async def definitions and 0 await usages under src/.
- This module still composes with async-capable xw libraries at integration boundaries when needed.
<!-- async-support:end -->
Version: 0.6.0.19 | Updated: 31-Mar-2026

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
