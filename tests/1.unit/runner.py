#!/usr/bin/env python3
"""
#exonware/xwapi/tests/1.unit/runner.py
Unit test runner for xwapi.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 18-Dec-2025
"""

from __future__ import annotations

import os
from pathlib import Path

from exonware.xwsystem.console.cli import ensure_utf8_console

ensure_utf8_console()

_XWAPI_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    """Run unit tests (expects editable installs / venv)."""
    os.chdir(_XWAPI_ROOT)
    from exonware.xwsystem.utils.test_runner import TestRunner

    test_dir = Path(__file__).parent
    runner = TestRunner(
        library_name="xwapi",
        layer_name="1.unit",
        description="Unit Tests - Individual Component Validation",
        test_dir=test_dir,
        markers=["xwapi_unit"],
        pytest_cwd=_XWAPI_ROOT,
    )
    raise SystemExit(runner.run())


if __name__ == "__main__":
    main()
