#exonware/xwjson/src/exonware/xwjson/__init__.py
"""
xwjson: Extended Binary JSON Format
XWJSON is an extended binary JSON format that serves as the single version of truth
for all format conversions. It is a separate library that extends xwsystem serialization,
exactly like XWFormats.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 2025-01-XX
Key Features:
- Binary-first design (MessagePack-based encoding)
- Lazy loading support (defer parsing until access)
- Reference support (all format-specific: $ref JSON, @href XML, *anchor YAML)
- xwnode integration (dependency graphs, graph operations, topological sort)
- xwschema integration (schema validation, fast compiled schemas)
- Format metadata preservation (YAML anchors, XML namespaces, TOML tables, etc.)
- Universal intermediate format (single source of truth)
- Async-first architecture (all operations async by default)
- Transaction support (ACID guarantees with zero performance penalty)
- Smart batch operations (dependency-aware, parallel execution)
Installation:
    # Install with all dependencies
    pip install exonware-xwjson[full]
    # Or minimal install (dependencies required separately)
    pip install exonware-xwjson
"""
# =============================================================================
# XWLAZY INTEGRATION — GUIDE_00_MASTER: config_package_lazy_install_enabled (EARLY)
# =============================================================================
# Dependency: exonware-xwlazy (PyPI). Import canonical namespace: exonware.xwlazy
# (top-level alias package: xwlazy).
try:
    from exonware.xwlazy import config_package_lazy_install_enabled

    config_package_lazy_install_enabled(
        __package__ or "exonware.xwjson",
        enabled=True,
        mode="smart",
    )
except ImportError:
    # xwlazy not installed — omit [lazy] extra or install exonware-xwlazy for lazy mode.
    pass
from .version import __version__
# Version metadata constants
__author__ = "eXonware Backend Team"
__email__ = "connect@exonware.com"
__company__ = "eXonware.com"
# Import main serializer
from .formats.binary.xwjson.serializer import XWJSONSerializer
# Import facade for main public API
from .facade import XWJSON
# ============================================================================
# AUTO-REGISTRATION WITH UNIVERSALCODECREGISTRY
# ============================================================================

def _auto_register():
    """
    Auto-register XWJSONSerializer with UniversalCodecRegistry on import.
    Registers:
    - XWJSONSerializer → codec_types: ["binary", "serialization"]
    - Magic bytes: b'XWJ1' (Extended JSON v1)
    Note: xwnode and xwschema are required dependencies, which bring xwsystem transitively.
    No try/except per DEV_GUIDELINES.md - if registration fails, it should fail-fast.
    """
    from exonware.xwsystem.io.codec.registry import get_registry
    registry = get_registry()
    # Register with magic bytes for content detection
    registry.register(
        XWJSONSerializer,
        magic_bytes=[b'XWJ1'],  # Magic: XWJ1 (Extended JSON v1)
        priority=10  # Higher priority for XWJSON format
    )
# Run auto-registration
_auto_register()


def is_encrypted(bytes_or_path: bytes | str) -> bool:
    """
    Return True if the payload or file is an XWJE encrypted envelope.
    Accepts bytes (first 4 bytes must be b'XWJE') or a file path (peeks first 4 bytes).
    """
    from pathlib import Path
    if isinstance(bytes_or_path, bytes):
        return len(bytes_or_path) >= 4 and bytes_or_path[:4] == b"XWJE"
    path = Path(bytes_or_path)
    if not path.exists():
        return False
    try:
        with path.open("rb") as f:
            return f.read(4) == b"XWJE"
    except OSError:
        return False
__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__email__',
    '__company__',
    # Main classes
    'XWJSONSerializer',
    'XWJSON',
    'is_encrypted',
]
