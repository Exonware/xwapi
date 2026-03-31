#exonware/xwjson/src/exonware/xwjson/formats/binary/xwjson/serializer.py
"""
XWJSON Serializer - Extended Binary JSON Format
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 2025-01-XX
XWJSON is an extended binary JSON format that serves as the single version of truth
for all format conversions. This serializer extends ASerialization from xwsystem.
Following I→A→XW pattern:
- I: ISerialization (interface)
- A: ASerialization (abstract base)
- XW: XWJSONSerializer (concrete implementation)
Priority 1 (Security): Safe binary deserialization, path traversal protection
Priority 2 (Usability): Clear APIs, helpful error messages, intuitive design
Priority 3 (Maintainability): Clean code, design patterns, comprehensive documentation
Priority 4 (Performance): Fast operations, memory efficiency, scalability
Priority 5 (Extensibility): Plugin system, hooks, customization points
"""

from typing import Any
from pathlib import Path
import asyncio
# xwsystem comes transitively via xwnode/xwschema dependencies
from exonware.xwsystem.io.serialization.base import ASerialization
from exonware.xwsystem.io.contracts import EncodeOptions, DecodeOptions
from exonware.xwsystem.io.errors import SerializationError
# Import encoder/decoder
from .encoder import XWJSONEncoder, XWJSONDecoder
# Import operations (lazy to avoid circular import)
from collections.abc import Callable
XWJSONDataOperations = None  # Will be imported lazily


