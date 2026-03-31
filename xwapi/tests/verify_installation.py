#exonware/xwapi/tests/verify_installation.py
"""
Verify xwapi installation and basic imports.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations
import sys
from pathlib import Path


def _add_monorepo_paths() -> None:
    """Add xwapi and xwsystem src to path for standalone run."""
    root = Path(__file__).resolve().parent.parent
    for pkg in ("xwapi", "xwsystem"):
        src = root.parent / pkg / "src"
        if src.is_dir():
            sys.path.insert(0, str(src))
_add_monorepo_paths()
# GUIDE_TEST.md: ensure UTF-8 console for Windows (emojis)
try:
    from exonware.xwsystem.console.cli import ensure_utf8_console
    ensure_utf8_console()
except Exception:
    pass


def test_import():
    """Test basic import of xwapi."""
    try:
        import exonware.xwapi
        print("✅ xwapi import successful")
        return True
    except ImportError as e:
        print(f"❌ xwapi import failed: {e}")
        return False


def test_version():
    """Test version information."""
    try:
        from exonware.xwapi import __version__, __author__, __email__
        print(f"✅ Version: {__version__}")
        print(f"✅ Author: {__author__}")
        print(f"✅ Email: {__email__}")
        return True
    except ImportError as e:
        print(f"❌ Version import failed: {e}")
        return False
if __name__ == "__main__":
    print("Verifying xwapi installation...")
    print()
    success = True
    success &= test_import()
    success &= test_version()
    print()
    if success:
        print("✅ All installation checks passed!")
        sys.exit(0)
    else:
        print("❌ Some installation checks failed!")
        sys.exit(1)
