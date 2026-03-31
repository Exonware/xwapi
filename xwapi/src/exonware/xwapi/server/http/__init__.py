#!/usr/bin/env python3
"""
HTTP adapter helpers for engine-specific response rendering.
"""

from .error_adapter import starlette_json_response_from_xwapi_error

__all__ = ["starlette_json_response_from_xwapi_error"]
