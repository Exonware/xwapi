"""One-off: list third-party top-level modules under src/exonware/xwsystem."""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "xwsystem" / "src" / "exonware" / "xwsystem"

STDLIB: set[str] = set(getattr(sys, "stdlib_module_names", ()))
STDLIB.add("__future__")


def walk_imports(tree: ast.AST) -> set[str]:
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                out.add(node.module.split(".")[0])
    return out


def main() -> None:
    mods: set[str] = set()
    for path in sorted(ROOT.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        mods |= walk_imports(tree)
        for rx in (
            r"import_module\(\s*['\"]([a-zA-Z0-9_.]+)['\"]",
            r"__import__\(\s*['\"]([a-zA-Z0-9_.]+)['\"]",
            r"find_spec\(\s*['\"]([a-zA-Z0-9_.]+)['\"]",
        ):
            for m in re.finditer(rx, text):
                mods.add(m.group(1).split(".")[0])

    third = []
    for m in sorted(mods, key=str.lower):
        if m == "exonware" or m.startswith("exonware_"):
            continue
        if m in STDLIB:
            continue
        third.append(m)
    for m in third:
        print(m)


if __name__ == "__main__":
    main()
