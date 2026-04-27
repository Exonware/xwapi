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

from __future__ import annotations

import os
import sys
from pathlib import Path

from exonware.xwsystem.console.cli import ensure_utf8_console

ensure_utf8_console()

_XWAPI_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    """Run advance tests. Layer runners stream only (no file writes)."""
    os.chdir(_XWAPI_ROOT)
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
        pytest_cwd=_XWAPI_ROOT,
    )
    code = runner.run()
    if code == 5:
        code = 0
    raise SystemExit(code)


if __name__ == "__main__":
    main()
