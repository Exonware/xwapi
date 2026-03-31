#!/usr/bin/env python3
"""
#exonware/xwjson/src/exonware/xwjson/facade.py
XWJSON Facade - Main Public API
This module provides the main public API for xwjson following GUIDE_DEV.md facade pattern.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 07-Jan-2025
"""

from typing import Any
from pathlib import Path
from .formats.binary.xwjson.serializer import XWJSONSerializer
from .config import XWJSONConfig


class XWJSON:
    """
    Main XWJSON class providing extended binary JSON format.
    This class implements the facade pattern, providing a unified API for
    XWJSON operations including serialization, lazy loading, transactions,
    and format conversion.
    """

    def __init__(
        self,
        max_depth: int | None = None,
        max_size_mb: float | None = None,
        enable_cache: bool = True,
        **options
    ):
        """
        Initialize XWJSON.
        Args:
            max_depth: Maximum nesting depth
            max_size_mb: Maximum size in MB
            enable_cache: Enable file caching
            **options: Additional configuration options
        """
        self._config = XWJSONConfig(
            max_depth=max_depth,
            max_size_mb=max_size_mb,
            enable_cache=enable_cache
        )
        self._serializer = XWJSONSerializer(
            max_depth=max_depth,
            max_size_mb=max_size_mb,
            enable_cache=enable_cache
        )

    async def load(self, path: Path | str) -> Any:
        """
        Load XWJSON file asynchronously.
        Args:
            path: File path
        Returns:
            Loaded data
        """
        return await self._serializer.load_file_async(path)

    async def save(self, data: Any, path: Path | str) -> None:
        """
        Save data to XWJSON file asynchronously.
        Args:
            data: Data to save
            path: File path
        """
        await self._serializer.save_file_async(data, path)

    def encode(self, data: Any, options: dict[str, Any] | None = None) -> bytes:
        """
        Encode data to XWJSON format.
        Args:
            data: Data to encode
            options: Encoding options
        Returns:
            Encoded bytes
        """
        return self._serializer.encode(data, options)

    def decode(self, data: bytes, options: dict[str, Any] | None = None) -> Any:
        """
        Decode data from XWJSON format.
        Args:
            data: Data to decode
            options: Decoding options
        Returns:
            Decoded data
        """
        return self._serializer.decode(data, options)
    @property

    def serializer(self) -> XWJSONSerializer:
        """Get underlying serializer instance."""
        return self._serializer
