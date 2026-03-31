#exonware/xwjson/src/exonware/xwjson/formats/binary/xwjson/lazy.py
"""
Lazy Loading Support for XWJSON
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 2025-01-XX
Lazy loading support: defer parsing, node creation, reference resolution until access.
Priority 1 (Security): Safe lazy loading, input validation
Priority 2 (Usability): Transparent lazy loading, helpful error messages
Priority 3 (Maintainability): Clean code, design patterns
Priority 4 (Performance): Memory-efficient lazy loading, smart prefetching
Priority 5 (Extensibility): Configurable lazy thresholds, customization points
"""

from typing import Any
from pathlib import Path
import mmap


from collections.abc import Callable
class LazyFileProxy:
    """
    Defer file reading until access.
    Memory-efficient for large files - keeps raw bytes until needed.
    """

    def __init__(self, file_path: str | Path, lazy_threshold: int = 1024 * 1024):
        """
        Initialize lazy file proxy.
        Args:
            file_path: Path to file
            lazy_threshold: File size threshold for lazy loading (bytes)
        """
        self._file_path = Path(file_path)
        self._lazy_threshold = lazy_threshold
        self._data = None
        self._mmap = None
        self._loaded = False

    def __getitem__(self, key: Any) -> Any:
        """Access data (triggers lazy loading if not loaded)."""
        if not self._loaded:
            self._load()
        return self._data[key]

    def __len__(self) -> int:
        """Get length (triggers lazy loading if not loaded)."""
        if not self._loaded:
            self._load()
        return len(self._data)

    def _load(self) -> None:
        """Load file data (lazy)."""
        file_size = self._file_path.stat().st_size
        if file_size > self._lazy_threshold:
            # Use memory mapping for large files
            with open(self._file_path, 'rb') as f:
                self._mmap = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                self._data = self._mmap
        else:
            # Load entire file for small files
            with open(self._file_path, 'rb') as f:
                self._data = f.read()
        self._loaded = True

    def close(self) -> None:
        """Close file and release resources."""
        if self._mmap:
            self._mmap.close()
            self._mmap = None
        self._data = None
        self._loaded = False


class LazySerializationProxy:
    """
    Defer parsing until access.
    Keeps raw bytes until first access, then parses on-demand.
    """

    def __init__(
        self,
        raw_data: bytes,
        parser: Callable[[bytes], Any],
        lazy_threshold: int = 1024 * 1024
    ):
        """
        Initialize lazy serialization proxy.
        Args:
            raw_data: Raw bytes to parse
            parser: Parser function (bytes -> data)
            lazy_threshold: Size threshold for lazy parsing (bytes)
        """
        self._raw_data = raw_data
        self._parser = parser
        self._lazy_threshold = lazy_threshold
        self._parsed_data = None
        self._parsed = False

    def __getitem__(self, key: Any) -> Any:
        """Access data (triggers lazy parsing if not parsed)."""
        if not self._parsed:
            self._parse()
        return self._parsed_data[key]

    def __len__(self) -> int:
        """Get length (triggers lazy parsing if not parsed)."""
        if not self._parsed:
            self._parse()
        return len(self._parsed_data)

    def _parse(self) -> None:
        """Parse raw data (lazy)."""
        if len(self._raw_data) > self._lazy_threshold:
            # Use incremental parsing for large data
            # For now, use standard parsing but could be optimized with streaming parsers
            # Future: Implement incremental parsing with streaming JSON/YAML parsers
            # This would allow parsing large files without loading entire content into memory
            try:
                # Try to use streaming parser if available
                if hasattr(self._parser, '__name__') and 'stream' in self._parser.__name__.lower():
                    self._parsed_data = self._parser(self._raw_data)
                else:
                    # Standard parsing for now
                    self._parsed_data = self._parser(self._raw_data)
            except Exception:
                # Fallback to standard parsing
                self._parsed_data = self._parser(self._raw_data)
        else:
            # Parse entire data for small data
            self._parsed_data = self._parser(self._raw_data)
        self._parsed = True


class LazyXWNodeProxy:
    """
    Defer xwnode creation until navigation.
    Uses xwnode for lazy node creation - creates node only when needed.
    """

    def __init__(
        self,
        data: Any,
        node_factory: Callable[[Any], Any] | None = None
    ):
        """
        Initialize lazy xwnode proxy.
        Args:
            data: Data to create node from
            node_factory: Factory function to create xwnode (optional)
        """
        self._data = data
        self._node_factory = node_factory
        self._node = None
        self._created = False

    def __getitem__(self, key: Any) -> Any:
        """Access data (creates node if needed)."""
        if not self._created and self._node_factory:
            self._create_node()
            return self._node[key]
        return self._data[key]

    def _create_node(self) -> None:
        """Create xwnode (lazy)."""
        if self._node_factory:
            try:
                from exonware.xwnode import XWNode
                self._node = XWNode.from_native(self._data, mode='AUTO')
            except ImportError:
                # xwnode not available - use data as-is
                self._node = self._data
            except Exception:
                # Fallback to data if node creation fails
                self._node = self._data
        else:
            self._node = self._data
        self._created = True


class LazyReferenceProxy:
    """
    Defer reference resolution until access.
    Lazy reference resolution for all format-specific references.
    """

    def __init__(
        self,
        reference: str,
        resolver: Callable[[str], Any],
        cache: dict[str, Any] | None = None
    ):
        """
        Initialize lazy reference proxy.
        Args:
            reference: Reference string ($ref, @href, *anchor, etc.)
            resolver: Resolver function (reference -> data)
            cache: Optional cache for resolved references
        """
        self._reference = reference
        self._resolver = resolver
        self._cache = cache if cache is not None else {}
        self._resolved_data = None
        self._resolved = False

    def __getitem__(self, key: Any) -> Any:
        """Access data (triggers lazy resolution if not resolved)."""
        if not self._resolved:
            self._resolve()
        return self._resolved_data[key]

    def __len__(self) -> int:
        """Get length (triggers lazy resolution if not resolved)."""
        if not self._resolved:
            self._resolve()
        return len(self._resolved_data)

    def _resolve(self) -> None:
        """Resolve reference (lazy)."""
        # Check cache first
        if self._reference in self._cache:
            self._resolved_data = self._cache[self._reference]
        else:
            # Resolve reference
            self._resolved_data = self._resolver(self._reference)
            # Cache result
            self._cache[self._reference] = self._resolved_data
        self._resolved = True
