#exonware/xwapi/action.py
"""
Helpers to wire *exposable actions* (XWAction) onto HTTP apps.

``register_action_endpoint`` uses the FastAPI action engine by default; other transports
(bots, console, alternate engines) use the same xwaction registries with different adapters.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.12
"""

from __future__ import annotations
from typing import Any


def register_action_endpoint(
    app: Any,
    action: Any,
    *,
    path: str | None = None,
    method: str = "POST",
) -> bool:
    """Register an XWAction as a FastAPI endpoint. Uses xwaction FastAPIActionEngine."""
    try:
        from exonware.xwaction.engines import action_engine_registry
        from exonware.xwaction.engines.fastapi import FastAPIActionEngine
    except ImportError:
        return False
    engine = action_engine_registry.get_engine("fastapi")
    if not engine:
        engine = FastAPIActionEngine()
        action_engine_registry.register(engine)
    return engine.register_action(action, app, path=path or f"/{getattr(action, 'api_name', 'unknown')}", method=method)


def create_action_context_dependency(request: Any) -> Any:
    """FastAPI Depends(): build ActionContext from Request (trace_id, path, method)."""
    from exonware.xwaction.context import ActionContext
    trace_id = getattr(getattr(request, "state", None), "trace_id", None)
    path = getattr(getattr(request, "url", None), "path", "unknown")
    method = getattr(request, "method", "GET")
    return ActionContext(
        actor="request",
        source=path,
        trace_id=trace_id,
        metadata={"method": method, "path": path},
    )