class XWJSONSerializer(ASerialization):
    """
    XWJSON (Extended Binary JSON) serializer.
    I: ISerialization (interface)
    A: ASerialization (abstract base)
    XW: XWJSONSerializer (concrete implementation)
    Features:
    - Binary-first design (MessagePack-based encoding)
    - Lazy loading support (defer parsing until access)
    - Reference support (all format-specific: $ref JSON, @href XML, *anchor YAML)
    - xwnode integration (dependency graphs, graph operations, topological sort)
    - xwschema integration (schema validation, fast compiled schemas)
    - Format metadata preservation (YAML anchors, XML namespaces, TOML tables, etc.)
    - Async-first architecture (all operations async by default)
    - Transaction support (ACID guarantees with zero performance penalty)
    - Smart batch operations (dependency-aware, parallel execution)
    Examples:
        >>> serializer = XWJSONSerializer()
        >>> 
        >>> # Async (default, recommended, fastest)
        >>> data = await serializer.load_file_async("data.xwjson")
        >>> await serializer.save_file_async(data, "output.xwjson")
        >>> 
        >>> # Sync (wrapper, for compatibility)
        >>> data = serializer.load_file("data.xwjson")
        >>> serializer.save_file(data, "output.xwjson")
    """
    # Class-level cache shared across all instances (singleton pattern)
    _file_cache = None           # For small files (< 10MB) - full data
    _index_cache = None          # For ALL files - index/meta only (ALWAYS cached)
    _mtime_cache = None          # Tracks mtime for data files
    _index_mtime_cache = None    # Tracks mtime for meta/index files
    _cache_lock = None
    _cache_initialized = False
    # Cache configuration
    CACHE_THRESHOLD_MB = 10.0  # Cache files < 10MB
    CACHE_CAPACITY = 1000      # Max number of cached files

    def __init__(
        self, 
        max_depth: int | None = None, 
        max_size_mb: float | None = None,
        read_parser: str | None = None,
        write_parser: str | None = None,
        enable_cache: bool = True
    ):
        """
        Initialize XWJSON serializer with intelligent file caching.
        Args:
            max_depth: Maximum nesting depth allowed (default: from ACodec)
            max_size_mb: Maximum estimated data size in MB (default: from ACodec)
            read_parser: Parser for reading ("msgspec", "orjson", "hybrid", or None for default)
                        Default: msgspec (fastest for reading)
            write_parser: Parser for writing ("orjson", "msgspec", "hybrid", or None for default)
                        Default: orjson (fastest for writing)
            enable_cache: Enable intelligent file caching for small files (< 10MB)
                         Default: True (recommended for better read performance)
        """
        super().__init__(max_depth=max_depth, max_size_mb=max_size_mb)
        self._encoder = XWJSONEncoder(write_parser=write_parser)
        self._decoder = XWJSONDecoder(read_parser=read_parser)
        self._ops = None  # Lazy initialization
        self._enable_cache = enable_cache
        # Initialize class-level cache (singleton)
        if enable_cache and not XWJSONSerializer._cache_initialized:
            XWJSONSerializer._initialize_cache()
    @classmethod

    def _initialize_cache(cls):
        """Initialize class-level cache (called once)."""
        if cls._cache_initialized:
            return
        from exonware.xwsystem.caching import create_cache
        import threading
        cls._file_cache = create_cache(capacity=cls.CACHE_CAPACITY, namespace='xwjson', name="XWJSONFileCache")
        cls._index_cache = create_cache(capacity=cls.CACHE_CAPACITY, namespace='xwjson', name="XWJSONIndexCache")
        cls._mtime_cache = {}  # Track file modification times (for data files)
        cls._index_mtime_cache = {}  # Track meta/index file modification times
        cls._cache_lock = threading.RLock()
        cls._cache_initialized = True
    # ========================================================================
    # CODEC METADATA
    # ========================================================================
    @property

    def codec_id(self) -> str:
        """Codec identifier."""
        return "xwjson"
    @property

    def media_types(self) -> list[str]:
        """Supported MIME types."""
        return [
            "application/x-xwjson",           # Data files
            "application/x-xwjson-schema",     # Schema files
        ]
    @property

    def file_extensions(self) -> list[str]:
        """Supported file extensions."""
        return [
            ".xwjson",           # Data files (binary XWJSON format)
            ".schema.xwjson",    # Schema files (XWJSON schema format)
        ]
    @property

    def aliases(self) -> list[str]:
        """Alternative names."""
        return ["xwjson", "XWJSON", "xwj"]
    @property

    def codec_types(self) -> list[str]:
        """XWJSON is a binary serialization format."""
        return ["binary", "serialization"]
    @property

    def format_name(self) -> str:
        """Format name."""
        return "XWJSON"
    @property

    def is_binary_format(self) -> bool:
        """XWJSON is a binary format."""
        return True
    @property

    def supports_streaming(self) -> bool:
        """XWJSON supports streaming operations."""
        return True
    @property

    def supports_lazy_loading(self) -> bool:
        """XWJSON supports lazy loading (defer parsing until access)."""
        return True
    @property

    def supports_path_based_updates(self) -> bool:
        """XWJSON supports path-based updates (JSONPointer)."""
        return True
    @property

    def supports_atomic_path_write(self) -> bool:
        """XWJSON supports atomic path writes."""
        return True
    @property

    def supports_schema_validation(self) -> bool:
        """XWJSON supports schema validation (using xwschema)."""
        return True
    @property

    def supports_queries(self) -> bool:
        """XWJSON supports queries (using xwquery for 30+ query formats)."""
        return True
    # ========================================================================
    # CORE CODEC METHODS
    # ========================================================================

    def encode(self, value: Any, *, options: EncodeOptions | None = None) -> bytes:
        """
        Encode data to XWJSON binary format.
        Args:
            value: Data to encode
            options: Encoding options
                - metadata: Format-specific metadata (YAML anchors, XML namespaces, etc.)
                - format_code: Source format code (JSON=0x00, YAML=0x01, XML=0x02, TOML=0x03)
                - flags: Format flags (has_metadata, has_index, compressed, etc.)
                - index: Optional index structure
        Returns:
            XWJSON binary bytes
        Raises:
            SerializationError: If encoding fails
        """
        try:
            opts = options or {}
            metadata = opts.get('metadata')
            format_code = opts.get('format_code', 0x00)  # Default: JSON
            flags = opts.get('flags', 0)
            index = opts.get('index')
            file_path = opts.get('file_path')
            create_index_file = opts.get('create_index_file', False)
            return self._encoder.encode(
                data=value,
                metadata=metadata,
                format_code=format_code,
                flags=flags,
                index=index,
                file_path=file_path,
                create_index_file=create_index_file
            )
        except Exception as e:
            raise SerializationError(f"Failed to encode data to XWJSON: {e}") from e

    def decode(self, repr: bytes | str, *, options: DecodeOptions | None = None) -> Any:
        """
        Decode XWJSON binary format to data.
        Args:
            repr: XWJSON binary bytes or string
            options: Decoding options
                - return_metadata: If True, return tuple (data, metadata, index, header_info)
                - return_header: If True, include header_info in return
        Returns:
            Decoded Python data (or tuple if return_metadata=True)
        Raises:
            SerializationError: If decoding fails
        """
        try:
            if isinstance(repr, str):
                repr = repr.encode('utf-8')
            opts = options or {}
            return_metadata = opts.get('return_metadata', False)
            return_header = opts.get('return_header', False)
            file_path = opts.get('file_path')
            data, metadata, index, header_info = self._decoder.decode(repr, file_path=file_path)
            if return_metadata or return_header:
                result = {'data': data}
                if return_metadata:
                    result['metadata'] = metadata
                    result['index'] = index
                if return_header:
                    result['header'] = header_info
                return result
            else:
                return data
        except Exception as e:
            raise SerializationError(f"Failed to decode XWJSON data: {e}") from e
    # ========================================================================
    # FILE I/O METHODS (Direct sync implementation for performance)
    # ========================================================================

    def save_file(
        self,
        data: Any,
        file_path: str | Path,
        **options: Any
    ) -> None:
        """
        Save data to XWJSON file using optimized I/O.
        This is an optimized sync implementation that avoids async wrapper overhead.
        Supports fast write mode for maximum performance (matches Example Optimized speed).
        Args:
            data: Data to save
            file_path: Path to save file
            **options: Options
                - atomic: Use atomic writes (default: True for safety, False for speed)
                - fast: Enable fast write mode (direct I/O, no atomic wrapper) - default: False
                - backup: Create backup of existing file (default: True, only if atomic=True)
                - create_index_file: Create dual-file format (default: auto based on size)
        """
        file_path = Path(file_path).resolve()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        # When encryption/archive/binary_framing are used, force single-file (v1)
        pipeline_opts = any(options.get(k) for k in ('encryption', 'archive', 'binary_framing', 'key', 'password'))
        create_index_file = options.get('create_index_file', False) and not pipeline_opts
        # Encode data (pass file_path for dual-file format)
        encode_options = {**options}
        encode_options['file_path'] = file_path
        if create_index_file:
            encode_options['create_index_file'] = True
        data_bytes = self.encode(data, options=encode_options)
        # Apply serialization pipeline (encryption, archive, binary) from xwsystem
        if pipeline_opts:
            try:
                from exonware.xwsystem.io.serialization.services.pipeline import apply_pipeline_save
                enc_opts = options.get('encryption')
                if enc_opts is None and (options.get('key') is not None or options.get('password') is not None):
                    enc_opts = {
                        'key': options.get('key'),
                        'password': options.get('password'),
                        'algorithm': options.get('encryption_algorithm', 'aes256-gcm'),
                    }
                pipeline_options = {}
                if enc_opts is not None:
                    pipeline_options['encryption'] = enc_opts
                if options.get('archive') is not None:
                    pipeline_options['archive'] = options['archive']
                if options.get('binary_framing'):
                    pipeline_options['binary_framing'] = True
                if pipeline_options:
                    data_bytes = apply_pipeline_save(data_bytes, pipeline_options)
            except ImportError:
                pass
        # Atomic write (temp + rename) always used so encryption/pipeline never bypass atomic access
        from exonware.xwsystem.io.common.atomic import AtomicFileWriter
        backup = options.get('backup', True)
        # Write to temp file, then atomic rename (use binary mode for bytes)
        with AtomicFileWriter(file_path, mode='wb', backup=backup) as writer:
            writer.write(data_bytes)
        # Invalidate cache (file changed)
        self._invalidate_cache(file_path)

    async def async_save_file(
        self,
        data: Any,
        file_path: str | Path,
        **options: Any
    ) -> None:
        """
        Save data to XWJSON file using async I/O (potentially faster for parallel writes).
        Args:
            data: Data to save
            file_path: Path to save file
            **options: Options (backup, encoding, etc.)
        """
        file_path = Path(file_path).resolve()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        pipeline_opts = any(options.get(k) for k in ('encryption', 'archive', 'binary_framing', 'key', 'password'))
        create_index_file = options.get('create_index_file', False) and not pipeline_opts
        encode_options = {**options}
        encode_options['file_path'] = file_path
        if create_index_file:
            encode_options['create_index_file'] = True
        data_bytes = self.encode(data, options=encode_options)
        if pipeline_opts:
            try:
                from exonware.xwsystem.io.serialization.services.pipeline import apply_pipeline_save
                enc_opts = options.get('encryption')
                if enc_opts is None and (options.get('key') is not None or options.get('password') is not None):
                    enc_opts = {
                        'key': options.get('key'),
                        'password': options.get('password'),
                        'algorithm': options.get('encryption_algorithm', 'aes256-gcm'),
                    }
                pipeline_options = {}
                if enc_opts is not None:
                    pipeline_options['encryption'] = enc_opts
                if options.get('archive') is not None:
                    pipeline_options['archive'] = options['archive']
                if options.get('binary_framing'):
                    pipeline_options['binary_framing'] = True
                if pipeline_options:
                    data_bytes = apply_pipeline_save(data_bytes, pipeline_options)
            except ImportError:
                pass
        from exonware.xwsystem.io.stream.async_operations import async_safe_write_bytes
        backup = options.get('backup', True)
        await async_safe_write_bytes(file_path, data_bytes, backup=backup)
        self._invalidate_cache(file_path)

    def _should_cache_file(self, file_path: Path) -> bool:
        """Check if file should be cached (< 10MB)."""
        if not self._enable_cache or not self._cache_initialized:
            return False
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            return file_size_mb < self.CACHE_THRESHOLD_MB
        except (OSError, FileNotFoundError):
            return False

    def _get_cached_data(self, file_path: Path) -> Any | None:
        """
        Get cached data if valid (file hasn't changed).
        Returns None if cache miss or file modified.
        """
        if not self._enable_cache or not self._cache_initialized:
            return None
        cache_key = str(file_path)
        with self._cache_lock:
            # Check if we have cached data
            cached_data = self._file_cache.get(cache_key)
            if cached_data is None:
                return None
            # Check if file mtime matches
            if cache_key not in self._mtime_cache:
                return None
            try:
                current_mtime = file_path.stat().st_mtime
                cached_mtime = self._mtime_cache[cache_key]
                if current_mtime == cached_mtime:
                    return cached_data  # Cache HIT! ✅
                else:
                    # File changed - invalidate cache
                    del self._mtime_cache[cache_key]
                    return None
            except (OSError, FileNotFoundError):
                return None

    def _cache_file_data(self, file_path: Path, data: Any) -> None:
        """Cache file data with mtime tracking."""
        if not self._enable_cache or not self._cache_initialized:
            return
        cache_key = str(file_path)
        with self._cache_lock:
            try:
                mtime = file_path.stat().st_mtime
                self._file_cache.put(cache_key, data)
                self._mtime_cache[cache_key] = mtime
            except (OSError, FileNotFoundError):
                pass

    def _get_cached_index(self, file_path: Path, meta_file_path: Path | None = None) -> Any | None:
        """
        Get cached index/meta if valid (file hasn't changed).
        For dual-file format, checks both data file AND meta file mtimes.
        Returns None if cache miss or file modified.
        """
        if not self._enable_cache or not self._cache_initialized:
            return None
        # Determine cache key - use meta file path if provided (dual-file format)
        if meta_file_path and meta_file_path.exists():
            cache_key = f"index:{meta_file_path}"
            data_file_key = str(file_path)
            meta_file_key = str(meta_file_path)
        else:
            cache_key = f"index:{file_path}"
            data_file_key = str(file_path)
            meta_file_key = None
        with self._cache_lock:
            # Check if we have cached index
            cached_index = self._index_cache.get(cache_key)
            if cached_index is None:
                return None
            # Check if data file mtime matches
            if data_file_key not in self._mtime_cache:
                return None
            try:
                current_data_mtime = file_path.stat().st_mtime
                cached_data_mtime = self._mtime_cache[data_file_key]
                if current_data_mtime != cached_data_mtime:
                    # Data file changed - invalidate cache
                    del self._mtime_cache[data_file_key]
                    if meta_file_key and meta_file_key in self._index_mtime_cache:
                        del self._index_mtime_cache[meta_file_key]
                    return None
                # For dual-file format, also check meta file mtime
                if meta_file_key:
                    if meta_file_key not in self._index_mtime_cache:
                        return None
                    current_meta_mtime = meta_file_path.stat().st_mtime
                    cached_meta_mtime = self._index_mtime_cache[meta_file_key]
                    if current_meta_mtime != cached_meta_mtime:
                        # Meta file changed - invalidate cache
                        del self._index_mtime_cache[meta_file_key]
                        return None
                return cached_index  # Cache HIT! ✅
            except (OSError, FileNotFoundError):
                return None

    def _cache_index_data(self, file_path: Path, index_data: Any, meta_file_path: Path | None = None) -> None:
        """Cache index/meta data with mtime tracking (ALWAYS caches, regardless of file size)."""
        if not self._enable_cache or not self._cache_initialized:
            return
        # Determine cache key - use meta file path if provided (dual-file format)
        if meta_file_path and meta_file_path.exists():
            cache_key = f"index:{meta_file_path}"
            data_file_key = str(file_path)
            meta_file_key = str(meta_file_path)
        else:
            cache_key = f"index:{file_path}"
            data_file_key = str(file_path)
            meta_file_key = None
        with self._cache_lock:
            try:
                data_mtime = file_path.stat().st_mtime
                self._index_cache.put(cache_key, index_data)
                self._mtime_cache[data_file_key] = data_mtime
                # For dual-file format, also track meta file mtime
                if meta_file_key:
                    meta_mtime = meta_file_path.stat().st_mtime
                    self._index_mtime_cache[meta_file_key] = meta_mtime
            except (OSError, FileNotFoundError):
                pass
    @classmethod

    def _normalize_cache_key(cls, file_path: Path, meta_file_path: Path | None = None) -> tuple[str, str, str | None]:
        """
        Normalize cache key components to ensure consistency.
        Returns: (cache_key, data_file_key, meta_file_key)
        """
        # Always resolve to absolute paths for consistency
        file_path_resolved = file_path.resolve()
        data_file_key = str(file_path_resolved)
        if meta_file_path and meta_file_path.exists():
            meta_file_path_resolved = meta_file_path.resolve()
            meta_file_key = str(meta_file_path_resolved)
            cache_key = f"index:{meta_file_key}"
            return (cache_key, data_file_key, meta_file_key)
        # Try to find meta file ourselves (for consistency with _load_index_file logic)
        potential_meta_paths = []
        if file_path_resolved.name.endswith('.data.xwjson'):
            base_name = file_path_resolved.stem.replace('.data', '')
            potential_meta_paths.append(file_path_resolved.parent / f"{base_name}.meta.xwjson")
        elif file_path_resolved.suffix == '.xwjson':
            potential_meta_paths.append(file_path_resolved.parent / f"{file_path_resolved.stem}.meta.xwjson")
            potential_meta_paths.append(file_path_resolved.parent / f"{file_path_resolved.stem}.idx.xwjson")
        # Try each potential meta file path
        for potential_path in potential_meta_paths:
            if potential_path.exists():
                meta_file_path_resolved = potential_path.resolve()
                meta_file_key = str(meta_file_path_resolved)
                cache_key = f"index:{meta_file_key}"
                return (cache_key, data_file_key, meta_file_key)
        # Fallback to file_path-based key if no meta file found
        cache_key = f"index:{data_file_key}"
        return (cache_key, data_file_key, None)
    @classmethod

    def _get_cached_index_static(cls, file_path: Path, meta_file_path: Path | None = None) -> Any | None:
        """
        Static method to get cached index (for use by encoder/decoder).
        Returns None if cache miss or file modified.
        """
        if not cls._cache_initialized:
            return None
        # Normalize cache key components
        cache_key, data_file_key, meta_file_key = cls._normalize_cache_key(file_path, meta_file_path)
        # Get the resolved paths for mtime checking
        file_path_resolved = file_path.resolve()
        meta_file_path_resolved = None
        if meta_file_key:
            # meta_file_key is already the resolved path string
            meta_file_path_resolved = Path(meta_file_key)
        with cls._cache_lock:
            # Check if we have cached index
            cached_index = cls._index_cache.get(cache_key)
            if cached_index is None:
                return None
            # Check if data file mtime matches
            if data_file_key not in cls._mtime_cache:
                return None
            try:
                current_data_mtime = file_path_resolved.stat().st_mtime
                cached_data_mtime = cls._mtime_cache[data_file_key]
                if current_data_mtime != cached_data_mtime:
                    # Data file changed - invalidate cache
                    if data_file_key in cls._mtime_cache:
                        del cls._mtime_cache[data_file_key]
                    if meta_file_key and meta_file_key in cls._index_mtime_cache:
                        del cls._index_mtime_cache[meta_file_key]
                    return None
                # For dual-file format, also check meta file mtime
                if meta_file_key and meta_file_path_resolved:
                    if meta_file_key not in cls._index_mtime_cache:
                        return None
                    try:
                        current_meta_mtime = meta_file_path_resolved.stat().st_mtime
                        cached_meta_mtime = cls._index_mtime_cache[meta_file_key]
                        if current_meta_mtime != cached_meta_mtime:
                            # Meta file changed - invalidate cache
                            if meta_file_key in cls._index_mtime_cache:
                                del cls._index_mtime_cache[meta_file_key]
                            return None
                    except (OSError, FileNotFoundError):
                        # Meta file might have been deleted, invalidate cache
                        if meta_file_key in cls._index_mtime_cache:
                            del cls._index_mtime_cache[meta_file_key]
                        return None
                return cached_index  # Cache HIT! ✅
            except (OSError, FileNotFoundError):
                return None
    @classmethod

    def _cache_index_data_static(cls, file_path: Path, index_data: Any, meta_file_path: Path | None = None) -> None:
        """
        Static method to cache index/meta data (for use by encoder/decoder).
        ALWAYS caches, regardless of file size.
        """
        if not cls._cache_initialized:
            return
        # Normalize cache key components (use same logic as _get_cached_index_static)
        cache_key, data_file_key, meta_file_key = cls._normalize_cache_key(file_path, meta_file_path)
        # Get resolved paths for mtime tracking
        file_path_resolved = file_path.resolve()
        meta_file_path_resolved = None
        if meta_file_key:
            meta_file_path_resolved = Path(meta_file_key).resolve()
        with cls._cache_lock:
            try:
                data_mtime = file_path_resolved.stat().st_mtime
                cls._index_cache.put(cache_key, index_data)
                cls._mtime_cache[data_file_key] = data_mtime
                # For dual-file format, also track meta file mtime
                if meta_file_key and meta_file_path_resolved:
                    meta_mtime = meta_file_path_resolved.stat().st_mtime
                    cls._index_mtime_cache[meta_file_key] = meta_mtime
            except (OSError, FileNotFoundError):
                pass

    def _get_meta_file_path(self, file_path: Path) -> Path | None:
        """
        Get meta file path for dual-file format, if it exists.
        Returns None if no meta file exists (single-file format).
        """
        # Determine meta/index file path (same logic as encoder._load_index_file)
        if file_path.name.endswith('.data.xwjson'):
            # Minimal format: *.data.xwjson -> *.meta.xwjson
            base_name = file_path.stem.replace('.data', '')
            meta_file_path = file_path.parent / f"{base_name}.meta.xwjson"
        elif file_path.suffix == '.xwjson':
            # Try minimal format first: data.xwjson -> data.meta.xwjson
            meta_file_path = file_path.parent / f"{file_path.stem}.meta.xwjson"
            if not meta_file_path.exists():
                # Fallback to old format: data.xwjson -> data.idx.xwjson
                meta_file_path = file_path.parent / f"{file_path.stem}.idx.xwjson"
        else:
            meta_file_path = file_path.parent / f"{file_path.name}.meta.xwjson"
            if not meta_file_path.exists():
                meta_file_path = file_path.parent / f"{file_path.name}.idx.xwjson"
        return meta_file_path if meta_file_path.exists() else None

    def _invalidate_cache(self, file_path: Path) -> None:
        """Invalidate cache for a file (called after save). Invalidates both file cache and index cache."""
        if not self._enable_cache or not self._cache_initialized:
            return
        # Fast path: Use resolved path for consistent cache keys
        file_path_resolved = file_path.resolve()
        cache_key = str(file_path_resolved)
        with self._cache_lock:
            # Invalidate file cache (for small files) - fast dict operation
            if cache_key in self._mtime_cache:
                del self._mtime_cache[cache_key]
            # Invalidate index cache - use normalized key for consistency
            index_cache_key, data_file_key, meta_file_key = self._normalize_cache_key(file_path_resolved)
            # Pop from index cache if exists (fast operation)
            if hasattr(self._index_cache, 'pop'):
                try:
                    self._index_cache.pop(index_cache_key, None)
                except (KeyError, AttributeError):
                    pass
            # Also invalidate header_index cache key if exists
            header_index_cache_key = f"header_index:{cache_key}"
            if hasattr(self._index_cache, 'pop'):
                try:
                    self._index_cache.pop(header_index_cache_key, None)
                except (KeyError, AttributeError):
                    pass
            # Invalidate meta file mtime cache if dual-file format
            if meta_file_key and meta_file_key in self._index_mtime_cache:
                del self._index_mtime_cache[meta_file_key]

    def load_file(
        self,
        file_path: str | Path,
        **options: Any
    ) -> Any:
        """
        Load data from XWJSON file with intelligent caching.
        Features:
        - Automatic caching for small files (< 10MB)
        - Cache invalidation on file modification
        - Memory-mapped I/O for large files (> 1MB)
        - Optimized for repeated reads
        Args:
            file_path: Path to load file from
            **options: Options
        Returns:
            Decoded data
        """
        file_path = Path(file_path).resolve()
        # Check if minimal format exists (data.data.xwjson)
        if file_path.suffix == '.xwjson' and not file_path.name.endswith('.data.xwjson'):
            minimal_path = file_path.parent / f"{file_path.stem}.data.xwjson"
            if minimal_path.exists():
                # Use minimal format (fastest - pure MessagePack array)
                file_path = minimal_path
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        # FAST PATH: Check cache first (for small files)
        if self._should_cache_file(file_path):
            cached_data = self._get_cached_data(file_path)
            if cached_data is not None:
                return cached_data  # Cache HIT! No I/O needed! ✅
        # SLOW PATH: Load from disk
        file_size = file_path.stat().st_size
        use_mmap = file_size > 1024 * 1024  # Use mmap for files > 1MB
        pipeline_opts = any(options.get(k) for k in ('encryption', 'archive', 'binary_framing', 'key', 'password'))
        xwje_magic = b'XWJE'
        if use_mmap and not pipeline_opts:
            # Use mmap-based decoding (faster for large files) when no pipeline
            data, metadata, index, header_info = self._decoder.decode_file_mmap(file_path)
        else:
            with file_path.open('rb') as f:
                data_bytes = f.read()
            need_pipeline = pipeline_opts or (len(data_bytes) >= 4 and data_bytes[:4] == xwje_magic)
            if need_pipeline:
                try:
                    from exonware.xwsystem.io.serialization.services.pipeline import apply_pipeline_load
                    enc_opts = options.get('encryption')
                    if enc_opts is None and (options.get('key') is not None or options.get('password') is not None):
                        enc_opts = {
                            'key': options.get('key'),
                            'password': options.get('password'),
                        }
                    pipeline_options = {}
                    if enc_opts is not None:
                        pipeline_options['encryption'] = enc_opts
                    if options.get('archive') is not None:
                        pipeline_options['archive'] = options['archive']
                    if options.get('binary_framing'):
                        pipeline_options['binary_framing'] = True
                    if pipeline_options or enc_opts is not None:
                        data_bytes = apply_pipeline_load(data_bytes, pipeline_options or options)
                except ImportError:
                    pass
            decode_options = {**options, 'file_path': file_path}
            data = self.decode(data_bytes, options=decode_options)
        # Cache the data if file is small
        if self._should_cache_file(file_path):
            self._cache_file_data(file_path, data)
        return data
    # ========================================================================
    # SYNC WRAPPER METHODS (Matching json.py and jsonlines.py APIs)
    # ========================================================================

    def _get_ops(self):
        """Get or create XWJSONDataOperations instance."""
        if self._ops is None:
            # Lazy import to avoid circular dependency
            # serializer.py is in: xwjson/formats/binary/xwjson/
            # xwjson_ops.py is in: xwjson/operations/
            # So we need to go up 4 levels: .../.../.../.../operations/xwjson_ops
            from exonware.xwjson.operations.xwjson_ops import XWJSONDataOperations
            self._ops = XWJSONDataOperations(serializer=self)
        return self._ops

    def _run_async(self, coro):
        """Run async coroutine synchronously."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, try nest_asyncio
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                    return loop.run_until_complete(coro)
                except ImportError:
                    # Fallback: create new thread with new event loop
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, coro)
                        return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop, create new one
            return asyncio.run(coro)

    def atomic_update_path(
        self,
        file_path: str | Path,
        path: str,
        value: Any,
        **options
    ) -> None:
        """
        Atomically update a single path in an XWJSON file using JSONPointer.
        Sync wrapper for async write_path operation.
        Args:
            file_path: Path to the XWJSON file
            path: JSONPointer path (e.g., "/users/0/name")
            value: Value to set at the specified path
            **options: Options (backup=True, etc.)
        Raises:
            SerializationError: If update fails
            ValueError: If path is invalid
            KeyError: If path doesn't exist
        """
        return self._run_async(self._get_ops().write_path(file_path, path, value, **options))

    def atomic_read_path(
        self,
        file_path: str | Path,
        path: str,
        **options
    ) -> Any:
        """
        Read a single path from an XWJSON file using JSONPointer.
        Sync wrapper for async read_path operation.
        Args:
            file_path: Path to the XWJSON file
            path: JSONPointer path (e.g., "/users/0/name")
            **options: Options
        Returns:
            Value at the specified path
        Raises:
            SerializationError: If read fails
            KeyError: If path doesn't exist
        """
        return self._run_async(self._get_ops().read_path(file_path, path))

    def query(
        self,
        file_path: str | Path,
        query_expr: str,
        **options
    ) -> Any:
        """
        Query XWJSON file using JSONPath expression.
        Sync wrapper for async query operation.
        Args:
            file_path: Path to the XWJSON file
            query_expr: JSONPath expression (e.g., "$.users[*].name")
            **options: Query options
        Returns:
            Query results (list of matching values)
        Raises:
            SerializationError: If query fails
            ValueError: If query expression is invalid
        """
        return self._run_async(self._get_ops().query(file_path, query_expr, **options))

    def stream_read_record(
        self,
        file_path: str | Path,
        match: Callable,
        projection: list[Any] | None = None,
        **options: Any,
    ) -> Any:
        """
        Stream-style read of a single logical record from an XWJSON file.
        Sync wrapper for async operation. For XWJSON, this loads the file and searches.
        Args:
            file_path: Path to the XWJSON file
            match: Function that returns True for matching records
            projection: Optional projection fields
            **options: Options
        Returns:
            First matching record
        Raises:
            KeyError: If no matching record found
        """
        data = self._run_async(self._get_ops().atomic_read(file_path))
        # If data is a list, search through it
        if isinstance(data, list):
            for record in data:
                if match(record):
                    if projection:
                        return {k: record.get(k) for k in projection if k in record}
                    return record
        elif isinstance(data, dict):
            if match(data):
                if projection:
                    return {k: data.get(k) for k in projection if k in data}
                return data
        raise KeyError("No matching record found")

    def stream_update_record(
        self,
        file_path: str | Path,
        match: Callable,
        updater: Callable,
        *,
        atomic: bool = True,
        **options: Any,
    ) -> int:
        """
        Stream-style update of logical records in an XWJSON file.
        Sync wrapper for async operation.
        Args:
            file_path: Path to the XWJSON file
            match: Function that returns True for matching records
            updater: Function that updates matching records
            atomic: Whether to use atomic writes (default: True)
            **options: Options
        Returns:
            Number of records updated
        """
        data = self._run_async(self._get_ops().atomic_read(file_path))
        updated = 0
        # Update matching records
        if isinstance(data, list):
            for i, record in enumerate(data):
                if match(record):
                    data[i] = updater(record)
                    updated += 1
        elif isinstance(data, dict):
            if match(data):
                data = updater(data)
                updated = 1
        # Write back atomically
        if updated > 0:
            self._run_async(self._get_ops().atomic_write(file_path, data))
        return updated

    def get_record_page(
        self,
        file_path: str | Path,
        page_number: int,
        page_size: int,
        **options: Any,
    ) -> list[Any]:
        """
        Retrieve a logical page of records from an XWJSON file.
        Optimized sync implementation that uses ops cache to avoid async wrapper overhead.
        Automatically handles common data structures:
        - If data is a list, paginates directly
        - If data is a dict with "records" key, paginates records list
        - Otherwise, uses path from options or defaults to "/records"
        Args:
            file_path: Path to the XWJSON file
            page_number: Page number (1-based)
            page_size: Number of records per page
            **options: Options (path: optional JSONPointer path)
        Returns:
            List of records in the page
        """
        file_path = Path(file_path).resolve()
        ops = self._get_ops()
        # Auto-detect path if not provided
        path = options.get('path')
        if path is None:
            # Check ops file cache first (fast path - avoids file I/O and decoding)
            if file_path in ops._file_cache:
                cached_data, cache_time = ops._file_cache[file_path]
                import time
                if time.time() - cache_time < ops._cache_max_age:
                    data = cached_data
                else:
                    # Cache expired, reload
                    data = self.load_file(file_path, **options)
                    ops._file_cache[file_path] = (data, time.time())
            else:
                # Not in cache, load and cache it
                data = self.load_file(file_path, **options)
                import time
                ops._file_cache[file_path] = (data, time.time())
            # Handle data structure
            if isinstance(data, list):
                # Data is already a list, paginate directly
                start = (page_number - 1) * page_size
                end = start + page_size
                return data[start:end]
            elif isinstance(data, dict) and "records" in data:
                # Data is wrapped in dict with "records" key
                records = data["records"]
                if isinstance(records, list):
                    start = (page_number - 1) * page_size
                    end = start + page_size
                    return records[start:end]
                path = "/records"
            else:
                # Default to "/records" for common case
                path = "/records"
        # If path is needed, use ops with async wrapper (unavoidable for path resolution)
        if path:
            return self._run_async(ops.read_page(file_path, page_number, page_size, path=path, **{k: v for k, v in options.items() if k != 'path'}))
        # Should not reach here, but fallback
        return []

    def get_record_by_id(
        self,
        file_path: str | Path,
        id_value: Any,
        *,
        id_field: str = "id",
        **options: Any,
    ) -> Any:
        """
        Retrieve a logical record by identifier from an XWJSON file.
        Sync wrapper for async operation.
        Args:
            file_path: Path to the XWJSON file
            id_value: ID value to search for
            id_field: Field name containing the ID (default: "id")
            **options: Options
        Returns:
            Record with matching ID
        Raises:
            KeyError: If record not found
        """
        data = self._run_async(self._get_ops().atomic_read(file_path))
        # Search for record
        if isinstance(data, list):
            for record in data:
                if isinstance(record, dict) and record.get(id_field) == id_value:
                    return record
        elif isinstance(data, dict):
            if data.get(id_field) == id_value:
                return data
        raise KeyError(f"Record with {id_field}={id_value!r} not found")
