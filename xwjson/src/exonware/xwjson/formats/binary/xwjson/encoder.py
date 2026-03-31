# exonware/xwjson/src/exonware/xwjson/formats/binary/xwjson/encoder.py
"""
XWJSON Binary Encoder/Decoder
Company: eXonware.com
Author: eXonware Backend Team
Version: 0.9.0.11
Generation Date: 2025-01-XX
Binary encoding/decoding for XWJSON format using MessagePack with hybrid parser.
Optimized for high-throughput serialization (150MB/s+).
"""

import os
import struct
import mmap
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any
import msgspec
import orjson
from exonware.xwsystem.io.errors import SerializationError
# ============================================================================
# CONSTANTS & HEADERS
# ============================================================================
XWJSON_MAGIC = b'XWJ1'
XWJSON_VERSION = 1
HEADER_STRUCT = struct.Struct('>4sBBBI I I')  # Pre-compiled struct for speed
HEADER_SIZE = HEADER_STRUCT.size
# Format Codes
FORMAT_JSON = 0x00
FORMAT_YAML = 0x01
FORMAT_XML = 0x02
FORMAT_TOML = 0x03
# Flags
FLAG_HAS_METADATA = 0x01
FLAG_HAS_INDEX = 0x02
FLAG_COMPRESSED = 0x04
FLAG_ENCRYPTED = 0x08
FLAG_STREAMING = 0x20
FLAG_SCHEMA_INCLUDED = 0x40
# Thresholds
DUAL_FILE_THRESHOLD_MB = 10.0
PARALLEL_RECORD_THRESHOLD = 2000
# ============================================================================
# HYBRID PARSER (Optimized & Unified)
# ============================================================================


class XWJSONHybridParser:
    """
    Centralized hybrid parser. 
    Encapsulates the 'fastest path' logic to keep the main classes clean.
    """
    @staticmethod

    def json_loads(s: str | bytes) -> Any:
        """Fastest JSON read (msgspec)."""
        if isinstance(s, str):
            s = s.encode("utf-8")
        return msgspec.json.decode(s)
    @staticmethod

    def json_dumps(obj: Any, **kwargs) -> bytes:
        """Fastest JSON write (orjson)."""
        option = 0
        if kwargs.get("indent"):
            option |= orjson.OPT_INDENT_2
        if kwargs.get("sort_keys"):
            option |= orjson.OPT_SORT_KEYS
        # orjson defaults to ensure_ascii=False (UTF-8), which is what we want
        return orjson.dumps(obj, option=option)
    @staticmethod

    def msgpack_encode(obj: Any) -> bytes:
        """Direct MessagePack encoding (msgspec)."""
        return msgspec.msgpack.encode(obj)
    @staticmethod

    def msgpack_decode(b: bytes) -> Any:
        """Direct MessagePack decoding (msgspec)."""
        return msgspec.msgpack.decode(b)

    def dumps(self, obj: Any, **kwargs) -> bytes:
        """Encode object to bytes (JSON format)."""
        return self.json_dumps(obj, **kwargs)

    def loads(self, s: str | bytes) -> Any:
        """Decode bytes/string to object (JSON format)."""
        return self.json_loads(s)
# ============================================================================
# ENCODER
# ============================================================================


