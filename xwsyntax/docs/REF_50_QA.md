# Quality Assurance Reference — xwsyntax

**Library:** exonware-xwsyntax  
**Produced by:** [GUIDE_50_QA.md](https://github.com/exonware/exonware/blob/main/.docs/guides/GUIDE_50_QA.md) (central guide)  
**Last Updated:** 26-Mar-2026

---

## Purpose

**Quality gates and readiness** for this package: what must pass before a release, and where evidence lives.

---

## Gates (summary)

1. **Tests:** `python tests/runner.py` (or layer runners) — see [REF_51_TEST.md](REF_51_TEST.md).  
2. **Docs/API:** Public surface matches [REF_15_API.md](REF_15_API.md) and [REF_14_DX.md](REF_14_DX.md).  
3. **Packaging:** `pyproject.toml` dependencies match runtime imports (exonware-xwsystem, exonware-xwnode, exonware-xwlazy, lark).  
4. **Benchmarks (when applicable):** [REF_54_BENCH.md](REF_54_BENCH.md) and `benchmarks/` at repo root.

---

## Readiness state

- **Last full sweep:** Align with repo state after packaging fix (2026-03-26).  
- **Release:** Follow [GUIDE_61_DEP](https://github.com/exonware/exonware/blob/main/.docs/guides/GUIDE_61_DEP.md); evidence under `docs/logs/releases/` when used.

---

## Related

| Guide | Role |
|-------|------|
| [GUIDE_50_QA](https://github.com/exonware/exonware/blob/main/.docs/guides/GUIDE_50_QA.md) | QA orchestration (central) |
| [GUIDE_51_TEST](https://github.com/exonware/exonware/blob/main/.docs/guides/GUIDE_51_TEST.md) | Test implementation |
| [REF_51_TEST.md](REF_51_TEST.md) | Test status |
