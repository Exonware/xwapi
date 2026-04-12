#!/usr/bin/env python3
"""
OpenAPI merge/export/validation for *published* exposable actions (engine-agnostic helpers).

Engine-specific document generation still lives in HTTP engines (FastAPI, …).

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.7
"""

from typing import Any, Optional
from pathlib import Path


def merge_openapi_schemas(schemas: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Merge multiple OpenAPI schemas into one.
    Combines paths, components, and tags from multiple schemas.
    Handles conflicts by preferring later schemas.
    Args:
        schemas: List of OpenAPI schema dictionaries
    Returns:
        Merged OpenAPI schema
    """
    if not schemas:
        return {
            "openapi": "3.1.0",
            "info": {"title": "API", "version": "1.0.0"},
            "paths": {},
            "components": {"schemas": {}, "securitySchemes": {}},
        }
    # Start with first schema
    merged = schemas[0].copy()
    # Merge subsequent schemas
    for schema in schemas[1:]:
        # Merge paths
        if "paths" in schema:
            merged.setdefault("paths", {}).update(schema["paths"])
        # Merge components
        if "components" in schema:
            merged.setdefault("components", {})
            # Merge schemas
            if "schemas" in schema["components"]:
                merged["components"].setdefault("schemas", {}).update(schema["components"]["schemas"])
            # Merge security schemes
            if "securitySchemes" in schema["components"]:
                merged["components"].setdefault("securitySchemes", {}).update(schema["components"]["securitySchemes"])
            # Merge other components
            for key in schema["components"]:
                if key not in ["schemas", "securitySchemes"]:
                    merged["components"].setdefault(key, {}).update(schema["components"][key])
        # Merge tags
        if "tags" in schema:
            merged.setdefault("tags", []).extend(schema.get("tags", []))
            # Deduplicate tags
            seen = set()
            unique_tags = []
            for tag in merged["tags"]:
                tag_name = tag.get("name") if isinstance(tag, dict) else tag
                if tag_name not in seen:
                    seen.add(tag_name)
                    unique_tags.append(tag)
            merged["tags"] = unique_tags
    return merged


def validate_openapi_schema(schema: dict[str, Any]) -> tuple[bool, str | None]:
    """
    Validate OpenAPI schema structure.
    Checks for required fields and basic structure compliance.
    Args:
        schema: OpenAPI schema dictionary
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    if "openapi" not in schema:
        return False, "Missing 'openapi' field"
    if "info" not in schema:
        return False, "Missing 'info' field"
    if "title" not in schema["info"]:
        return False, "Missing 'info.title' field"
    if "version" not in schema["info"]:
        return False, "Missing 'info.version' field"
    # Check OpenAPI version
    openapi_version = schema["openapi"]
    if not openapi_version.startswith("3."):
        return False, f"Unsupported OpenAPI version: {openapi_version}"
    # Check paths exist (may be empty)
    if "paths" not in schema:
        schema["paths"] = {}
    # Check components exist (may be empty)
    if "components" not in schema:
        schema["components"] = {"schemas": {}, "securitySchemes": {}}
    return True, None


def export_openapi_schema(
    app: Any,  # Engine-agnostic: accepts any framework app
    format: str = "json",
    path: str | None = None
) -> str | dict[str, Any]:
    """
    Export OpenAPI schema from framework app (engine-agnostic).
    Delegates to engine-specific implementations for schema extraction.
    Uses XWData for flexible format support if path is provided.
    Args:
        app: Framework application instance (engine-specific)
        format: Export format ("json", "yaml", "toml", "xml", etc.)
        path: Optional file path to save schema (uses XWData for format conversion)
    Returns:
        OpenAPI schema as string (YAML/XML/etc.) or dict (JSON)
    """
    app_type_name = type(app).__module__ + "." + type(app).__name__
    # Extract schema via capability-based detection.
    if hasattr(app, "openapi"):
        schema = app.openapi()
    else:
        if hasattr(app, "generate_openapi"):
            schema = app.generate_openapi()
        else:
            raise NotImplementedError(f"OpenAPI schema extraction not implemented for engine type: {app_type_name}")
    # If path provided, use XWData to save in any format
    if path:
        try:
            from exonware.xwdata import XWData
            # Use XWData directly to save
            xwdata = XWData(schema)
            xwdata.save(path)  # Auto-detects format from extension
            # Return appropriate type based on format
            if format.lower() == "json":
                return schema
            else:
                # For non-JSON, load back as string
                try:
                    with open(path) as f:
                        return f.read()
                except Exception:
                    return schema
        except ImportError:
            # Fallback: use xwsystem codec
            from exonware.xwsystem.io.codec.registry import get_registry
            registry = get_registry()
            codec = registry.get_by_id(format or "json")
            if codec:
                serialized = codec.encode(schema)
                path_obj = Path(path)
                if not path_obj.parent.exists():
                    path_obj.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(serialized, str):
                    path_obj.write_text(serialized, encoding='utf-8')
                elif isinstance(serialized, bytes):
                    path_obj.write_bytes(serialized)
                return schema if format.lower() == "json" else serialized
            return schema
    # No path, return in-memory representation
    if format.lower() == "yaml":
        try:
            from exonware.xwsystem.io.serialization import YamlSerializer
            return YamlSerializer().encode(schema, options={"default_flow_style": False})
        except ImportError:
            # YAML not available, fallback to JSON dict
            return schema
    else:
        return schema


def add_openapi_metadata(schema: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    """
    Add custom metadata to OpenAPI schema.
    Metadata is added to info.x-* extensions.
    Args:
        schema: OpenAPI schema
        metadata: Metadata dictionary
    Returns:
        Schema with added metadata
    """
    if "info" not in schema:
        schema["info"] = {}
    for key, value in metadata.items():
        schema["info"][f"x-{key}"] = value
    return schema


def get_openapi_version(schema: dict[str, Any]) -> str | None:
    """
    Get OpenAPI version from schema.
    Args:
        schema: OpenAPI schema
    Returns:
        OpenAPI version string (e.g., "3.1.0") or None
    """
    return schema.get("openapi")
