#exonware/xwapi/tests/0.core/test_core_imports.py
"""
Test core imports for xwapi library.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations
import pytest
@pytest.mark.xwapi_core

def test_import_xwapi():
    """Test importing xwapi package."""
    import exonware.xwapi
    assert exonware.xwapi is not None
@pytest.mark.xwapi_core

def test_import_version():
    """Test importing version information."""
    from exonware.xwapi import __version__, __author__, __email__
    assert __version__ is not None
    assert __author__ is not None
    assert __email__ is not None
@pytest.mark.xwapi_core

def test_import_errors():
    """Test importing error classes."""
    from exonware.xwapi.errors import (
        XWAPIError,
        OpenAPIGenerationError,
        FastAPICreationError,
    )
    assert XWAPIError is not None
    assert OpenAPIGenerationError is not None
    assert FastAPICreationError is not None
@pytest.mark.xwapi_core

def test_import_contracts():
    """Test importing contracts."""
    from exonware.xwapi.contracts import (
        HTTPMethod,
        SecurityType,
        IAPIEndpoint,
        IAPIGenerator,
    )
    assert HTTPMethod is not None
    assert SecurityType is not None
    assert IAPIEndpoint is not None
    assert IAPIGenerator is not None
