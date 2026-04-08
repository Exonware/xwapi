# exonware/xwapi/src/exonware/xwapi/server/engines/http_action_bridge.py
"""
Shared invocation of XWAction objects for optional HTTP server engines.

xwaction ships FastAPI/Flask engines; other frameworks use NativeActionEngine here.
"""

from __future__ import annotations

from typing import Any


class ActionExecutionError(Exception):
    """Raised when NativeActionEngine reports a failed ActionResult."""

    pass


async def invoke_action_for_http(
    action: Any,
    *,
    source_engine: str,
    parameters: dict[str, Any],
) -> Any:
    """
    Execute *action* (XWAction or IAction) with flat **parameters** (query + JSON body).
    """
    from exonware.xwaction.context import ActionContext
    from exonware.xwaction.engines.native import NativeActionEngine

    ctx = ActionContext(actor="http", source=source_engine)
    native = NativeActionEngine()
    result = native.execute(action, ctx, None, **parameters)
    if hasattr(result, "success") and not result.success:
        raise ActionExecutionError(str(getattr(result, "error", "action failed")))
    out = getattr(result, "data", result)
    if hasattr(out, "__await__"):
        out = await out  # type: ignore[misc]
    return out


def merge_query_and_json(
    query: dict[str, Any],
    body: dict[str, Any],
) -> dict[str, Any]:
    """Merge query params and JSON body (body wins on key clash)."""
    merged = {**query, **body}
    return merged