class XWJSONEncoder:
    """
    XWJSON binary encoder.
    Optimized for zero-copy operations where possible and parallel processing for large datasets.
    """

    def __init__(self, write_parser: str | None = None):
        self._progress_callback = None

    def encode(
        self,
        data: Any,
        metadata: dict[str, Any] | None = None,
        format_code: int = FORMAT_JSON,
        flags: int = 0,
        index: dict[str, Any] | None = None,
        file_path: str | Path | None = None,
        create_index_file: bool = False
    ) -> bytes:
        try:
            # 1. Analyze Data Structure
            records_list, data_wrapper = self._extract_records(data)
            # 2. Determine Strategy (Dual File vs Single File)
            if records_list and file_path:
                is_large = (len(records_list) * 300) / (1024 * 1024) > DUAL_FILE_THRESHOLD_MB
                if create_index_file or is_large:
                    return self._encode_dual_file_format(
                        records_list, data_wrapper, metadata, format_code, flags, Path(file_path)
                    )
                else:
                    return self._encode_single_file_optimized(
                        records_list, data_wrapper, metadata, format_code, flags
                    )
            # 3. Streaming Format (Record Level)
            if records_list:
                return self._encode_record_level(
                    records_list, data_wrapper, metadata, format_code, flags | FLAG_STREAMING
                )
            # 4. Standard Format (Blob)
            return self._encode_standard(data, metadata, index, format_code, flags)
        except Exception as e:
            raise SerializationError(f"Encoding failed: {e}") from e

    def _extract_records(self, data: Any) -> tuple[list[Any] | None, dict[str, Any] | None]:
        """Identify if data is a list of records or a wrapper dict."""
        if isinstance(data, list) and data:
            return data, None
        if isinstance(data, dict):
            for key in ["records", "entities"]:
                if key in data and isinstance(data[key], list) and data[key]:
                    wrapper = {k: v for k, v in data.items() if k != key}
                    return data[key], (wrapper if wrapper else None)
        return None, None

    def _encode_standard(self, data: Any, metadata: Any, index: Any, format_code: int, flags: int) -> bytes:
        """Traditional encoding for non-record-based data."""
        if index is None:
            index = self._build_index_if_needed(data)
        # Binary Encode Components
        data_bytes = XWJSONHybridParser.msgpack_encode(data)
        meta_bytes = XWJSONHybridParser.msgpack_encode(metadata) if metadata else b''
        index_bytes = XWJSONHybridParser.msgpack_encode(index) if index else b''
        # Update Flags
        if metadata: flags |= FLAG_HAS_METADATA
        if index: flags |= FLAG_HAS_INDEX
        header = self._build_header(XWJSON_VERSION, flags, format_code, len(data_bytes), len(meta_bytes), len(index_bytes))
        return header + data_bytes + meta_bytes + index_bytes

    def _encode_record_level(self, records: list[Any], wrapper: Any, metadata: Any, code: int, flags: int) -> bytes:
        """Streaming format: [Header][Rec1][Rec2]...[Meta][Index]."""
        total = len(records)
        record_bytes_list = []
        record_offsets = []
        current_offset = 0
        # Parallel Encoding
        use_parallel = total > PARALLEL_RECORD_THRESHOLD
        if use_parallel:
            with ThreadPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
                # Use map to preserve order
                results = ex.map(XWJSONHybridParser.msgpack_encode, records)
                for rb in results:
                    record_offsets.append(current_offset)
                    record_bytes_list.append(rb)
                    current_offset += len(rb)
        else:
            for rec in records:
                rb = XWJSONHybridParser.msgpack_encode(rec)
                record_offsets.append(current_offset)
                record_bytes_list.append(rb)
                current_offset += len(rb)
        records_blob = b''.join(record_bytes_list)
        # Build Index
        index = {
            'type': 'dict_records' if wrapper else 'list',
            'record_count': total,
            'record_offsets': record_offsets,
            'wrapper': wrapper
        }
        meta_bytes = XWJSONHybridParser.msgpack_encode(metadata) if metadata else b''
        index_bytes = XWJSONHybridParser.msgpack_encode(index)
        flags |= FLAG_HAS_INDEX | (FLAG_HAS_METADATA if metadata else 0)
        header = self._build_header(XWJSON_VERSION, flags, code, len(records_blob), len(meta_bytes), len(index_bytes))
        return header + records_blob + meta_bytes + index_bytes

    def _encode_single_file_optimized(self, records: list[Any], wrapper: Any, metadata: Any, code: int, flags: int) -> bytes:
        """Optimized Single File: [MsgPack Array][Meta Block][FooterOffset]."""
        # 1. Main Data (Raw Array)
        data_bytes = XWJSONHybridParser.msgpack_encode(records)
        # 2. Calculate offsets for paging (requires re-traversing or encoding individually)
        # Note: To enable paging in single file, we need offsets.
        # This adds overhead. If speed is critical, we might skip offsets here.
        record_offsets = []
        curr = 0
        for r in records:
            record_offsets.append(curr)
            curr += len(XWJSONHybridParser.msgpack_encode(r))
        meta = {
            'format': 'single_file_optimized',
            'header': {'version': XWJSON_VERSION, 'flags': flags, 'format_code': code, 'magic': 'XWJ1'},
            'metadata': metadata,
            'record_offsets': record_offsets,
            'wrapper': wrapper,
            'data_length': len(data_bytes)
        }
        meta_bytes = XWJSONHybridParser.msgpack_encode(meta)
        footer = struct.pack('>I', len(data_bytes)) # Pointer to start of meta
        return data_bytes + meta_bytes + footer

    def _encode_dual_file_format(self, records: list[Any], wrapper: Any, metadata: Any, code: int, flags: int, file_path: Path) -> bytes:
        """Dual File: .data (Raw Array) + .meta (Index/Info)."""
        # 1. Main Data (Raw Array)
        data_bytes = XWJSONHybridParser.msgpack_encode(records)
        # Resolve paths
        base = file_path.parent / file_path.stem.replace('.data', '')
        data_path = base.with_name(f"{base.name}.data.xwjson")
        meta_path = base.with_name(f"{base.name}.meta.xwjson")
        meta = {
            'format': 'dual_file_minimal',
            'header': {
                'version': XWJSON_VERSION, 'flags': flags, 'format_code': code, 
                'data_length': len(data_bytes), 'magic': 'XWJ1'
            },
            'metadata': metadata,
            'record_count': len(records),
            'wrapper': wrapper,
            'record_offsets': [] # Calculated on-demand on read to save write time
        }
        # Write files
        with open(data_path, 'wb') as f:
            f.write(data_bytes)
        with open(meta_path, 'wb') as f:
            f.write(XWJSONHybridParser.msgpack_encode(meta))
        return data_bytes

    def _build_header(self, *args) -> bytes:
        return HEADER_STRUCT.pack(XWJSON_MAGIC, *args)

    def _build_index_if_needed(self, data: Any) -> dict | None:
        if isinstance(data, list):
            return {'type': 'list', 'record_count': len(data)}
        if isinstance(data, dict) and 'records' in data and isinstance(data['records'], list):
            return {'type': 'dict_records', 'record_count': len(data['records']), 'path': '/records'}
        return None
