#!/usr/bin/env python3
"""
#exonware/xwjson/src/exonware/xwjson/base.py
Abstract base classes for xwjson.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 07-Jan-2025
"""

from abc import ABC, abstractmethod
from typing import Any
from pathlib import Path
from .contracts import IXWJSONSerializer, IXWJSONOperations, IXWJSONConverter


class AXWJSONSerializer(IXWJSONSerializer, ABC):
    """Abstract base class for XWJSON serializer."""
    @property
    @abstractmethod

    def codec_id(self) -> str:
        """Get codec identifier."""
    @property
    @abstractmethod

    def format_name(self) -> str:
        """Get format name."""
    @property
    @abstractmethod

    def is_binary_format(self) -> bool:
        """Check if format is binary."""
    @abstractmethod

    def encode(self, data: Any, options: dict[str, Any] | None = None) -> bytes:
        """Encode data to XWJSON format."""
    @abstractmethod

    def decode(self, data: bytes, options: dict[str, Any] | None = None) -> Any:
        """Decode data from XWJSON format."""
    @abstractmethod

    async def load_file_async(self, path: Path | str) -> Any:
        """Load file asynchronously."""
    @abstractmethod

    async def save_file_async(self, data: Any, path: Path | str) -> None:
        """Save file asynchronously."""


class AXWJSONOperations(IXWJSONOperations, ABC):
    """Abstract base class for XWJSON operations."""
    @abstractmethod

    async def batch_operations(self, operations: list[dict[str, Any]]) -> list[Any]:
        """Execute batch operations."""
    @abstractmethod

    async def transaction(self, operations: list[dict[str, Any]]) -> Any:
        """Execute transaction."""


class AXWJSONConverter(IXWJSONConverter, ABC):
    """Abstract base class for XWJSON format conversion."""
    @abstractmethod

    async def convert_to_xwjson(
        self,
        data: Any,
        from_format: str,
        options: dict[str, Any] | None = None
    ) -> Any:
        """Convert data to XWJSON format."""
    @abstractmethod

    async def convert_from_xwjson(
        self,
        data: Any,
        to_format: str,
        options: dict[str, Any] | None = None
    ) -> Any:
        """Convert data from XWJSON format."""
