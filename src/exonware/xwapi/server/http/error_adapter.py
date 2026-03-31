#!/usr/bin/env python3
"""
HTTP response adapter for XWAPIError objects.
"""

from __future__ import annotations

from typing import Any, Optional

from starlette.responses import JSONResponse

from exonware.xwapi.errors import XWAPIError, xwapi_error_to_http_parts


def starlette_json_response_from_xwapi_error(
    error: XWAPIError,
    request: Optional[Any] = None,
    *,
    include_details: bool = True,
    extra_headers: Optional[dict[str, str]] = None,
) -> JSONResponse:
    """
    Render an XWAPIError as Starlette-compatible JSONResponse.
    Keeps engine/protocol mapping in errors.py and rendering in adapter layer.
    """
    body, status_code, headers = xwapi_error_to_http_parts(
        error,
        request=request,
        include_details=include_details,
        extra_headers=extra_headers,
    )
    return JSONResponse(status_code=status_code, content=body, headers=headers)
