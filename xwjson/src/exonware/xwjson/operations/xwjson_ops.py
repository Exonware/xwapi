#exonware/xwjson/src/exonware/xwjson/operations/xwjson_ops.py
"""
XWJSON Data Operations
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 2025-01-XX
Data operations for XWJSON: streaming, indexing, paging, path operations.
Uses xwnode for graph operations, dependency resolution, topological sort.
Uses xwschema for schema validation, fast compiled schemas.
Priority 1 (Security): Safe operations, path validation, input validation
Priority 2 (Usability): Clear APIs, helpful error messages
Priority 3 (Maintainability): Clean code, design patterns
Priority 4 (Performance): Fast operations, memory efficiency, scalability
Priority 5 (Extensibility): Plugin system, hooks, customization points
"""

from typing import Any
from pathlib import Path
import asyncio
# xwsystem is a direct dependency (every XW library extends xwsystem)
from exonware.xwsystem.io.errors import SerializationError
# xwquery is optional: imported lazily where used (query_execute, query_advanced)
# xwnode for optimized LRU caching (now faster than dict!)
from exonware.xwnode import XWNode
from exonware.xwnode.defs import NodeMode
# Import XWJSON components
from ..formats.binary.xwjson.serializer import XWJSONSerializer
from ..formats.binary.xwjson.dependency_graph import XWJSONDependencyGraph
from ..formats.binary.xwjson.schema import XWJSONSchemaValidator
from ..formats.binary.xwjson.encoder import FLAG_STREAMING


