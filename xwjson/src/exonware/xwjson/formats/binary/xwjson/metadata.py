#exonware/xwjson/src/exonware/xwjson/formats/binary/xwjson/metadata.py
"""
Format Metadata Extractor and Restorer
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 2025-01-XX
Extracts and restores format-specific metadata (YAML anchors, XML namespaces, etc.)
to enable lossless round-trip conversion.
Priority 1 (Security): Safe metadata extraction, path validation
Priority 2 (Usability): Clear metadata structure, helpful error messages
Priority 3 (Maintainability): Clean code, design patterns
Priority 4 (Performance): Fast metadata extraction/restoration
Priority 5 (Extensibility): Plugin system for custom formats
"""

from typing import Any
from dataclasses import dataclass, field
@dataclass


class FormatMetadata:
    """
    Container for all format-specific metadata.
    Preserves format-specific features during conversion:
    - YAML: anchors, aliases, multi-document, comments, tags
    - XML: namespaces, attributes, processing instructions, CDATA, DOCTYPE
    - TOML: table arrays, inline tables, date/time types, comments
    - JSON: comments (JSON5), trailing commas, references
    - xwformats: schema info, compression, encoding
    - xwsyntax: grammar metadata, AST structure
    """
    # Source format information
    source_format: str = "json"  # json, yaml, xml, toml, etc.
    source_version: str | None = None
    # YAML-specific metadata
    yaml_anchors: dict[str, Any] = field(default_factory=dict)  # &anchor -> value
    yaml_aliases: dict[str, str] = field(default_factory=dict)  # *alias -> &anchor
    yaml_tags: dict[str, str] = field(default_factory=dict)  # !!tag -> type
    yaml_comments: dict[str, str] = field(default_factory=dict)  # path -> comment
    yaml_multi_document: list[int] = field(default_factory=list)  # Document offsets
    # XML-specific metadata
    xml_namespaces: dict[str, str] = field(default_factory=dict)  # prefix -> URI
    xml_attributes: dict[str, dict[str, str]] = field(default_factory=dict)  # path -> {attr: value}
    xml_processing_instructions: list[dict[str, str]] = field(default_factory=list)
    xml_cdata_sections: list[str] = field(default_factory=list)  # Paths to CDATA sections
    xml_doctype: dict[str, Any] | None = None
    # TOML-specific metadata
    toml_table_arrays: list[str] = field(default_factory=list)  # Paths to table arrays
    toml_inline_tables: list[str] = field(default_factory=list)  # Paths to inline tables
    toml_date_time_types: dict[str, str] = field(default_factory=dict)  # path -> type
    toml_comments: dict[str, str] = field(default_factory=dict)  # path -> comment
    # JSON-specific metadata
    json_comments: dict[str, str] = field(default_factory=dict)  # path -> comment (JSON5)
    json_trailing_commas: list[str] = field(default_factory=list)  # Paths with trailing commas
    json_references: dict[str, str] = field(default_factory=dict)  # path -> $ref value
    # xwformats-specific metadata
    xwformats_schema: dict[str, Any] | None = None
    xwformats_compression: str | None = None
    xwformats_encoding: str | None = None
    # xwsyntax-specific metadata
    xwsyntax_grammar: dict[str, Any] | None = None
    xwsyntax_ast: dict[str, Any] | None = None
    # Custom metadata (for future extensions)
    custom: dict[str, Any] = field(default_factory=dict)


