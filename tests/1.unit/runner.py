#!/usr/bin/env python3
"""
#exonware/xwapi/tests/1.unit/runner.py
Unit test runner for xwapi.
Fine-grained per-module tests.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 18-Dec-2025
"""

import sys
import os
from pathlib import Path
# Add src to path if needed
test_dir = Path(__file__).parent
monorepo_root = test_dir.parent.parent.parent
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
# ⚠️ CRITICAL: Configure UTF-8 encoding for Windows console using xwsystem utility
# NEVER manually configure UTF-8 - always use xwsystem's ensure_utf8_console()
from exonware.xwsystem.console.cli import ensure_utf8_console
ensure_utf8_console()
import pytest


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


def main() -> None:
    """Run unit tests."""
    # Force pytest rootdir/config discovery to use the xwapi project folder
    monorepo_root = _find_monorepo_root(Path(__file__).resolve())
    os.chdir(monorepo_root / "xwapi")
    _add_monorepo_src_paths()
    # Use xwsystem TestRunner utility
    from exonware.xwsystem.utils.test_runner import TestRunner
    test_dir = Path(__file__).parent
    runner = TestRunner(
        library_name="xwapi",
        layer_name="1.unit",
        description="Unit Tests - Fine-Grained Per-Module Tests",
        test_dir=test_dir,
        markers=["xwapi_unit"]
    )
    raise SystemExit(runner.run())
if __name__ == "__main__":
    main()
