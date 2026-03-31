#exonware/xwjson/src/exonware/xwjson/formats/binary/xwjson/converter.py
"""
XWJSON Format Converter - Universal Intermediate Format
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 2025-01-XX
XWJSON as universal intermediate format for all conversions.
Enables lossless conversion chain: Source → XWJSON → Target.
Priority 1 (Security): Safe conversion, input validation
Priority 2 (Usability): Clear conversion API, helpful error messages
Priority 3 (Maintainability): Clean code, design patterns
Priority 4 (Performance): Fast conversion, metadata preservation
Priority 5 (Extensibility): Plugin system for custom formats
"""

from typing import Any
from pathlib import Path
from .serializer import XWJSONSerializer
from .metadata import FormatMetadataExtractor, FormatMetadataRestorer
from exonware.xwsystem.io.errors import SerializationError
from exonware.xwsystem.io.serialization.formats.text import json as xw_json


class XWJSONConverter:
    """
    Format converter using XWJSON as universal intermediate format.
    Conversion flow: Source Format → XWJSON → Target Format
    Features:
    - Lossless conversion chain (metadata preserved)
    - Single code path for all format operations
    - Consistent performance across all formats
    - Future-proof (new formats automatically supported)
    - Centralized optimization (improve once, benefit all)
    """

    def __init__(self):
        """Initialize format converter."""
        self._serializer = XWJSONSerializer()
        self._metadata_extractor = FormatMetadataExtractor()
        self._metadata_restorer = FormatMetadataRestorer()

    async def convert(
        self,
        source_data: Any,
        source_format: str,
        target_format: str,
        source_path: str | Path | None = None,
        target_path: str | Path | None = None
    ) -> Any:
        """
        Convert data from source format to target format via XWJSON.
        Args:
            source_data: Source data (format-specific)
            source_format: Source format name (json, yaml, xml, toml, etc.)
            target_format: Target format name (json, yaml, xml, toml, etc.)
            source_path: Optional source file path (for metadata extraction)
            target_path: Optional target file path (for saving)
        Returns:
            Converted data (format-specific)
        """
        # 1. Extract metadata from source format
        metadata = self._metadata_extractor.extract(
            source_data,
            source_format,
            source_path=source_path
        )
        # 2. Convert source → XWJSON (preserve metadata)
        xwjson_data = await self._to_xwjson(source_data, source_format, metadata)
        # 3. Convert XWJSON → target (restore metadata)
        target_data = await self._from_xwjson(xwjson_data, target_format, metadata)
        # 4. Save to target path if provided
        if target_path:
            await self._save_target(target_data, target_format, target_path)
        return target_data

    async def _to_xwjson(
        self,
        data: Any,
        source_format: str,
        metadata: Any
    ) -> bytes:
        """Convert source format to XWJSON."""
        # Encode with metadata
        format_code = self._get_format_code(source_format)
        return self._serializer.encode(
            data,
            options={
                'metadata': metadata.__dict__ if hasattr(metadata, '__dict__') else metadata,
                'format_code': format_code,
                'flags': 0x01 if metadata else 0x00  # FLAG_HAS_METADATA
            }
        )

    async def _from_xwjson(
        self,
        xwjson_data: bytes,
        target_format: str,
        metadata: Any
    ) -> Any:
        """Convert XWJSON to target format."""
        # Decode XWJSON
        result = self._serializer.decode(
            xwjson_data,
            options={'return_metadata': True}
        )
        data = result.get('data')
        extracted_metadata = result.get('metadata')
        # Restore metadata to target format
        if extracted_metadata and metadata:
            # Merge metadata
            if hasattr(metadata, '__dict__'):
                metadata.__dict__
            else:
                pass
            # Restore to target format
            return self._metadata_restorer.restore(
                data,
                metadata,
                target_format
            )
        return data

    async def _save_target(
        self,
        data: Any,
        target_format: str,
        target_path: str | Path
    ) -> None:
        """Save data to target format file using AutoSerializer."""
        try:
            from exonware.xwsystem.io.serialization.auto_serializer import AutoSerializer
            auto_serializer = AutoSerializer()
            target_path = Path(target_path)
            # Use AutoSerializer to save with format hint
            auto_serializer.auto_save_file(data, target_path, format_hint=target_format)
        except ImportError:
            # Fallback to manual format detection
            target_path = Path(target_path)
            suffix = target_path.suffix.lower()
            if suffix in ('.json', '.json5'):
                with open(target_path, 'w', encoding='utf-8') as f:
                    xw_json.dump(data, f, indent=2)
            elif suffix in ('.yaml', '.yml'):
                try:
                    import yaml
                    with open(target_path, 'w', encoding='utf-8') as f:
                        yaml.dump(data, f, default_flow_style=False)
                except ImportError:
                    raise SerializationError(
                        "YAML serialization requires PyYAML. Install with: pip install pyyaml"
                    )
            elif suffix == '.xml':
                try:
                    import xml.etree.ElementTree as ET
                    if isinstance(data, ET.Element):
                        tree = ET.ElementTree(data)
                        tree.write(target_path, encoding='utf-8', xml_declaration=True)
                    else:
                        raise SerializationError("Data must be an XML Element for XML serialization")
                except Exception as e:
                    raise SerializationError(f"Failed to serialize XML: {e}") from e
            elif suffix == '.toml':
                try:
                    import tomli_w
                    with open(target_path, 'wb') as f:
                        tomli_w.dump(data, f)
                except ImportError:
                    raise SerializationError(
                        "TOML serialization requires tomli-w. Install with: pip install tomli-w"
                    )
            else:
                # Default to JSON
                with open(target_path, 'w', encoding='utf-8') as f:
                    xw_json.dump(data, f, indent=2)

    def _get_format_code(self, format_name: str) -> int:
        """Get format code for format name."""
        format_codes = {
            'json': 0x00,
            'yaml': 0x01,
            'xml': 0x02,
            'toml': 0x03,
            'csv': 0x04,
            'bson': 0x05,
            'msgpack': 0x06,
            'cbor': 0x07,
            'ubjson': 0x08,
            'json5': 0x09,
            'jsonl': 0x0A,
            'ndjson': 0x0A,
        }
        return format_codes.get(format_name.lower(), 0x00)

    def convert_sync(
        self,
        source_data: Any,
        source_format: str,
        target_format: str,
        source_path: str | Path | None = None,
        target_path: str | Path | None = None
    ) -> Any:
        """
        Synchronous version of convert for convenience.
        Args:
            source_data: Source data (format-specific)
            source_format: Source format name
            target_format: Target format name
            source_path: Optional source file path
            target_path: Optional target file path
        Returns:
            Converted data (format-specific)
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a new task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.convert(source_data, source_format, target_format, source_path, target_path)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(
                    self.convert(source_data, source_format, target_format, source_path, target_path)
                )
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(
                self.convert(source_data, source_format, target_format, source_path, target_path)
            )
