# exonware/xwapi/tests/1.unit/server_tests/test_server_control_plane.py
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from exonware.xwapi.server import XWApiServer


@pytest.mark.xwapi_unit
def test_control_plane_registers_private_start_stop_actions() -> None:
    server = XWApiServer(engine="fastapi")
    start_action = server.resolve_control_action("start")
    stop_action = server.resolve_control_action("stop")
    kill_action = server.resolve_control_action("kill")
    assert start_action is not None
    assert stop_action is not None
    assert kill_action is not None
    assert server.resolve_control_action("run") is None
    assert bool(getattr(start_action.xwaction, "expose_http", True)) is False
    assert bool(getattr(stop_action.xwaction, "expose_http", True)) is False
    assert bool(getattr(kill_action.xwaction, "expose_http", True)) is False


@pytest.mark.xwapi_unit
def test_http_bridge_exposes_safe_commands_only() -> None:
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    # Dangerous commands stay private by design.
    assert client.post("/server/run", json={}).status_code == 404
    assert client.post("/server/kill", json={}).status_code == 404

    started = client.post("/server/start", json={})
    assert started.status_code == 200
    assert started.json().get("status") == "started"

    stopped = client.post("/server/stop", json={})
    assert stopped.status_code == 200
    assert stopped.json().get("status") == "stopped"
