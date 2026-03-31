#exonware/xwjson/src/exonware/xwjson/formats/binary/xwjson/references.py
"""
Reference Support for All Format-Specific References
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 2025-01-XX
Reference support for all format-specific references:
- JSON: $ref (JSON Reference, JSON Pointer)
- XML: @href (XLink, XPointer)
- YAML: *anchor (aliases), &anchor (anchors)
- TOML: Inline references
- xwformats: Format-specific references
- xwsyntax: Grammar references
Priority 1 (Security): Safe reference resolution, path validation, scheme checks
Priority 2 (Usability): Clear reference structure, helpful error messages
Priority 3 (Maintainability): Clean code, design patterns
Priority 4 (Performance): Fast reference resolution, caching
Priority 5 (Extensibility): Plugin system for custom references
"""

from typing import Any
from pathlib import Path
from urllib.parse import urlparse
from exonware.xwsystem.io.errors import SerializationError
from exonware.xwsystem.io.serialization.formats.text import json as xw_json


class XWJSONReferenceResolver:
    """
    Reference resolver for all format-specific references.
    Supports:
    - JSON: $ref (JSON Reference, JSON Pointer)
    - XML: @href (XLink, XPointer)
    - YAML: *anchor (aliases), &anchor (anchors)
    - TOML: Inline references
    - xwformats: Format-specific references
    - xwsyntax: Grammar references
    """

    def __init__(self):
        """Initialize reference resolver."""
        self._cache: dict[str, Any] = {}
        self._circular_detection: set[str] = set()
        self._resolving: set[str] = set()

    def resolve(
        self,
        reference: str,
        reference_type: str = "json",
        base_path: str | Path | None = None,
        data: Any | None = None
    ) -> Any:
        """
        Resolve reference.
        Args:
            reference: Reference string ($ref, @href, *anchor, etc.)
            reference_type: type of reference (json, xml, yaml, toml, etc.)
            base_path: Base path for relative references
            data: Source data (for JSON Pointer, YAML anchors, etc.)
        Returns:
            Resolved data
        Raises:
            SerializationError: If resolution fails or circular reference detected
        """
        # Check cache
        cache_key = f"{reference_type}:{reference}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        # Detect circular references
        if reference in self._resolving:
            raise SerializationError(f"Circular reference detected: {reference}")
        self._resolving.add(reference)
        try:
            # Resolve based on type
            if reference_type.lower() == "json":
                resolved = self._resolve_json_reference(reference, base_path, data)
            elif reference_type.lower() == "xml":
                resolved = self._resolve_xml_reference(reference, base_path, data)
            elif reference_type.lower() == "yaml":
                resolved = self._resolve_yaml_reference(reference, base_path, data)
            elif reference_type.lower() == "toml":
                resolved = self._resolve_toml_reference(reference, base_path, data)
            else:
                raise SerializationError(f"Unsupported reference type: {reference_type}")
            # Cache result
            self._cache[cache_key] = resolved
            return resolved
        finally:
            self._resolving.discard(reference)

    def _resolve_json_reference(
        self,
        reference: str,
        base_path: str | Path | None,
        data: Any | None
    ) -> Any:
        """
        Resolve JSON reference ($ref).
        Supports:
        - JSON Reference (RFC 6901): file://path/to/file.json
        - JSON Pointer (RFC 6901): #/paths/user
        - URL references: http://example.com/schema.json
        """
        # Check if it's a JSON Pointer (starts with #)
        if reference.startswith("#/"):
            return self._resolve_json_pointer(reference[2:], data)
        # Check if it's a file reference
        if reference.startswith("file://"):
            return self._resolve_file_reference(reference[7:], base_path)
        # Check if it's a URL reference
        parsed = urlparse(reference)
        if parsed.scheme in ("http", "https"):
            return self._resolve_http_reference(reference)
        # Assume it's a JSON Pointer without #
        if reference.startswith("/"):
            return self._resolve_json_pointer(reference[1:], data)
        raise SerializationError(f"Invalid JSON reference: {reference}")

    def _resolve_json_pointer(self, pointer: str, data: Any) -> Any:
        """
        Resolve JSON Pointer (RFC 6901).
        Examples:
        - "/users/0/name" -> data["users"][0]["name"]
        - "/metadata/version" -> data["metadata"]["version"]
        """
        if not data:
            raise SerializationError("No data provided for JSON Pointer resolution")
        # Decode JSON Pointer (replace ~1 with /, ~0 with ~)
        pointer = pointer.replace("~1", "/").replace("~0", "~")
        # Split path
        parts = pointer.split("/")
        if parts[0] == "":
            parts = parts[1:]
        # Navigate through data
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                try:
                    index = int(part)
                    current = current[index]
                except (ValueError, IndexError):
                    raise SerializationError(f"Invalid array index in JSON Pointer: {part}")
            else:
                raise SerializationError(f"Cannot navigate through {type(current).__name__} at {part}")
            if current is None:
                raise SerializationError(f"Reference not found: {pointer}")
        return current

    def _resolve_xml_reference(
        self,
        reference: str,
        base_path: str | Path | None,
        data: Any | None
    ) -> Any:
        """
        Resolve XML reference (@href, xlink:href, xml:base).
        Supports:
        - XLink href references (xlink:href)
        - XPointer references (#xpointer(...))
        - xml:base for relative resolution
        """
        # Try to use XML parser if available
        try:
            import xml.etree.ElementTree as ET
            # Check if it's a file reference
            if base_path and not reference.startswith(('http://', 'https://', '#')):
                xml_path = Path(base_path) / reference
                if xml_path.exists():
                    return ET.parse(xml_path).getroot()
            # Check if it's an XPointer reference (starts with #)
            if reference.startswith('#'):
                # XPointer syntax: #xpointer(/path/to/element)
                if 'xpointer(' in reference:
                    xpointer_expr = reference[reference.find('xpointer(')+9:reference.rfind(')')]
                    # Simple XPath-like resolution
                    if data:
                        # Try to resolve using ElementTree
                        if isinstance(data, ET.Element):
                            # Use findall with simplified XPath
                            elements = data.findall(xpointer_expr.replace('/', './'))
                            if elements:
                                return elements[0] if len(elements) == 1 else elements
                else:
                    # Simple fragment reference
                    fragment = reference[1:]
                    if data and isinstance(data, ET.Element):
                        element = data.find(f".//*[@id='{fragment}']")
                        if element is not None:
                            return element
            # Check if it's a URL
            parsed = urlparse(reference)
            if parsed.scheme in ("http", "https"):
                return self._resolve_http_reference(reference)
            raise SerializationError(f"Could not resolve XML reference: {reference}")
        except ImportError:
            raise SerializationError(
                f"XML reference resolution requires XML parser. "
                f"Python's xml.etree.ElementTree should be available. "
                f"Reference: {reference}"
            )
        except Exception as e:
            raise SerializationError(f"XML reference resolution failed: {e}") from e

    def _resolve_yaml_reference(
        self,
        reference: str,
        base_path: str | Path | None,
        data: Any | None
    ) -> Any:
        """
        Resolve YAML reference (*anchor, &anchor).
        Supports:
        - YAML anchor references (&anchor)
        - YAML alias references (*alias)
        - Multi-document references
        """
        # Try to use YAML parser if available
        try:
            import yaml
            # Check if reference is an alias (starts with *)
            if reference.startswith('*'):
                alias_name = reference[1:]
                # Look for anchor in data structure
                if data:
                    # Search for anchor in nested structure
                    anchor_value = self._find_yaml_anchor(data, alias_name)
                    if anchor_value is not None:
                        return anchor_value
                # Check if it's a file reference
                if base_path:
                    yaml_path = Path(base_path)
                    if yaml_path.exists():
                        with open(yaml_path, encoding='utf-8') as f:
                            content = f.read()
                            # Check for multi-document YAML
                            if '---' in content:
                                yaml_data = list(yaml.safe_load_all(content))
                            else:
                                yaml_data = yaml.safe_load(content)
                            anchor_value = self._find_yaml_anchor(yaml_data, alias_name)
                            if anchor_value is not None:
                                return anchor_value
            # Check if reference is an anchor (starts with &)
            elif reference.startswith('&'):
                anchor_name = reference[1:]
                if data:
                    anchor_value = self._find_yaml_anchor(data, anchor_name)
                    if anchor_value is not None:
                        return anchor_value
            raise SerializationError(f"Could not resolve YAML reference: {reference}")
        except ImportError:
            raise SerializationError(
                f"YAML reference resolution requires PyYAML. "
                f"Install with: pip install pyyaml. "
                f"Reference: {reference}"
            )
        except Exception as e:
            raise SerializationError(f"YAML reference resolution failed: {e}") from e

    def _find_yaml_anchor(self, data: Any, anchor_name: str) -> Any:
        """
        Find YAML anchor value in data structure.
        This is a simplified implementation - full YAML anchor resolution
        would require a YAML parser that preserves anchor information.
        """
        # Basic search in dict/list structures
        if isinstance(data, dict):
            # Check if this dict has the anchor as a key
            if anchor_name in data:
                return data[anchor_name]
            # Recursively search
            for value in data.values():
                result = self._find_yaml_anchor(value, anchor_name)
                if result is not None:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self._find_yaml_anchor(item, anchor_name)
                if result is not None:
                    return result
        return None

    def _resolve_toml_reference(
        self,
        reference: str,
        base_path: str | Path | None,
        data: Any | None
    ) -> Any:
        """
        Resolve TOML reference (inline references).
        Attempts to parse as TOML if tomli library is available.
        TOML references are typically file-based.
        """
        # Try to use TOML parser if available
        try:
            import tomli
            # TOML references are typically file-based
            if base_path:
                toml_path = Path(base_path) / reference
                if toml_path.exists():
                    with open(toml_path, 'rb') as f:
                        return tomli.load(f)
        except ImportError:
            pass
        raise SerializationError(
            f"TOML reference resolution requires tomli library. "
            f"Install with: pip install tomli. Reference: {reference}"
        )

    def _resolve_file_reference(
        self,
        file_path: str,
        base_path: str | Path | None
    ) -> Any:
        """
        Resolve file reference with security validation.
        Args:
            file_path: File path (relative or absolute)
            base_path: Base path for relative references
        Returns:
            File contents (parsed)
        """
        # Security: normalize URI-style inputs first (e.g. file:///etc/passwd).
        if "://" in file_path:
            parsed = urlparse(file_path)
            if parsed.scheme != "file":
                raise SerializationError(f"Path traversal detected: {file_path}")
            file_path = parsed.path or ""

        # Security: Validate path (prevent path traversal)
        path = Path(file_path)
        if base_path:
            base = Path(base_path).resolve()
            resolved = (base / path).resolve()
            # Ensure resolved path is within base path
            if not str(resolved).startswith(str(base)):
                raise SerializationError(f"Path traversal detected: {file_path}")
            path = resolved
        else:
            path = path.resolve()
        # Security: Validate scheme (only allow file://)
        if not path.exists():
            raise SerializationError(f"File not found: {path}")
        # Load and parse file
        # Auto-detect format and parse accordingly
        return self._load_file_with_auto_detect(path)

    def detect_references(self, data: Any, reference_type: str = "json") -> list[dict[str, Any]]:
        """
        Detect all references in data.
        Args:
            data: Data to scan for references
            reference_type: type of references to detect
        Returns:
            list of detected references with their paths
        """
        references = []
        if reference_type.lower() == "json":
            references = self._detect_json_references(data)
        elif reference_type.lower() == "xml":
            references = self._detect_xml_references(data)
        elif reference_type.lower() == "yaml":
            references = self._detect_yaml_references(data)
        elif reference_type.lower() == "toml":
            references = self._detect_toml_references(data)
        return references

    def _detect_json_references(self, data: Any, path: str = "") -> list[dict[str, Any]]:
        """Detect JSON $ref references."""
        references = []
        if isinstance(data, dict):
            if "$ref" in data:
                references.append({
                    "type": "json",
                    "path": path,
                    "reference": data["$ref"]
                })
            for key, value in data.items():
                new_path = f"{path}/{key}" if path else f"/{key}"
                references.extend(self._detect_json_references(value, new_path))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_path = f"{path}/{i}"
                references.extend(self._detect_json_references(item, new_path))
        return references

    def _detect_xml_references(self, data: Any) -> list[dict[str, Any]]:
        """Detect XML @href references."""
        references = []
        # Basic detection for dict-like structures
        if isinstance(data, dict):
            # Check for @href, xlink:href, href attributes
            for key, value in data.items():
                if key in ('@href', 'xlink:href', 'href') and isinstance(value, str):
                    references.append({
                        "type": "xml",
                        "path": "",
                        "reference": value
                    })
                elif isinstance(value, (dict, list)):
                    references.extend(self._detect_xml_references(value))
        elif isinstance(data, list):
            for item in data:
                references.extend(self._detect_xml_references(item))
        return references

    def _detect_yaml_references(self, data: Any) -> list[dict[str, Any]]:
        """Detect YAML *anchor and &anchor references."""
        references = []
        # Basic detection for dict-like structures
        # YAML anchors/aliases are typically represented as special keys
        if isinstance(data, dict):
            for key, value in data.items():
                # Check for anchor markers (* for alias, & for anchor)
                if isinstance(key, str):
                    if key.startswith('*') or key.startswith('&'):
                        references.append({
                            "type": "yaml",
                            "path": "",
                            "reference": key
                        })
                if isinstance(value, (dict, list)):
                    references.extend(self._detect_yaml_references(value))
        elif isinstance(data, list):
            for item in data:
                references.extend(self._detect_yaml_references(item))
        return references

    def _detect_toml_references(self, data: Any) -> list[dict[str, Any]]:
        """Detect TOML inline references."""
        references = []
        # TOML references are typically file-based or table references
        # Basic detection for dict-like structures
        if isinstance(data, dict):
            for key, value in data.items():
                # Check for reference-like patterns
                if isinstance(key, str) and isinstance(value, str):
                    # Simple heuristic: if value looks like a file path or table reference
                    if value.startswith('./') or value.startswith('../') or '/' in value:
                        references.append({
                            "type": "toml",
                            "path": key,
                            "reference": value
                        })
                elif isinstance(value, (dict, list)):
                    references.extend(self._detect_toml_references(value))
        elif isinstance(data, list):
            for item in data:
                references.extend(self._detect_toml_references(item))
        return references

    def clear_cache(self) -> None:
        """Clear reference cache."""
        self._cache.clear()
        self._circular_detection.clear()

    def _resolve_http_reference(self, url: str) -> Any:
        """
        Resolve HTTP/HTTPS reference using xwsystem's HTTP client.
        Args:
            url: HTTP/HTTPS URL to fetch
        Returns:
            Parsed data from URL
        Raises:
            SerializationError: If HTTP request fails or parsing fails
        """
        # Security: Validate URL scheme
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise SerializationError(f"Invalid URL scheme: {parsed.scheme}")
        try:
            # Use xwsystem's HTTP client (with retry mechanisms, connection pooling, etc.)
            from exonware.xwsystem.http_client import HttpClient, HttpError
            with HttpClient(timeout=30.0) as client:
                response = client.get(url)
                # Check for HTTP errors (xwsystem's HttpClient may handle retries, but we check final status)
                if response.status_code >= 400:
                    raise HttpError(
                        f"HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code,
                        response_data=response.text
                    )
                content = response.content
                content_type = response.headers.get('Content-Type', '').lower()
                # Auto-detect format from Content-Type or URL
                if 'json' in content_type or url.endswith('.json'):
                    return xw_json.loads(content.decode('utf-8'))
                elif 'yaml' in content_type or 'yml' in content_type or url.endswith(('.yaml', '.yml')):
                    try:
                        import yaml
                        return yaml.safe_load(content.decode('utf-8'))
                    except ImportError:
                        raise SerializationError(
                            "YAML parsing requires PyYAML. Install with: pip install pyyaml"
                        )
                elif 'xml' in content_type or url.endswith('.xml'):
                    try:
                        import xml.etree.ElementTree as ET
                        return ET.fromstring(content.decode('utf-8'))
                    except Exception as e:
                        raise SerializationError(f"Failed to parse XML: {e}") from e
                else:
                    # Default to JSON
                    return xw_json.loads(content.decode('utf-8'))
        except HttpError as e:
            raise SerializationError(f"HTTP request failed for {url}: {e}") from e
        except ImportError:
            # Fallback to urllib if xwsystem HTTP client not available
            try:
                import urllib.request
                import urllib.error
                with urllib.request.urlopen(url, timeout=30) as response:
                    content = response.read()
                    content_type = response.headers.get('Content-Type', '').lower()
                    # Auto-detect format from Content-Type or URL
                    if 'json' in content_type or url.endswith('.json'):
                        return xw_json.loads(content.decode('utf-8'))
                    elif 'yaml' in content_type or 'yml' in content_type or url.endswith(('.yaml', '.yml')):
                        try:
                            import yaml
                            return yaml.safe_load(content.decode('utf-8'))
                        except ImportError:
                            raise SerializationError(
                                "YAML parsing requires PyYAML. Install with: pip install pyyaml"
                            )
                    elif 'xml' in content_type or url.endswith('.xml'):
                        try:
                            import xml.etree.ElementTree as ET
                            return ET.fromstring(content.decode('utf-8'))
                        except Exception as e:
                            raise SerializationError(f"Failed to parse XML: {e}") from e
                    else:
                        # Default to JSON
                        return xw_json.loads(content.decode('utf-8'))
            except urllib.error.URLError as e:
                raise SerializationError(f"Failed to fetch URL {url}: {e}") from e
        except Exception as e:
            raise SerializationError(f"HTTP reference resolution failed: {e}") from e

    def _load_file_with_auto_detect(self, file_path: Path) -> Any:
        """
        Load file with automatic format detection.
        Args:
            file_path: Path to file
        Returns:
            Parsed data
        """
        suffix = file_path.suffix.lower()
        # Try to use AutoSerializer if available
        try:
            from exonware.xwsystem.io.serialization.auto_serializer import AutoSerializer
            auto_serializer = AutoSerializer()
            return auto_serializer.auto_load_file(file_path)
        except ImportError:
            # Fallback to manual format detection
            pass
        # Manual format detection
        if suffix in ('.json', '.json5'):
            with open(file_path, encoding='utf-8') as f:
                return xw_json.load(f)
        elif suffix in ('.yaml', '.yml'):
            try:
                import yaml
                with open(file_path, encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except ImportError:
                raise SerializationError(
                    "YAML parsing requires PyYAML. Install with: pip install pyyaml"
                )
        elif suffix == '.xml':
            try:
                import xml.etree.ElementTree as ET
                return ET.parse(file_path).getroot()
            except Exception as e:
                raise SerializationError(f"Failed to parse XML: {e}") from e
        elif suffix == '.toml':
            try:
                import tomli
                with open(file_path, 'rb') as f:
                    return tomli.load(f)
            except ImportError:
                raise SerializationError(
                    "TOML parsing requires tomli. Install with: pip install tomli"
                )
        else:
            # Default to JSON
            with open(file_path, encoding='utf-8') as f:
                return xw_json.load(f)