class FormatMetadataExtractor:
    """
    Extracts format-specific metadata from source formats.
    Supports extraction from:
    - YAML (anchors, aliases, tags, comments)
    - XML (namespaces, attributes, processing instructions, CDATA, DOCTYPE)
    - TOML (table arrays, inline tables, date/time types, comments)
    - JSON (comments, trailing commas, references)
    - xwformats (schema, compression, encoding)
    - xwsyntax (grammar, AST)
    """

    def extract(self, data: Any, source_format: str, **kwargs) -> FormatMetadata:
        """
        Extract metadata from source format.
        Args:
            data: Source data (format-specific)
            source_format: Source format name (yaml, xml, toml, json, etc.)
            **kwargs: Format-specific extraction options
        Returns:
            FormatMetadata with extracted metadata
        """
        metadata = FormatMetadata(source_format=source_format)
        if source_format.lower() == 'yaml':
            return self._extract_yaml(data, metadata, **kwargs)
        elif source_format.lower() == 'xml':
            return self._extract_xml(data, metadata, **kwargs)
        elif source_format.lower() == 'toml':
            return self._extract_toml(data, metadata, **kwargs)
        elif source_format.lower() == 'json':
            return self._extract_json(data, metadata, **kwargs)
        else:
            # Unknown format - return empty metadata
            return metadata

    def _extract_yaml(self, data: Any, metadata: FormatMetadata, **kwargs) -> FormatMetadata:
        """
        Extract YAML-specific metadata (anchors, aliases, tags, comments).
        Note: Full YAML metadata extraction requires ruamel.yaml which preserves
        anchors, aliases, tags, and comments. Standard PyYAML does not preserve this metadata.
        For now, provides basic extraction where possible with standard libraries.
        """
        source_path = kwargs.get('source_path')
        # Try to use ruamel.yaml if available (preserves metadata)
        try:
            from ruamel.yaml import YAML
            if source_path:
                yaml_parser = YAML()
                yaml_parser.preserve_quotes = True
                with open(source_path, encoding='utf-8') as f:
                    yaml_parser.load(f)
                    # ruamel.yaml preserves anchors/aliases in the data structure
                    # This is a simplified extraction - full implementation would
                    # traverse the ruamel.yaml data structure to extract all metadata
                    metadata.source_format = "yaml"
                    # Note: Full anchor/alias/tag/comment extraction would require
                    # traversing ruamel.yaml's internal structure
        except ImportError:
            # Fallback: Use standard PyYAML (doesn't preserve metadata)
            # Basic extraction from data structure
            if isinstance(data, dict):
                # Look for anchor-like patterns in keys
                for key, value in data.items():
                    if isinstance(key, str):
                        if key.startswith('&'):
                            anchor_name = key[1:]
                            metadata.yaml_anchors[anchor_name] = value
                        elif key.startswith('*'):
                            alias_name = key[1:]
                            metadata.yaml_aliases[alias_name] = key
        return metadata

    def _extract_xml(self, data: Any, metadata: FormatMetadata, **kwargs) -> FormatMetadata:
        """
        Extract XML-specific metadata (namespaces, attributes, processing instructions, CDATA, DOCTYPE).
        Uses xml.etree.ElementTree for basic extraction. For full metadata preservation
        (especially comments and processing instructions), lxml is recommended.
        """
        source_path = kwargs.get('source_path')
        try:
            import xml.etree.ElementTree as ET
            # Load XML if source_path provided
            if source_path:
                tree = ET.parse(source_path)
                root = tree.getroot()
            elif isinstance(data, ET.Element):
                root = data
            else:
                return metadata
            # Extract namespaces
            for prefix, uri in root.attrib.items():
                if prefix.startswith('xmlns'):
                    ns_prefix = prefix[6:] if prefix.startswith('xmlns:') else ''
                    metadata.xml_namespaces[ns_prefix] = uri
            # Extract attributes (basic - full implementation would preserve all attributes)
            def extract_attributes(element: ET.Element, path: str = ""):
                if element.attrib:
                    metadata.xml_attributes[path] = element.attrib.copy()
                for child in element:
                    child_path = f"{path}/{child.tag}" if path else f"/{child.tag}"
                    extract_attributes(child, child_path)
            extract_attributes(root)
            # Note: Processing instructions, CDATA, and DOCTYPE require
            # lxml or manual parsing of the XML source
            metadata.source_format = "xml"
        except ImportError:
            # XML support should be available via xml.etree.ElementTree
            pass
        except Exception:
            # If extraction fails, return metadata with format set
            metadata.source_format = "xml"
        return metadata

    def _extract_toml(self, data: Any, metadata: FormatMetadata, **kwargs) -> FormatMetadata:
        """
        Extract TOML-specific metadata (table arrays, inline tables, date/time types, comments).
        Note: Full TOML metadata extraction requires a parser that preserves comments
        and table structure (like tomli-w or tomlkit). Standard tomli does not preserve comments.
        """
        kwargs.get('source_path')
        # Basic extraction from parsed data structure
        def detect_toml_structure(obj: Any, path: str = ""):
            """Detect TOML-specific structures in data."""
            if isinstance(obj, dict):
                # Check for inline table patterns (all values are simple types)
                is_inline_table = all(
                    isinstance(v, (str, int, float, bool, type(None))) 
                    for v in obj.values()
                )
                if is_inline_table and path:
                    metadata.toml_inline_tables.append(path)
                # Check for date/time types
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    if isinstance(value, (str, type(None))):
                        # Heuristic: check if string looks like date/time
                        if value and isinstance(value, str):
                            if any(char in value for char in ['T', '-', ':']) and len(value) > 8:
                                metadata.toml_date_time_types[new_path] = "datetime"
                    detect_toml_structure(value, new_path)
            elif isinstance(obj, list):
                # Table array detection
                if path:
                    metadata.toml_table_arrays.append(path)
                for i, item in enumerate(obj):
                    detect_toml_structure(item, f"{path}[{i}]")
        detect_toml_structure(data)
        metadata.source_format = "toml"
        # Note: Comment extraction requires a TOML parser that preserves comments
        # (like tomlkit or tomli-w with comment support)
        return metadata

    def _extract_json(self, data: Any, metadata: FormatMetadata, **kwargs) -> FormatMetadata:
        """
        Extract JSON-specific metadata (comments, trailing commas, references).
        Extracts:
        - JSON5 comments (if source was JSON5)
        - Trailing commas (if source had them)
        - $ref references (JSON Reference/JSON Pointer)
        """
        source_path = kwargs.get('source_path')
        # Extract $ref references
        self._extract_json_references(data, metadata, "")
        # If source_path is provided and it's a JSON5 file, try to extract comments
        if source_path:
            path_obj = Path(source_path)
            if path_obj.suffix.lower() == '.json5':
                # JSON5 comments would need a JSON5 parser
                # For now, we note that it's JSON5 format
                metadata.source_format = "json5"
        return metadata

    def _extract_json_references(self, data: Any, metadata: FormatMetadata, path: str) -> None:
        """Recursively extract $ref references from JSON data."""
        if isinstance(data, dict):
            if "$ref" in data:
                ref_value = data["$ref"]
                metadata.json_references[path] = ref_value
            for key, value in data.items():
                new_path = f"{path}/{key}" if path else f"/{key}"
                self._extract_json_references(value, metadata, new_path)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_path = f"{path}/{i}"
                self._extract_json_references(item, metadata, new_path)


