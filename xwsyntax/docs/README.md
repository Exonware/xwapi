# xwsyntax documentation

Pointers into the doc set for this package.

## Primary

- **[INDEX.md](INDEX.md)** - full index  
- **[GUIDE_01_USAGE.md](GUIDE_01_USAGE.md)** - install modes, grammar loading, troubleshooting  
- **[../README.md](../README.md)** - package overview and quick start  

## Reference

- [REF_01_REQ.md](REF_01_REQ.md), [REF_22_PROJECT.md](REF_22_PROJECT.md) - requirements and status  
- [REF_15_API.md](REF_15_API.md), [REF_13_ARCH.md](REF_13_ARCH.md), [REF_14_DX.md](REF_14_DX.md)  
- [REF_51_TEST.md](REF_51_TEST.md) - testing  

## Install (quick)

```bash
pip install exonware-xwsyntax[full]
```

```python
from exonware.xwsyntax import BidirectionalGrammar
grammar = BidirectionalGrammar.load('json')
```

Run tests from repo root: `python tests/runner.py`.
