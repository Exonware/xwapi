# exonware/xwapi/tests/1.unit/client_tests/test_client_engines_registry.py
"""Client-side agent engine registry (publish/consume symmetry surface)."""

from __future__ import annotations

import pytest

from exonware.xwapi.client.engines import (
    NativeAgentEngine,
    api_agent_engine_registry,
)


@pytest.mark.xwapi_unit
def test_agent_engine_registry_has_native_default() -> None:
    eng = api_agent_engine_registry.get_engine("native")
    assert eng is not None
    assert isinstance(eng, NativeAgentEngine)


@pytest.mark.xwapi_unit
def test_agent_engine_registry_list_contains_native() -> None:
    names = api_agent_engine_registry.list_engines()
    assert "native" in names


@pytest.mark.xwapi_unit
def test_native_agent_engine_discovers_xwaction_methods() -> None:
    from exonware.xwaction import XWAction
    from exonware.xwapi import XWApiAgent

    class SampleAgent(XWApiAgent):
        @XWAction(operationId="ping", profile="endpoint")
        def ping(self) -> str:
            return "pong"

    agent = SampleAgent(name="reg_test", auto_discover=True)
    native = NativeAgentEngine()
    found = native.discover_actions(agent)
    names = {getattr(f, "__name__", str(f)) for f in found}
    assert "ping" in names
