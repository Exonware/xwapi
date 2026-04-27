#exonware/xwapi/src/exonware/xwapi/client/runtime_gate.py
"""
Concrete runtime gating for :class:`exonware.xwapi.client.xwclient.XWApiAgent`.

``api_stop`` / ``api_pause`` must actually block action execution (not only flip flags for status).
Lifecycle actions stay callable so operators can inspect and recover.
"""

from __future__ import annotations

from typing import Any

from exonware.xwaction.errors import XWActionError

# Actions that must remain callable while the agent is paused or fully stopped.
RUNTIME_EXEMPT_API_NAMES: frozenset[str] = frozenset(
    {
        "api_health",
        "api_status",
        "api_start",
        "api_stop",
        "api_restart",
        "api_pause",
        "api_resume",
    }
)


def agent_runtime_blocks_actions(agent: Any) -> bool:
    """Return True when non-exempt XWApi actions must not run."""
    if agent is None:
        return False
    if not bool(getattr(agent, "_runtime_active", True)):
        return True
    if bool(getattr(agent, "_runtime_paused", False)):
        return True
    return False


def action_api_name(fn: Any) -> str:
    """Resolve OpenAPI-style ``api_name`` from a bound action or wrapper function."""
    xw = getattr(fn, "xwaction", None)
    if xw is None:
        inner = getattr(fn, "__func__", fn)
        xw = getattr(inner, "xwaction", None)
    if xw is not None:
        for key in ("_api_name", "api_name"):
            v = getattr(xw, key, None)
            if v:
                return str(v)
    inner = getattr(fn, "__func__", fn)
    return str(getattr(inner, "__name__", "unknown"))


def ensure_xwapi_runtime_allows_action(agent: Any, fn: Any) -> None:
    """
    Raise :class:`XWActionError` when ``agent`` is paused/stopped and ``fn`` is not exempt.

    Used by the native agent engine and by XWApiAgent method wrappers so both
    ``action(**kwargs)`` and ``action.execute(...)`` paths stay consistent.
    """
    api_name = action_api_name(fn)
    if api_name in RUNTIME_EXEMPT_API_NAMES:
        return
    if not agent_runtime_blocks_actions(agent):
        return
    paused = bool(getattr(agent, "_runtime_paused", False))
    active = bool(getattr(agent, "_runtime_active", True))
    if paused and active:
        state = "paused"
        remedy = "api_resume or api_start"
    else:
        state = "stopped"
        remedy = "api_start or api_restart"
    raise XWActionError(
        f"Agent «{getattr(agent, '_name', '?')}» runtime is {state}; "
        f"action «{api_name}» is blocked. Use {remedy} (see /api_status).",
        details={
            "state": state,
            "api_name": api_name,
            "remedy": remedy,
        },
    )