# ============================================================================
# DECODER
# ============================================================================


class XWJSONDecoder:
    """
    XWJSON binary decoder.
    Support for memory mapping, partial reads, and intelligent index caching.
    """

    def __init__(self, read_parser: str | None = None):
        # Allow injection of cache handler if needed
        pass

    def decode(
        self, 
        data: bytes, 
        file_path: str | Path | None = None
    ) -> tuple[Any, dict | None, dict | None, dict]:
        try:
            # 1. Try Optimized Footer Format (Single File Optimized)
            if len(data) > 4:
                try:
                    meta_offset = struct.unpack('>I', data[-4:])[0]
                    if 0 < meta_offset < len(data) - 4:
                        meta = XWJSONHybridParser.msgpack_decode(data[meta_offset:-4])
                        if meta.get('format') == 'single_file_optimized':
                            decoded = XWJSONHybridParser.msgpack_decode(data[:meta_offset])
                            return decoded, meta.get('metadata'), meta, meta.get('header', {})
                except Exception:
                    pass # Fallthrough
            # 2. Try Dual File / Minimal Format (Pure Array)
            file_path_obj = Path(file_path) if file_path else None
            if file_path_obj and file_path_obj.name.endswith('.data.xwjson'):
                meta = self._load_external_index(file_path_obj)
                if not meta:
                    raise SerializationError("Meta file missing for .data.xwjson")
                return XWJSONHybridParser.msgpack_decode(data), meta.get('metadata'), meta, meta.get('header', {})
            # 3. Standard Header Format
            if len(data) < HEADER_SIZE:
                raise SerializationError("Data too short: expected at least HEADER_SIZE bytes")
            if data[:4] != XWJSON_MAGIC:
                raise SerializationError("Invalid XWJSON magic bytes or header")
            header_info = self._parse_header(data[:HEADER_SIZE])
            # Offsets
            offset = HEADER_SIZE
            d_len, m_len, i_len = header_info['data_length'], header_info['metadata_length'], header_info['index_length']
            data_bytes = data[offset : offset + d_len]
            offset += d_len
            meta_bytes = data[offset : offset + m_len]
            offset += m_len
            index_bytes = data[offset : offset + i_len]
            # Parse Aux Blocks
            metadata = XWJSONHybridParser.msgpack_decode(meta_bytes) if m_len else None
            # Handle Streaming vs Standard
            if header_info['flags'] & FLAG_STREAMING:
                decoded, index = self._decode_streaming(data_bytes, index_bytes)
            else:
                decoded = XWJSONHybridParser.msgpack_decode(data_bytes)
                if i_len:
                    index = XWJSONHybridParser.msgpack_decode(index_bytes)
                elif file_path:
                    index = self._load_external_index(file_path)
                else:
                    index = None
            return decoded, metadata, index, header_info
        except Exception as e:
            raise SerializationError(f"Decoding failed: {e}") from e

    def _decode_streaming(self, data_bytes: bytes, index_bytes: bytes) -> tuple[Any, dict]:
        """Decode record-level streaming format."""
        index = XWJSONHybridParser.msgpack_decode(index_bytes)
        offsets = index.get('record_offsets', [])
        # Optimization: Full load via parallel batching
        if len(offsets) > 1000:
            records = self._batch_decode_bytes(data_bytes, offsets)
        elif offsets:
            # Sequential slice and decode
            records = []
            total_len = len(data_bytes)
            for i, start in enumerate(offsets):
                end = offsets[i+1] if i+1 < len(offsets) else total_len
                records.append(XWJSONHybridParser.msgpack_decode(data_bytes[start:end]))
        else:
            # Fallback to single blob decode
            records = XWJSONHybridParser.msgpack_decode(data_bytes)
        # Reconstruct wrapper if needed
        wrapper = index.get('wrapper')
        if wrapper:
            return {**wrapper, 'records': records}, index
        return records, index

    def _batch_decode_bytes(self, data: bytes, offsets: list[int]) -> list[Any]:
        """Parallel decode of byte slices."""
        total = len(offsets)
        d_len = len(data)
        results = [None] * total # Pre-allocate
        def decode_chunk(chunk_indices):
            chunk_res = []
            for i in chunk_indices:
                start = offsets[i]
                end = offsets[i+1] if i+1 < total else d_len
                chunk_res.append(XWJSONHybridParser.msgpack_decode(data[start:end]))
            return chunk_indices[0], chunk_res
        # Chunk indices to reduce thread overhead
        chunk_size = 500
        chunks = [range(i, min(i + chunk_size, total)) for i in range(0, total, chunk_size)]
        with ThreadPoolExecutor() as ex:
            for start_idx, res in ex.map(decode_chunk, chunks):
                results[start_idx : start_idx + len(res)] = res
        return results

    def _load_external_index(self, file_path: Path) -> dict | None:
        """
        Locates and loads external index/meta file.
        Attempts to use serializer cache to avoid disk I/O.
        """
        file_path = Path(file_path).resolve()
        # 1. Resolve Meta Path
        base = file_path.parent / file_path.stem.replace('.data', '')
        candidates = [
            base.with_name(f"{base.name}.meta.xwjson"),
            base.with_name(f"{base.name}.idx.xwjson")
        ]
        meta_path = next((p for p in candidates if p.exists()), None)
        if not meta_path:
            return None
        # 2. Check Cache (Abstracted safe access)
        cached = self._try_get_from_cache(file_path, meta_path)
        if cached:
            return cached
        # 3. Disk Load
        try:
            with open(meta_path, 'rb') as f:
                data = XWJSONHybridParser.msgpack_decode(f.read())
                # Handle old format (json inside msgpack)
                if isinstance(data, bytes):
                    data = XWJSONHybridParser.json_loads(data)
                # Update Cache
                self._try_update_cache(file_path, data, meta_path)
                return data
        except Exception:
            return None

    def _parse_header(self, header: bytes) -> dict[str, Any]:
        unpacked = HEADER_STRUCT.unpack(header)
        return {
            'magic': unpacked[0], 'version': unpacked[1], 'flags': unpacked[2],
            'format_code': unpacked[3], 'data_length': unpacked[4],
            'metadata_length': unpacked[5], 'index_length': unpacked[6]
        }
    # ========================================================================
    # Cache Helpers (Safe Interface)
    # ========================================================================

    def _try_get_from_cache(self, data_path: Path, meta_path: Path) -> dict | None:
        """Safely attempt to retrieve index from global/injected cache."""
        try:
            # Dynamic import to avoid circular dependency, but handled cleanly
            from .serializer import XWJSONSerializer
            return XWJSONSerializer._get_cached_index_static(data_path, meta_path)
        except (ImportError, AttributeError):
            return None

    def _try_update_cache(self, data_path: Path, index_data: dict, meta_path: Path):
        """Safely attempt to update global/injected cache."""
        try:
            from .serializer import XWJSONSerializer
            XWJSONSerializer._cache_index_data_static(data_path, index_data, meta_path)
        except (ImportError, AttributeError):
            pass
    # ========================================================================
    # Advanced I/O
    # ========================================================================

    def decode_partial(self, file_path: str | Path, start: int, end: int) -> list[Any]:
        """
        Partially decode a file using mmap.
        """
        path = Path(file_path)
        header_info, index = self.read_header_and_index(path)
        if not index or 'record_offsets' not in index:
            raise SerializationError("Index required for partial decoding")
        offsets = index['record_offsets']
        count = len(offsets)
        if start >= end or end > count:
            raise ValueError("Invalid range")
        # Streaming Format (Offsets are relative to Data Start)
        if header_info['flags'] & FLAG_STREAMING:
            data_start = HEADER_SIZE
            byte_start = data_start + offsets[start]
            byte_end = data_start + (offsets[end] if end < count else header_info['data_length'])
            with open(path, 'rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    chunk = mm[byte_start:byte_end]
            # Decode the chunk (must calculate relative offsets)
            records = []
            # Slice the subset of offsets
            subset_offsets = offsets[start:end]
            base_offset = subset_offsets[0]
            for i, abs_offset in enumerate(subset_offsets):
                chunk_start = abs_offset - base_offset
                if i + 1 < len(subset_offsets):
                    chunk_end = subset_offsets[i+1] - base_offset
                else:
                    chunk_end = len(chunk)
                records.append(XWJSONHybridParser.msgpack_decode(chunk[chunk_start:chunk_end]))
            return records
        else:
            # Dual File / Standard: Must decode full array and slice list
            # Note: Optimized Dual File usually has no internal offsets, so we load full array.
            # This is fast because it's a single msgpack operation.
            decoded, _, _, _ = self.decode_file_mmap(path)
            return decoded[start:end]

    def read_header_and_index(self, file_path: str | Path) -> tuple[dict, dict | None]:
        """
        Fastest way to get structure without loading data.
        Optimizations:
        1. Checks in-memory cache first (avoiding disk I/O entirely).
        2. Validates cache using file modification time (mtime).
        3. Returns cached tuple (Header, Index) immediately on hit.
        """
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"{path}")
        # --- LEVEL 1: HOT CACHE (Avoid File Open) ---
        # Try to retrieve the exact (Header, Index) tuple based on mtime
        cached_tuple = self._try_get_tuple_from_cache(path)
        if cached_tuple:
             # Cache Hit! Zero disk I/O (except stat check in helper)
            return cached_tuple
        # --- LEVEL 2: COLD READ (Disk Access) ---
        # If we are here, cache is cold or invalid. Read from disk.
        # Check for external index (e.g. .meta.xwjson)
        # Note: _load_external_index handles its own caching
        ext_index = self._load_external_index(path)
        with open(path, 'rb') as f:
            # Read minimal header (19 bytes)
            header_bytes = f.read(HEADER_SIZE)
            if len(header_bytes) < HEADER_SIZE:
                raise SerializationError("File too short for header")
            header_info = self._parse_header(header_bytes)
            # Determine Index
            index = ext_index
            if not index and (header_info['flags'] & FLAG_HAS_INDEX):
                # Index is embedded in the main file
                seek_pos = HEADER_SIZE + header_info['data_length'] + header_info['metadata_length']
                f.seek(seek_pos)
                index_bytes = f.read(header_info['index_length'])
                index = XWJSONHybridParser.msgpack_decode(index_bytes)
        # --- LEVEL 3: UPDATE CACHE ---
        result = (header_info, index)
        self._try_update_tuple_cache(path, result)
        return result

    def _try_get_tuple_from_cache(self, path: Path) -> tuple[dict, dict | None] | None:
        """
        Retrieves (header, index) tuple ONLY if file mtime matches cache.
        """
        try:
            from .serializer import XWJSONSerializer
            if not XWJSONSerializer._cache_initialized:
                return None
            cache_key = f"header_index:{str(path)}"
            with XWJSONSerializer._cache_lock:
                # 1. Check if entry exists
                cached_data = XWJSONSerializer._index_cache.get(cache_key)
                if not cached_data:
                    return None
                # 2. Validate MTIME (Critical Security/Integrity Step)
                current_mtime = path.stat().st_mtime
                cached_mtime = XWJSONSerializer._mtime_cache.get(str(path))
                if current_mtime != cached_mtime:
                    # Stale cache - invalidate it implicitly by returning None
                    # (The caller will re-read and we will overwrite later)
                    return None
                return cached_data
        except (ImportError, AttributeError, OSError):
            return None

    def _try_update_tuple_cache(self, path: Path, data: tuple[dict, dict | None]):
        """
        Updates the tuple cache and the mtime cache atomically.
        """
        try:
            from .serializer import XWJSONSerializer
            if not XWJSONSerializer._cache_initialized:
                return
            cache_key = f"header_index:{str(path)}"
            current_mtime = path.stat().st_mtime
            with XWJSONSerializer._cache_lock:
                XWJSONSerializer._index_cache.put(cache_key, data)
                XWJSONSerializer._mtime_cache[str(path)] = current_mtime
                # OPTIMIZATION: Also populate the individual index cache
                # This helps other methods like _load_external_index that might look for just the dict
                if data[1]: # If index exists
                    # We might need to resolve the meta path here, or just cache on the main file key
                    # For simplicity in this tuple-centric view, we skip complex cross-file mapping
                    pass 
        except (ImportError, AttributeError, OSError):
            pass

    def decode_file_mmap(self, file_path: str | Path) -> tuple[Any, dict | None, dict | None, dict]:
        path = Path(file_path)
        # Check for minimal data file
        if path.suffix == '.xwjson' and not path.name.endswith('.data.xwjson'):
            min_path = path.with_name(f"{path.stem}.data.xwjson")
            if min_path.exists():
                path = min_path
        with open(path, 'rb') as f:
            # mmap context manager ensures close() is called
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                # mmap behaves like bytes, so we can pass it directly
                return self.decode(mm, file_path=path)
