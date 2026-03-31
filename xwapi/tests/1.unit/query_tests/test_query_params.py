#exonware/xwapi/tests/1.unit/query_tests/test_query_params.py
"""
Unit tests for QueryParams and query execution.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
"""

from __future__ import annotations
import pytest
from unittest.mock import Mock, MagicMock
from exonware.xwapi.query import QueryParams
from exonware.xwapi.server.engines.fastapi import get_query_params
@pytest.mark.xwapi_unit

def test_query_params_initialization():
    """Test QueryParams initialization."""
    params = QueryParams(
        filter_expr="name:test",
        sort="name",
        limit=10,
        offset=0
    )
    assert params.filter_expr == "name:test"
    assert params.sort == "name"
    assert params.limit == 10
    assert params.offset == 0
@pytest.mark.xwapi_unit

def test_query_params_defaults():
    """Test QueryParams with default values."""
    params = QueryParams()
    assert params.filter_expr is None
    assert params.sort is None
    assert params.limit is None
    assert params.offset is None
@pytest.mark.xwapi_unit

def test_get_query_params_from_request():
    """Test extracting query params using FastAPI dependency."""
    # get_query_params returns a dict; call with keyword arguments
    params = get_query_params(
        filter='{"name":"test"}',
        sort="name",
        limit=10,
        offset=0,
    )
    assert params is not None
    assert isinstance(params, dict)
    assert params.get("filter") == '{"name":"test"}'
    assert params.get("sort") == "name"
    assert params.get("limit") == 10
    assert params.get("offset") == 0
