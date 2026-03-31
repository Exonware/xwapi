#!/usr/bin/env python3
"""
#exonware/xwapi/tests/3.advance/runner.py
Advance test runner for xwapi (3.advance layer).
Production excellence validation (v1.0.0+). GUIDE_TEST.md compliant.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 07-Jan-2025
"""

import sys
import os
from pathlib import Path


def _find_monorepo_root(start: Path) -> Path:
    """Find the monorepo root (folder that contains xwapi + xwsystem)."""
    for p in [start] + list(start.parents):
        if (p / "xwapi").is_dir() and (p / "xwsystem").is_dir():
            return p
    return start.parents[2]


def _add_monorepo_src_paths() -> None:
    """Add all required sibling package src/ folders to sys.path for monorepo testing."""
    monorepo_root = _find_monorepo_root(Path(__file__).resolve())
    for pkg in (
        "xwapi",
        "xwsystem",
        "xwentity",
        "xwauth",
        "xwstorage",
        "xwaction",
        "xwschema",
        "xwdata",
        "xwnode",
        "xwquery",
        "xwjson",
        "xwsyntax",
    ):
        src = monorepo_root / pkg / "src"
        if src.is_dir():
            sys.path.insert(0, str(src))
_add_monorepo_src_paths()
# ⚠️ CRITICAL: Configure UTF-8 encoding for Windows console using xwsystem utility (GUIDE_TEST.md)
from exonware.xwsystem.console.cli import ensure_utf8_console
ensure_utf8_console()


def main() -> None:
    """Run advance tests. Layer runners stream only (no file writes)."""
    monorepo_root = _find_monorepo_root(Path(__file__).resolve())
    os.chdir(monorepo_root / "xwapi")
    args = sys.argv[1:]
    marker = "xwapi_advance"
    if "--security" in args:
        marker = "xwapi_security"
    elif "--performance" in args:
        marker = "xwapi_performance"
    elif "--usability" in args:
        marker = "xwapi_usability"
    elif "--maintainability" in args:
        marker = "xwapi_maintainability"
    elif "--extensibility" in args:
        marker = "xwapi_extensibility"
    from exonware.xwsystem.utils.test_runner import TestRunner
    runner = TestRunner(
        library_name="xwapi",
        layer_name="3.advance",
        description="Advance Tests - Production Excellence (v1.0.0+)",
        test_dir=Path(__file__).parent,
        markers=[marker],
    )
    code = runner.run()
    # Pytest exit 5 = no tests collected; treat as success (GUIDE_TEST: advance optional until v1.0.0)
    if code == 5:
        code = 0
    raise SystemExit(code)
if __name__ == "__main__":
    main()
