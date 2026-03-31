#exonware/xwapi/common/serialization.py
"""
OpenAPI settings serialization (save/load, content-type, format response).
Uses xwsystem Json/Yaml serializers. GUIDE_TEST root-cause fix.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.2
"""

from __future__ import annotations
from pathlib import Path
from typing import Any

from exonware.xwsystem import JsonSerializer, YamlSerializer

def save_openapi_settings(data: dict[str, Any], path: str | Path) -> None:
    """Save OpenAPI settings to JSON or YAML file (by extension)."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        ser = YamlSerializer()
    else:
        ser = JsonSerializer()
    ser.save_file(data, path)


def load_openapi_settings(path: str | Path) -> dict[str, Any]:
    """Load OpenAPI settings from JSON or YAML file (by extension)."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        ser = YamlSerializer()
    else:
        ser = JsonSerializer()
    out = ser.load_file(path)
    return out if isinstance(out, dict) else {"openapi": "3.1.0", "info": out}


def create_custom_format_response(data: Any, content_type: str) -> Any:
    """Return data for application/json (FastAPI handles it); minimal handling otherwise."""
    if "json" in (content_type or "").lower():
        return data
    return data


def get_content_type(request: Any) -> str:
    """Content type from Accept header; default application/json."""
    h = getattr(request, "headers", None) or {}
    if isinstance(h, dict):
        raw = h.get("accept") or h.get("Accept") or ""
    else:
        get = getattr(h, "get", None)
        raw = (get("accept") or get("Accept") or "") if callable(get) else ""
    if not raw or not isinstance(raw, str):
        return "application/json"
    part = raw.split(",")[0].strip().split(";")[0].strip()
    return part or "application/json"