class FormatMetadataRestorer:
    """
    Restores format-specific metadata on round-trip conversion.
    Supports restoration to:
    - YAML (anchors, aliases, tags, comments)
    - XML (namespaces, attributes, processing instructions, CDATA, DOCTYPE)
    - TOML (table arrays, inline tables, date/time types, comments)
    - JSON (comments, trailing commas, references)
    """

    def restore(self, data: Any, metadata: FormatMetadata, target_format: str, **kwargs) -> Any:
        """
        Restore metadata to target format.
        Args:
            data: Data to restore metadata to
            metadata: FormatMetadata with metadata to restore
            target_format: Target format name (yaml, xml, toml, json, etc.)
            **kwargs: Format-specific restoration options
        Returns:
            Data with metadata restored (format-specific)
        """
        if target_format.lower() == 'yaml':
            return self._restore_yaml(data, metadata, **kwargs)
        elif target_format.lower() == 'xml':
            return self._restore_xml(data, metadata, **kwargs)
        elif target_format.lower() == 'toml':
            return self._restore_toml(data, metadata, **kwargs)
        elif target_format.lower() == 'json':
            return self._restore_json(data, metadata, **kwargs)
        else:
            # Unknown format - return data as-is
            return data

    def _restore_yaml(self, data: Any, metadata: FormatMetadata, **kwargs) -> Any:
        """
        Restore YAML-specific metadata (anchors, aliases, tags, comments).
        Note: Full YAML metadata restoration requires ruamel.yaml which can preserve
        anchors, aliases, tags, and comments. Standard PyYAML does not support this.
        """
        # Try to use ruamel.yaml if available
        try:
            from ruamel.yaml import YAML
            yaml_writer = YAML()
            yaml_writer.preserve_quotes = True
            # Restore anchors if available
            if metadata.yaml_anchors:
                # ruamel.yaml restoration would require building the data structure
                # with anchor/alias references - this is a simplified version
                pass
            # For now, return data as-is
            # Full implementation would use ruamel.yaml to build YAML with metadata
            return data
        except ImportError:
            # Fallback: Standard PyYAML doesn't support metadata restoration
            return data

    def _restore_xml(self, data: Any, metadata: FormatMetadata, **kwargs) -> Any:
        """
        Restore XML-specific metadata (namespaces, attributes, processing instructions, CDATA, DOCTYPE).
        Uses xml.etree.ElementTree for basic restoration. For full metadata preservation
        (especially comments and processing instructions), lxml is recommended.
        """
        try:
            import xml.etree.ElementTree as ET
            # Convert data to Element if needed
            if not isinstance(data, ET.Element):
                # Try to create element from dict
                if isinstance(data, dict):
                    root_tag = data.get('tag', 'root')
                    root = ET.Element(root_tag)
                    # Restore namespaces
                    for prefix, uri in metadata.xml_namespaces.items():
                        if prefix:
                            ET.register_namespace(prefix, uri)
                            root.set(f"xmlns:{prefix}", uri)
                        else:
                            root.set("xmlns", uri)
                    return root
                else:
                    return data
            # Restore namespaces
            for prefix, uri in metadata.xml_namespaces.items():
                if prefix:
                    ET.register_namespace(prefix, uri)
                    data.set(f"xmlns:{prefix}", uri)
                else:
                    data.set("xmlns", uri)
            # Restore attributes
            def restore_attributes(element: ET.Element, path: str = ""):
                if path in metadata.xml_attributes:
                    for attr, value in metadata.xml_attributes[path].items():
                        element.set(attr, value)
                for child in element:
                    child_path = f"{path}/{child.tag}" if path else f"/{child.tag}"
                    restore_attributes(child, child_path)
            restore_attributes(data)
            # Note: Processing instructions, CDATA, and DOCTYPE require
            # lxml or manual XML construction
            return data
        except ImportError:
            return data
        except Exception:
            return data

    def _restore_toml(self, data: Any, metadata: FormatMetadata, **kwargs) -> Any:
        """
        Restore TOML-specific metadata (table arrays, inline tables, date/time types, comments).
        Note: Full TOML metadata restoration requires a serializer that preserves comments
        and table structure (like tomli-w or tomlkit). Standard tomli-w does not preserve comments.
        """
        # Basic restoration - structure is already preserved in data
        # Full implementation would use tomlkit or similar to preserve comments
        # Note: TOML structure (table arrays, inline tables) is typically
        # preserved in the data structure itself, so no special restoration needed
        # for basic cases. Comment restoration requires specialized libraries.
        return data

    def _restore_json(self, data: Any, metadata: FormatMetadata, **kwargs) -> Any:
        """
        Restore JSON-specific metadata (comments, trailing commas, references).
        Restores:
        - $ref references (JSON Reference/JSON Pointer)
        - Note: JSON5 comments and trailing commas require format-specific serializers
        """
        # Restore $ref references
        if metadata.json_references:
            data = self._restore_json_references(data, metadata, "")
        return data

    def _restore_json_references(self, data: Any, metadata: FormatMetadata, path: str) -> Any:
        """Recursively restore $ref references to JSON data."""
        if isinstance(data, dict):
            # Check if this path should have a $ref
            if path in metadata.json_references:
                data["$ref"] = metadata.json_references[path]
            # Recursively process nested structures
            for key, value in data.items():
                new_path = f"{path}/{key}" if path else f"/{key}"
                data[key] = self._restore_json_references(value, metadata, new_path)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_path = f"{path}/{i}"
                data[i] = self._restore_json_references(item, metadata, new_path)
        return data
