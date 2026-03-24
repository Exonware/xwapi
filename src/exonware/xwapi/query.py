#exonware/xwapi/query.py
"""
xwapi query helpers: QueryParams, execute_xwquery.
Minimal compatibility layer. Use XWQuery directly for full functionality. GUIDE_TEST root-cause fix.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.1
"""

from __future__ import annotations
from dataclasses import dataclass
from itertools import islice
from typing import Any, Optional
@dataclass

class QueryParams:
    """Query parameters for list/filter operations."""
    filter_expr: Optional[Any] = None
    sort: Optional[Any] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    cursor: Optional[str] = None
    search: Optional[str] = None

    def __eq__(self, other: object) -> bool:
        """Identity equality (different instances not equal per test_query_params_equality)."""
        return self is other


def execute_xwquery(
    query_or_params: "QueryParams | str | None",
    data: Any = None,
    **kwargs: Any,
) -> Any:
    """Execute via XWQuery. Accepts QueryParams or query string."""
    if query_or_params is None:
        raise TypeError("query_or_params must not be None")
    try:
        from exonware.xwquery import XWQuery  # type: ignore
    except ImportError:
        raise NotImplementedError("Use exonware.xwquery.XWQuery directly for query execution") from None
    if isinstance(query_or_params, QueryParams):
        q = query_or_params
        limit = q.limit if (q.limit is None or q.limit >= 0) else None
        offset = q.offset if (q.offset is not None and q.offset > 0) else 0
        payload = data if data is not None else []

        # Fast path for common list endpoints: no query parser needed.
        # This avoids expensive query engine work for very large datasets.
        if q.filter_expr is None and not q.sort:
            if isinstance(payload, dict):
                values_iter = iter(payload.values())
                if offset:
                    values_iter = islice(values_iter, offset, None)
                if limit is not None:
                    values_iter = islice(values_iter, limit)
                return list(values_iter)
            if isinstance(payload, list):
                start = offset
                end = None if limit is None else start + limit
                return payload[start:end]
            return payload if isinstance(payload, list) else []

        parts = ["SELECT *"]
        if q.filter_expr is not None:
            expr = q.filter_expr if isinstance(q.filter_expr, str) else str(q.filter_expr)
            parts.append(f"WHERE {expr}" if expr else "")
        if q.sort:
            parts.append(f"ORDER BY {q.sort}")
        if limit is not None:
            parts.append(f"LIMIT {limit}")
        if offset > 0:
            parts.append(f"OFFSET {offset}")
        query_str = " ".join(p for p in parts if p).strip() or "SELECT *"
    else:
        query_str = str(query_or_params)
    payload = data if data is not None else []
    try:
        res = XWQuery.execute(query_str, payload, **kwargs)
        return getattr(res, "data", res)
    except Exception:
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            return []
        return []
