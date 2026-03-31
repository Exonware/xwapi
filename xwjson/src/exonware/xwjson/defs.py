#!/usr/bin/env python3
"""
#exonware/xwjson/src/exonware/xwjson/defs.py
Type definitions and enums for xwjson.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 07-Jan-2025
"""

from enum import Enum


class XWJSONVersion(Enum):
    """XWJSON format versions."""
    V1 = "1.0"


class ReferenceType(Enum):
    """Reference types."""
    JSON_REF = "$ref"
    XML_HREF = "@href"
    YAML_ANCHOR = "*anchor"
    XWJSON_REF = "xwjson_ref"


class LazyLoadingMode(Enum):
    """Lazy loading modes."""
    EAGER = "eager"
    LAZY = "lazy"
    HYBRID = "hybrid"


class TransactionMode(Enum):
    """Transaction modes."""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    WRITE_ONLY = "write_only"


class ParserType(Enum):
    """Parser types."""
    MSGSPEC = "msgspec"
    ORJSON = "orjson"
    HYBRID = "hybrid"