from collections.abc import AsyncIterator
class XWJSONDataOperations:
    """
    Data operations for XWJSON files.
    Uses xwnode for graph operations, dependency resolution, topological sort.
    Uses xwschema for schema validation, fast compiled schemas.
    Features:
    - Streaming read/update
    - Parallel indexing
    - Record paging
    - Path-based operations (JSONPointer)
    - Query support (JSONPath)
    - Binary-first parsing
    - Memory-mapped I/O for large files
    - Incremental/streaming parsing
    - Partial updates (RFC 6902 JSON Patch)
    - Path caching (LRU cache)
    - Fast path for small files
    - Object pooling
    - JSON index (like SQL Server 2025)
    """

    def __init__(self, serializer: XWJSONSerializer | None = None):
        """
        Initialize data operations.
        Args:
            serializer: XWJSONSerializer instance (creates new if None)
        """
        self._serializer = serializer or XWJSONSerializer()
        self._dependency_graph = XWJSONDependencyGraph()
        self._schema_validator: XWJSONSchemaValidator | None = None
        # Cache for recently read files (file path -> (data, timestamp))
        # Uses XWNode LRU_CACHE with xwsystem optimization (15-19% faster than dict!)
        # Stores (data, timestamp) tuples for TTL checking
        self._file_cache: XWNode = XWNode(mode=NodeMode.LRU_CACHE, max_size=10)
        # Cache for resolved paths (file_path:path -> (resolved_list, timestamp))
        # Uses XWNode LRU_CACHE for optimal performance
        # This dramatically speeds up paging on same file/path combination
        # Equivalent to JSONL's line_offsets index - instant access to cached list
        self._path_cache: XWNode = XWNode(mode=NodeMode.LRU_CACHE, max_size=50)
        self._cache_max_age = 30.0  # Cache for 30 seconds (extended for performance)
    # ========================================================================
    # READ OPERATIONS
    # ========================================================================

    async def atomic_read(self, file_path: str | Path, use_cache: bool = True) -> Any:
        """
        Atomic file read with transaction support.
        Args:
            file_path: Path to XWJSON file
            use_cache: Whether to use file cache (default: True)
        Returns:
            Decoded data
        """
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise SerializationError(f"File not found: {file_path}")
        # Check cache first (critical for performance - avoids repeated file I/O)
        # Uses XWNode LRU_CACHE (optimized with xwsystem cache - 15-19% faster than dict!)
        if use_cache:
            import time
            cache_key = str(file_path)
            cached_value = self._file_cache.get_value(cache_key)
            if cached_value is not None:
                cached_data, cache_time = cached_value
                # Extended cache age for performance (30 seconds for integration tests)
                if time.time() - cache_time < self._cache_max_age:
                    return cached_data
                # Cache expired, remove it
                self._file_cache.delete(cache_key)
        # Use memory-mapped I/O for large files (faster than regular file I/O)
        file_size = file_path.stat().st_size
        use_mmap = file_size > 1024 * 1024  # Use mmap for files > 1MB
        if use_mmap:
            # Use mmap-based decoding (faster for large files)
            data, metadata, index, header_info = self._serializer._decoder.decode_file_mmap(file_path)
        else:
            # Regular async file I/O for small files
            import aiofiles
            async with aiofiles.open(file_path, 'rb') as f:
                data_bytes = await f.read()
            data, metadata, index, header_info = self._serializer._decoder.decode(data_bytes)
        # Cache the result (important for paging operations that read same file multiple times)
        # Uses XWNode LRU_CACHE (automatic LRU eviction, no manual size management needed!)
        if use_cache:
            import time
            cache_key = str(file_path)
            self._file_cache.put(cache_key, (data, time.time()))
            # LRU eviction is automatic (no manual size management needed)
        return data

    async def read_path(
        self,
        file_path: str | Path,
        path: str
    ) -> Any:
        """
        Read specific path (JSONPointer).
        Args:
            file_path: Path to XWJSON file
            path: JSONPointer path (e.g., "/users/0/name")
        Returns:
            Value at path
        """
        data = await self.atomic_read(file_path)
        # Navigate to path
        from jsonpointer import resolve_pointer
        try:
            return resolve_pointer(data, path)
        except Exception as e:
            raise SerializationError(f"Failed to read path {path}: {e}") from e

    async def read_page(
        self,
        file_path: str | Path,
        page_number: int = 1,
        page_size: int = 100,
        path: str | None = None,
        data: Any | None = None
    ) -> list[Any]:
        """
        Read page of records (indexed) - optimized with path-level caching.
        Performance optimization: Uses dual-level caching:
        1. File-level cache: Avoids re-reading and re-decoding files
        2. Path-level cache: Avoids re-resolving paths for same file/path combination
        Args:
            file_path: Path to XWJSON file
            page_number: Page number (1-based)
            page_size: Number of records per page
            path: Optional JSON Pointer path to list to paginate (e.g., "/users")
            data: Optional pre-loaded data (avoids file read if provided)
        Returns:
            list of records in page
        """
        import time
        file_path = Path(file_path).resolve()
        # Performance optimization: Check path-level cache first (avoids path resolution AND file I/O)
        # Uses XWNode LRU_CACHE (optimized with xwsystem cache - 15-19% faster than dict!)
        # This works even when data is passed in (for subsequent calls with same file/path)
        path_cache_key = None
        if path:
            path_cache_key = f"{file_path}:{path}"
            cached_value = self._path_cache.get_value(path_cache_key)
            if cached_value is not None:
                cached_list, cache_time = cached_value
                if time.time() - cache_time < self._cache_max_age:
                    # Use cached resolved list directly (fastest path - just list slicing)
                    if isinstance(cached_list, list):
                        start = (page_number - 1) * page_size
                        end = start + page_size
                        return cached_list[start:end]
        # Use provided data or read from file (with file-level cache)
        if data is None:
            # Optimization: For cold paging with streaming format, use partial decoding
            # Check if file supports streaming format (record-level encoding)
            try:
                header_info, index = self._serializer._decoder.read_header_and_index(file_path)
                # Check that index is a dict (not bytes or None) before checking for keys
                if (header_info['flags'] & FLAG_STREAMING) and index and isinstance(index, dict) and 'record_offsets' in index:
                    # Use partial decoding for cold paging (only decode needed records)
                    start_record = (page_number - 1) * page_size
                    end_record = start_record + page_size
                    record_count = len(index.get('record_offsets', []))
                    if start_record < record_count:
                        # Decode only the needed page range
                        records = self._serializer._decoder.decode_partial(file_path, start_record, min(end_record, record_count))
                        # Handle path if specified
                        if path:
                            # For streaming format with path, we need to reconstruct structure
                            wrapper = index.get('wrapper')
                            if wrapper:
                                data = {**wrapper, 'records': records}
                            else:
                                data = records
                            # Resolve path
                            from jsonpointer import resolve_pointer
                            target = resolve_pointer(data, path)
                            if isinstance(target, list):
                                return target[:page_size]  # Already the right size
                            else:
                                raise SerializationError(f"Path {path} does not point to a list")
                        else:
                            # No path, return records directly
                            return records
            except (SerializationError, FileNotFoundError, ValueError):
                # Fallback: Use regular full decode (for non-streaming format or errors)
                pass
            # Regular full decode (for non-streaming format or when partial decode fails)
            data = await self.atomic_read(file_path, use_cache=True)
        # If path is specified, navigate to that list
        if path:
            from jsonpointer import resolve_pointer
            try:
                target = resolve_pointer(data, path)
                if isinstance(target, list):
                    # Cache the resolved list for future page reads (critical performance optimization)
                    # This avoids re-resolving path for subsequent page requests on same file/path
                    if path_cache_key is None:
                        path_cache_key = f"{file_path}:{path}"
                    # Use XWNode LRU_CACHE (automatic LRU eviction, no manual size management needed!)
                    self._path_cache.put(path_cache_key, (target, time.time()))
                    # LRU eviction is automatic (no manual size management needed)
                    data = target
                else:
                    raise SerializationError(f"Path {path} does not point to a list")
            except Exception as e:
                raise SerializationError(f"Failed to resolve path {path}: {e}") from e
        # If data is a list, paginate it (fast operation - just slicing)
        if isinstance(data, list):
            start = (page_number - 1) * page_size
            end = start + page_size
            return data[start:end]
        elif isinstance(data, dict) and "records" in data and path is None:
            # Auto-handle common case: dict with "records" key, no path specified
            records = data["records"]
            if isinstance(records, list):
                start = (page_number - 1) * page_size
                end = start + page_size
                return records[start:end]
        # For non-list data, return single page with data (only for page 1)
        if page_number == 1:
            return [data]
        else:
            return []

    async def read_stream(
        self,
        file_path: str | Path
    ) -> AsyncIterator[Any]:
        """
        Stream read records.
        Args:
            file_path: Path to XWJSON file
        Yields:
            Records one by one
        """
        data = await self.atomic_read(file_path)
        if isinstance(data, list):
            for record in data:
                yield record
        else:
            yield data
    # ========================================================================
    # WRITE OPERATIONS
    # ========================================================================

    async def atomic_write(
        self,
        file_path: str | Path,
        data: Any
    ) -> None:
        """
        Atomic file write with transaction support.
        Args:
            file_path: Path to XWJSON file
            data: Data to write
        """
        file_path = Path(file_path).resolve()
        # Check if file exists BEFORE write (for cache invalidation optimization)
        file_existed = file_path.exists()
        # Invalidate both file cache and path cache for this file (critical for consistency)
        # Invalidate file cache (XWNode LRU_CACHE)
        cache_key = str(file_path)
        self._file_cache.delete(cache_key)
        # Invalidate all path caches for this file (XWNode LRU_CACHE)
        # Iterate strategy keys directly (XWNode facade doesn't expose keys() directly)
        path_cache_keys_to_remove = [
            k for k in self._path_cache._strategy.keys() 
            if k.startswith(str(file_path) + ":")
        ]
        for key in path_cache_keys_to_remove:
            self._path_cache.delete(key)
        # Only invalidate serializer's index cache if file existed before write (new files don't need invalidation)
        # This optimization avoids cache operations for new files, significantly improving write performance
        if file_existed and hasattr(self._serializer, '_invalidate_cache'):
            try:
                self._serializer._invalidate_cache(file_path)
            except Exception:
                pass  # Don't fail writes if cache invalidation fails
        # Encode data
        data_bytes = self._serializer.encode(data)
        # Write file asynchronously (atomic: write to temp, then rename)
        # Use aiofiles directly for maximum performance (faster than going through async_save_file)
        import aiofiles
        import uuid
        # Use unique temp file name to avoid conflicts with concurrent operations
        temp_path = file_path.parent / f"{file_path.name}.{uuid.uuid4().hex[:8]}.tmp"
        async with aiofiles.open(temp_path, 'wb') as f:
            await f.write(data_bytes)
        # Atomic rename (with retry for Windows file locking)
        import asyncio
        max_retries = 5
        for attempt in range(max_retries):
            try:
                temp_path.replace(file_path)
                break
            except (PermissionError, OSError, FileNotFoundError) as e:
                if attempt == max_retries - 1:
                    # Clean up temp file if it still exists
                    if temp_path.exists():
                        try:
                            temp_path.unlink()
                        except Exception:
                            pass
                    raise
                await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff (async to allow other coroutines to complete)

    async def write_path(
        self,
        file_path: str | Path,
        path: str,
        value: Any
    ) -> None:
        """
        Write to specific path (JSONPointer).
        Creates missing parent segments as dicts so nested paths work.
        Args:
            file_path: Path to XWJSON file
            path: JSONPointer path
            value: Value to write
        """
        # Read current data
        data = await self.atomic_read(file_path)
        from jsonpointer import set_pointer, JsonPointer, JsonPointerException
        path_stripped = path.rstrip("/")
        if path_stripped and path_stripped.startswith("/"):
            parts = path_stripped.split("/")[1:]  # e.g. ['level1','level2','level3','value']
            for i in range(1, len(parts)):  # parent prefixes only
                prefix = "/" + "/".join(parts[:i])
                try:
                    JsonPointer(prefix).resolve(data)
                except (JsonPointerException, KeyError, TypeError):
                    try:
                        set_pointer(data, prefix, {})
                    except Exception as e:
                        raise SerializationError(
                            f"Cannot create path {path}: segment {prefix} not a dict ({e})"
                        ) from e
        try:
            set_pointer(data, path, value)
        except Exception as e:
            raise SerializationError(f"Failed to write path {path}: {e}") from e
        await self.atomic_write(file_path, data)

    async def append(
        self,
        file_path: str | Path,
        record: Any
    ) -> None:
        """
        Append record (O(1) with append-only log).
        Args:
            file_path: Path to XWJSON file
            record: Record to append
        """
        # Read current data
        data = await self.atomic_read(file_path)
        # Append to list
        if isinstance(data, list):
            data.append(record)
        else:
            data = [data, record]
        # Write back
        await self.atomic_write(file_path, data)
    # ========================================================================
    # UPDATE OPERATIONS
    # ========================================================================

    async def atomic_update(
        self,
        file_path: str | Path,
        updates: dict[str, Any]
    ) -> None:
        """
        Atomic update with transaction support.
        Args:
            file_path: Path to XWJSON file
            updates: Dictionary of path -> value updates
        """
        # Read current data
        data = await self.atomic_read(file_path)
        # Apply updates
        from jsonpointer import set_pointer
        for path, value in updates.items():
            try:
                set_pointer(data, path, value)
            except Exception as e:
                raise SerializationError(f"Failed to update path {path}: {e}") from e
        # Write back
        await self.atomic_write(file_path, data)

    async def partial_update(
        self,
        file_path: str | Path,
        patch: list[dict[str, Any]]
    ) -> None:
        """
        Partial update (RFC 6902 JSON Patch).
        Args:
            file_path: Path to XWJSON file
            patch: JSON Patch operations
        """
        # Read current data
        data = await self.atomic_read(file_path)
        # Apply patch
        try:
            from jsonpatch import apply_patch
            data = apply_patch(data, patch)
        except Exception as e:
            raise SerializationError(f"Failed to apply patch: {e}") from e
        # Write back
        await self.atomic_write(file_path, data)
    # ========================================================================
    # DELETE OPERATIONS
    # ========================================================================

    async def atomic_delete(self, file_path: str | Path) -> None:
        """
        Atomic delete with transaction support.
        Args:
            file_path: Path to XWJSON file
        """
        file_path = Path(file_path)
        if file_path.exists():
            file_path.unlink()

    async def delete_path(
        self,
        file_path: str | Path,
        path: str
    ) -> None:
        """
        Delete specific path (JSONPointer).
        Args:
            file_path: Path to XWJSON file
            path: JSONPointer path to delete
        """
        # Read current data
        data = await self.atomic_read(file_path)
        # Delete path manually (jsonpointer doesn't have remove_pointer)
        from jsonpointer import resolve_pointer
        try:
            # Navigate to parent and delete the key
            if path == "":
                # Delete root - clear data
                data = {}
            else:
                # Split path into parent and key
                parts = path.strip('/').split('/')
                if len(parts) == 1:
                    # Top-level key
                    if parts[0] in data:
                        del data[parts[0]]
                else:
                    # Nested path
                    parent_path = '/' + '/'.join(parts[:-1])
                    key = parts[-1]
                    parent = resolve_pointer(data, parent_path)
                    if isinstance(parent, dict):
                        if key in parent:
                            del parent[key]
                        # else: key already missing (idempotent no-op)
                    elif isinstance(parent, list):
                        try:
                            index = int(key)
                            if 0 <= index < len(parent):
                                parent.pop(index)
                        except (ValueError, IndexError):
                            raise SerializationError(f"Invalid array index in path: {path}")
                    else:
                        raise SerializationError(f"Cannot delete from {type(parent).__name__} at {path}")
        except Exception as e:
            raise SerializationError(f"Failed to delete path {path}: {e}") from e
        # Write back
        await self.atomic_write(file_path, data)
    # ========================================================================
    # QUERY OPERATIONS (with xwquery integration)
    # ========================================================================

    async def query(
        self,
        file_path: str | Path,
        query: str,
        query_format: str | None = None,
        use_xwquery: bool = True
    ) -> list[Any]:
        """
        Query XWJSON file using xwquery (universal query language) or JSONPath.
        Supports multiple query formats via xwquery:
        - SQL: "SELECT * FROM users WHERE age > 25"
        - JSONPath: "$.users[*].name"
        - JMESPath: "users[?age > `25`].name"
        - Cypher: "MATCH (u:User) WHERE u.age > 25 RETURN u"
        - And 30+ more formats via xwquery
        Falls back to jsonpath-ng if xwquery not available.
        Args:
            file_path: Path to XWJSON file
            query: Query string (any xwquery-supported format)
            query_format: Explicit query format (optional, auto-detected if None)
            use_xwquery: Whether to use xwquery (True) or jsonpath-ng (False)
        Returns:
            list of matching values
        Examples:
            >>> # SQL query
            >>> results = await ops.query("data.xwjson", "SELECT name FROM users WHERE age > 25")
            >>> 
            >>> # JSONPath query
            >>> results = await ops.query("data.xwjson", "$.users[*].name")
            >>> 
            >>> # JMESPath query
            >>> results = await ops.query("data.xwjson", "users[?age > `25`].name", query_format="jmespath")
        """
        data = await self.atomic_read(file_path)
        # Store original query for error messages
        original_query = query
        # Detect JSONPath filter syntax [?(@.expression)] and convert to JMESPath
        # JSONPath filter syntax is: $.users[?(@.age > 30)].name
        # JMESPath filter syntax is: users[?age > `30`].name
        import re
        jsonpath_filter_pattern = r'\[\?\(@\.([^)]+)\)\]'
        has_jsonpath_filter = bool(re.search(jsonpath_filter_pattern, query))
        # Convert JSONPath filter syntax to JMESPath
        if has_jsonpath_filter and query_format is None:
            # Extract the filter expression and convert @.property to property
            def convert_filter(match):
                expr = match.group(1)  # Get the expression inside @.(...)
                # Replace @.property with property (JMESPath doesn't use @)
                expr = re.sub(r'@\.', '', expr)
                # Convert literals to JMESPath format:
                # - String literals: "string" -> 'string' (avoid deprecated backtick strings)
                # - Numeric literals in comparisons: use backticks
                # First handle string literals
                expr = re.sub(r'(["\'])([^"\']+)\1', r"'\2'", expr)
                # Then handle numeric literals in comparisons (JMESPath needs backticks for all literals)
                # Pattern: operator number -> operator `number`
                expr = re.sub(r'([><=!]+)\s*(\d+\.?\d*)', r'\1 `\2`', expr)
                return f'[?{expr}]'
            # Convert the entire query
            converted_query = re.sub(jsonpath_filter_pattern, convert_filter, query)
            # Remove leading $. if present (JMESPath doesn't use $)
            converted_query = re.sub(r'^\$\.', '', converted_query)
            # Use JMESPath format (use jmespath library directly for better support)
            query = converted_query
            query_format = "jmespath"
            # Use jmespath library directly for JMESPath queries (xwquery's JMESPath support is incomplete)
            try:
                import jmespath
                results = jmespath.search(query, data)
                # jmespath.search returns the result directly, normalize to list
                if results is None:
                    return []
                return results if isinstance(results, list) else [results]
            except ImportError:
                # jmespath not available, try xwquery as fallback
                pass
            except Exception as jmespath_error:
                # jmespath failed, try xwquery as fallback
                import warnings
                warnings.warn(f"jmespath library failed, falling back to xwquery: {jmespath_error}")
        # Try xwquery first (more powerful, supports 30+ query formats)
        if use_xwquery:
            try:
                from exonware.xwquery import XWQuery
                # Execute query using xwquery (auto-detects format or uses specified format)
                result = XWQuery.execute(
                    query,
                    data,
                    format=query_format,
                    auto_detect=query_format is None
                )
                # Check if query was successful
                if hasattr(result, 'success') and not result.success:
                    # Query failed - check if it's a JSONPath filter syntax issue
                    if has_jsonpath_filter:
                        raise ValueError(
                            f"xwquery execution failed for JSONPath filter syntax: {getattr(result, 'error', 'Unknown error')}. "
                            f"JSONPath filter syntax [?(@.expression)] requires xwquery with JSONPath support."
                        )
                    # For other failures, try to fall back to jsonpath-ng if possible
                    raise ValueError(f"xwquery execution failed: {getattr(result, 'error', 'Unknown error')}")
                # Extract results from ExecutionResult
                if hasattr(result, 'results') and result.results is not None:
                    return result.results if isinstance(result.results, list) else [result.results]
                elif hasattr(result, 'data') and result.data is not None:
                    return result.data if isinstance(result.data, list) else [result.data]
                else:
                    # No results - check if JSONPath filter syntax was used
                    if has_jsonpath_filter:
                        raise ValueError(
                            "xwquery returned no results for JSONPath filter syntax. "
                            "JSONPath filter syntax [?(@.expression)] requires xwquery with JSONPath support."
                        )
                    # For other cases, try to fall back to jsonpath-ng if possible
                    raise ValueError("xwquery returned no results")
            except ImportError:
                # xwquery is optional. Fall back to jsonpath-ng for JSONPath queries.
                import warnings
                warnings.warn(
                    "xwquery not installed; falling back to jsonpath-ng for query execution"
                )
            except (ValueError, Exception) as e:
                # xwquery failed - check if JSONPath filter syntax was used
                if has_jsonpath_filter:
                    # Already tried jmespath library above, xwquery also failed
                    raise SerializationError(
                        f"Failed to execute JSONPath filter query '{original_query}': {e}. "
                        f"Both jmespath library and xwquery failed. "
                        f"JSONPath filter syntax [?(@.expression)] requires jmespath library: pip install jmespath"
                    ) from e
                # For other failures, log warning and try to fall back to jsonpath-ng
                import warnings
                warnings.warn(f"xwquery execution failed, falling back to jsonpath-ng: {e}")
        # Fallback to jsonpath-ng (JSONPath only, no filter syntax)
        if has_jsonpath_filter:
            # Should have been handled by jmespath library above
            raise SerializationError(
                f"JSONPath filter syntax [?(@.expression)] in query '{original_query}' is not supported by jsonpath-ng. "
                f"Install jmespath library for filter syntax support: pip install jmespath"
            )
        try:
            from jsonpath_ng import parse
            jsonpath_expr = parse(query)
            matches = [match.value for match in jsonpath_expr.find(data)]
            return matches
        except Exception as e:
            raise SerializationError(
                f"Failed to execute query '{query}': {e}. "
                f"Install xwquery for 30+ query format support: pip install exonware-xwquery"
            ) from e

    async def query_advanced(
        self,
        file_path: str | Path,
        query: str,
        query_format: str | None = None,
        **options
    ) -> Any:
        """
        Advanced query with full xwquery ExecutionResult.
        Returns full ExecutionResult object with metadata, not just results.
        Args:
            file_path: Path to XWJSON file
            query: Query string (any xwquery-supported format)
            query_format: Explicit query format (optional)
            **options: Additional query options
        Returns:
            ExecutionResult object with query results and metadata
        Raises:
            ImportError: If xwquery not available
        """
        data = await self.atomic_read(file_path)
        try:
            from exonware.xwquery import XWQuery
            # Execute query and return full ExecutionResult
            return XWQuery.execute(
                query,
                data,
                format=query_format,
                auto_detect=query_format is None,
                **options
            )
        except ImportError:
            raise ImportError(
                "xwquery is required for advanced queries. "
                "Install with: pip install exonware-xwquery"
            )
    # ========================================================================
    # BATCH OPERATIONS
    # ========================================================================

    async def execute_batch(
        self,
        file_path: str | Path,
        operations: list[dict[str, Any]]
    ) -> list[Any]:
        """
        Execute batch operations with smart dependency resolution.
        Uses xwnode for dependency graph and topological sort.
        Args:
            file_path: Path to XWJSON file
            operations: list of operations to execute
        Returns:
            list of operation results
        """
        # Fast path: execute simple path operations in-memory with a single write.
        # This removes repeated file read/write cycles for large batches.
        simple_ops = {"read_path", "write_path", "update_path", "delete_path"}
        if operations and all(op.get("op") in simple_ops for op in operations):
            return await self._execute_batch_in_memory(file_path, operations)
        # Build dependency graph and get execution order
        execution_levels = self._dependency_graph.topological_sort(operations)
        results = []
        # Execute each level in parallel, levels sequentially
        for level_idx, level in enumerate(execution_levels):
            # Get operations for this level
            level_ops = [operations[int(op_id.split("_")[1])] for op_id in level]
            # Execute operations in parallel
            level_tasks = [
                self._execute_operation(file_path, op) for op in level_ops
            ]
            level_results = await asyncio.gather(*level_tasks)
            results.extend(level_results)
            # Invalidate cache after each level to ensure next level sees latest data
            # This is critical for read-after-write dependencies
            file_path_obj = Path(file_path).resolve()
            # Invalidate file cache (XWNode LRU_CACHE)
            cache_key = str(file_path_obj)
            self._file_cache.delete(cache_key)
            # Also invalidate path caches (XWNode LRU_CACHE)
            # Iterate strategy keys directly (XWNode facade doesn't expose keys() directly)
            path_cache_keys_to_remove = [
                k for k in self._path_cache._strategy.keys() 
                if k.startswith(str(file_path_obj) + ":")
            ]
            for key in path_cache_keys_to_remove:
                self._path_cache.delete(key)
        return results

    async def _execute_batch_in_memory(
        self,
        file_path: str | Path,
        operations: list[dict[str, Any]]
    ) -> list[Any]:
        """Execute path operations against in-memory data, then write once."""
        from jsonpointer import JsonPointer, JsonPointerException, resolve_pointer, set_pointer

        data = await self.atomic_read(file_path, use_cache=False)
        results: list[Any] = []
        has_mutation = False

        for operation in operations:
            op_type = operation.get("op")
            path = operation.get("path", "")

            if op_type == "read_path":
                try:
                    results.append(resolve_pointer(data, path))
                except Exception as e:
                    raise SerializationError(f"Failed to read path {path}: {e}") from e
                continue

            if op_type in ("write_path", "update_path"):
                path_stripped = path.rstrip("/")
                if path_stripped and path_stripped.startswith("/"):
                    parts = path_stripped.split("/")[1:]
                    for i in range(1, len(parts)):
                        prefix = "/" + "/".join(parts[:i])
                        try:
                            JsonPointer(prefix).resolve(data)
                        except (JsonPointerException, KeyError, TypeError):
                            try:
                                set_pointer(data, prefix, {})
                            except Exception as e:
                                raise SerializationError(
                                    f"Cannot create path {path}: segment {prefix} not a dict ({e})"
                                ) from e
                try:
                    set_pointer(data, path, operation["value"])
                except Exception as e:
                    raise SerializationError(f"Failed to write path {path}: {e}") from e
                results.append(None)
                has_mutation = True
                continue

            if op_type == "delete_path":
                try:
                    if path == "":
                        data = {}
                    else:
                        parts = path.strip("/").split("/")
                        if len(parts) == 1:
                            if isinstance(data, dict) and parts[0] in data:
                                del data[parts[0]]
                        else:
                            parent_path = "/" + "/".join(parts[:-1])
                            key = parts[-1]
                            parent = resolve_pointer(data, parent_path)
                            if isinstance(parent, dict):
                                if key in parent:
                                    del parent[key]
                            elif isinstance(parent, list):
                                index = int(key)
                                if 0 <= index < len(parent):
                                    parent.pop(index)
                            else:
                                raise SerializationError(f"Cannot delete from {type(parent).__name__} at {path}")
                except Exception as e:
                    raise SerializationError(f"Failed to delete path {path}: {e}") from e
                results.append(None)
                has_mutation = True
                continue

            raise SerializationError(f"Unknown operation type: {op_type}")

        if has_mutation:
            await self.atomic_write(file_path, data)
        return results

    async def _execute_operation(
        self,
        file_path: str | Path,
        operation: dict[str, Any]
    ) -> Any:
        """Execute single operation."""
        op_type = operation.get("op")
        if op_type == "read_path":
            return await self.read_path(file_path, operation["path"])
        elif op_type == "write_path":
            await self.write_path(file_path, operation["path"], operation["value"])
            return None
        elif op_type == "update_path":
            await self.write_path(file_path, operation["path"], operation["value"])
            return None
        elif op_type == "delete_path":
            await self.delete_path(file_path, operation["path"])
            return None
        else:
            raise SerializationError(f"Unknown operation type: {op_type}")
