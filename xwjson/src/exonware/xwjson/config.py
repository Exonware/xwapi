#!/usr/bin/env python3
"""
#exonware/xwjson/src/exonware/xwjson/config.py
Configuration classes for xwjson.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 07-Jan-2025
"""

from dataclasses import dataclass
from .defs import LazyLoadingMode, ParserType
@dataclass

class XWJSONConfig:
    """Configuration for XWJSON."""
    max_depth: int | None = None
    max_size_mb: float | None = None
    read_parser: ParserType = ParserType.MSGSPEC
    write_parser: ParserType = ParserType.MSGSPEC
    enable_cache: bool = True
    lazy_loading_mode: LazyLoadingMode = LazyLoadingMode.LAZY
    enable_transactions: bool = True
    enable_references: bool = True
    enable_schema_validation: bool = True
