#exonware/xwapi/serialization.py
"""
xwapi serialization (re-export from common.serialization).
GUIDE_TEST root-cause fix.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.4
"""

from exonware.xwapi.common.serialization import (
    save_openapi_settings,
    load_openapi_settings,
    create_custom_format_response,
    get_content_type,
)
__all__ = [
    "save_openapi_settings",
    "load_openapi_settings",
    "create_custom_format_response",
    "get_content_type",
]
