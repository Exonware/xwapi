#!/usr/bin/env python3
"""
#exonware/xwjson/src/exonware/xwjson/contracts.py
Protocol interfaces for xwjson.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 07-Jan-2025
"""

from typing import Any, Protocol, runtime_checkable
from pathlib import Path
@runtime_checkable

class IXWJSONSerializer(Protocol):
    """Interface for XWJSON serializer."""
    @property

    def codec_id(self) -> str:
        """Get codec identifier."""
        ...
    @property

    def format_name(self) -> str:
        """Get format name."""
        ...
    @property

    def is_binary_format(self) -> bool:
        """Check if format is binary."""
        ...

    def encode(self, data: Any, options: dict[str, Any] | None = None) -> bytes:
        """Encode data to XWJSON format."""
        ...

    def decode(self, data: bytes, options: dict[str, Any] | None = None) -> Any:
        """Decode data from XWJSON format."""
        ...

    async def load_file_async(self, path: Path | str) -> Any:
        """Load file asynchronously."""
        ...

    async def save_file_async(self, data: Any, path: Path | str) -> None:
        """Save file asynchronously."""
        ...
@runtime_checkable

class IXWJSONOperations(Protocol):
    """Interface for XWJSON operations."""

    async def batch_operations(self, operations: list[dict[str, Any]]) -> list[Any]:
        """Execute batch operations."""
        ...

    async def transaction(self, operations: list[dict[str, Any]]) -> Any:
        """Execute transaction."""
        ...
@runtime_checkable

class IXWJSONConverter(Protocol):
    """Interface for XWJSON format conversion."""

    async def convert_to_xwjson(
        self,
        data: Any,
        from_format: str,
        options: dict[str, Any] | None = None
    ) -> Any:
        """Convert data to XWJSON format."""
        ...

    async def convert_from_xwjson(
        self,
        data: Any,
        to_format: str,
        options: dict[str, Any] | None = None
    ) -> Any:
        """Convert data from XWJSON format."""
        ...
