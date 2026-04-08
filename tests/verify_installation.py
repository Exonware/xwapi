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

try:
    from exonware.xwsystem.console.cli import ensure_utf8_console

    ensure_utf8_console()
except Exception:
    pass


def test_import():
    """Test basic import of xwapi."""
    try:
        import exonware.xwapi  # noqa: F401

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
