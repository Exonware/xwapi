#exonware/xwapi/tests/1.unit/test_query.py
"""
Unit tests for xwapi query module — QueryParams and execute_xwquery.
"""

from __future__ import annotations

import pytest


@pytest.mark.xwapi_unit
class TestQueryParams:

    def test_defaults(self):
        from exonware.xwapi.query import QueryParams
        q = QueryParams()
        assert q.filter_expr is None
        assert q.sort is None
        assert q.limit is None
        assert q.offset is None
        assert q.cursor is None
        assert q.search is None

    def test_identity_equality(self):
        from exonware.xwapi.query import QueryParams
        q1 = QueryParams()
        q2 = QueryParams()
        assert q1 == q1
        assert q1 != q2


@pytest.mark.xwapi_unit
class TestExecuteXWQuery:

    def test_none_query_raises_type_error(self):
        from exonware.xwapi.query import execute_xwquery
        with pytest.raises(TypeError):
            execute_xwquery(None)

    def test_fast_path_list_no_filter(self):
        from exonware.xwapi.query import execute_xwquery, QueryParams
        data = [{"id": 1}, {"id": 2}, {"id": 3}]
        result = execute_xwquery(QueryParams(limit=2), data)
        assert result == [{"id": 1}, {"id": 2}]

    def test_fast_path_list_offset(self):
        from exonware.xwapi.query import execute_xwquery, QueryParams
        data = [{"id": 1}, {"id": 2}, {"id": 3}]
        result = execute_xwquery(QueryParams(offset=1, limit=2), data)
        assert result == [{"id": 2}, {"id": 3}]

    def test_fast_path_dict_no_filter(self):
        from exonware.xwapi.query import execute_xwquery, QueryParams
        data = {"a": {"id": 1}, "b": {"id": 2}, "c": {"id": 3}}
        result = execute_xwquery(QueryParams(limit=2), data)
        assert len(result) == 2

    def test_fast_path_no_limit(self):
        from exonware.xwapi.query import execute_xwquery, QueryParams
        data = [1, 2, 3]
        result = execute_xwquery(QueryParams(), data)
        assert result == [1, 2, 3]
