# exonware/xwapi/tests/1.unit/engines_tests/test_http_action_bridge.py
"""Unit tests for http_action_bridge (optional HTTP engines + NativeActionEngine glue)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from exonware.xwaction.context import ActionResult
from exonware.xwapi.server.engines.http_action_bridge import (
    ActionExecutionError,
    invoke_action_for_http,
    merge_query_and_json,
)


@pytest.mark.xwapi_unit
def test_merge_query_and_json_body_wins_on_overlap() -> None:
    assert merge_query_and_json({"a": "1", "b": "2"}, {"b": "3"}) == {"a": "1", "b": "3"}


@pytest.mark.xwapi_unit
def test_merge_query_and_json_empty() -> None:
    assert merge_query_and_json({}, {}) == {}


@pytest.mark.asyncio
@pytest.mark.xwapi_unit
async def test_invoke_action_for_http_calls_native_success() -> None:
    def fn(name: str = "x") -> dict[str, str]:
        return {"name": name}

    action = SimpleNamespace(func=fn)
    out = await invoke_action_for_http(
        action, source_engine="test_bridge", parameters={"name": "agent"}
    )
    assert out == {"name": "agent"}


@pytest.mark.asyncio
@pytest.mark.xwapi_unit
async def test_invoke_action_for_http_raises_on_failure_result() -> None:
    action = SimpleNamespace(func=lambda: None)

    failed = ActionResult.failure(error="boom")

    with patch(
        "exonware.xwaction.engines.native.NativeActionEngine.execute",
        return_value=failed,
    ):
        with pytest.raises(ActionExecutionError, match="boom"):
            await invoke_action_for_http(
                action, source_engine="test_bridge", parameters={}
            )
