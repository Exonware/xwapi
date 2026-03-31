#!/usr/bin/env python3
"""
#exonware/xwjson/src/exonware/xwjson/errors.py
Error classes for xwjson.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 07-Jan-2025
"""


class XWJSONError(Exception):
    """Base error for xwjson."""


class XWJSONSerializationError(XWJSONError):
    """Serialization-related errors."""


class XWJSONEncodingError(XWJSONError):
    """Encoding errors."""


class XWJSONDecodingError(XWJSONError):
    """Decoding errors."""


class XWJSONLazyLoadingError(XWJSONError):
    """Lazy loading errors."""


class XWJSONTransactionError(XWJSONError):
    """Transaction errors."""


class XWJSONReferenceError(XWJSONError):
    """Reference resolution errors."""


class XWJSONSchemaError(XWJSONError):
    """Schema validation errors."""
