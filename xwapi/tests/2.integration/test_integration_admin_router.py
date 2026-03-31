from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from exonware.xwaction import XWAction
from exonware.xwapi.server import XWApiServer
from exonware.xwapi.server.admin.router import register_admin_endpoints


@pytest.mark.xwapi_integration
def test_admin_router_status_exposes_pause_and_actions() -> None:
    """Secondary admin router should expose production status fields."""
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="admin_router_echo", profile="endpoint")
    def echo() -> dict[str, str]:
        return {"ok": "yes"}

    assert server.register_action(echo, path="/echo-admin", method="GET") is True
    register_admin_endpoints(server.app, server, prefix="/ops", tag="Operations")
    client = TestClient(server.app)

    response = client.get("/ops/status")
    body = response.json()
    assert response.status_code == 200
    assert "pause" in body
    assert "actions_count" in body
    assert body["actions_count"] >= 1


@pytest.mark.xwapi_integration
def test_admin_router_pause_resume_matches_server_policy() -> None:
    """Router pause/resume endpoints should enforce and clear pause policy."""
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="admin_router_pause_target", profile="endpoint")
    def echo() -> dict[str, str]:
        return {"ok": "yes"}

    assert server.register_action(echo, path="/echo-router-pause", method="GET") is True
    register_admin_endpoints(server.app, server, prefix="/ops", tag="Operations")
    client = TestClient(server.app)

    assert client.get("/echo-router-pause").status_code == 200

    pause_resp = client.post("/ops/pause", json={"endpoint": "/echo-router-pause", "method": "GET"})
    assert pause_resp.status_code == 200
    assert pause_resp.json()["status"] == "paused"
    assert client.get("/echo-router-pause").status_code == 503

    resume_resp = client.post("/ops/resume", json={"endpoint": "/echo-router-pause", "method": "GET"})
    assert resume_resp.status_code == 200
    assert resume_resp.json()["status"] == "resumed"
    assert client.get("/echo-router-pause").status_code == 200


@pytest.mark.xwapi_integration
def test_admin_router_control_endpoints_reachable_during_global_pause() -> None:
    """Secondary admin endpoints must stay available during global pause."""
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="admin_router_global_target", profile="endpoint")
    def echo() -> dict[str, str]:
        return {"ok": "yes"}

    assert server.register_action(echo, path="/echo-global-router", method="GET") is True
    register_admin_endpoints(server.app, server, prefix="/ops", tag="Operations")
    client = TestClient(server.app)

    pause_resp = client.post("/ops/pause", json={})
    assert pause_resp.status_code == 200
    assert pause_resp.json()["status"] == "paused"

    blocked = client.get("/echo-global-router")
    assert blocked.status_code == 503

    status_resp = client.get("/ops/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["pause"]["global_paused"] is True

    log_resp = client.post("/ops/log", json={"level": "warning", "message": "ops alive"})
    assert log_resp.status_code == 200
    assert log_resp.json()["level"] == "WARNING"
    assert log_resp.json()["message"] == "ops alive"


@pytest.mark.xwapi_integration
def test_admin_router_start_stop_semantics_match_server_admin_contract() -> None:
    """Start/stop from secondary router should mirror xwserver admin semantics."""
    server = XWApiServer(engine="fastapi")
    register_admin_endpoints(server.app, server, prefix="/ops", tag="Operations")
    client = TestClient(server.app)

    start_resp = client.post("/ops/start")
    assert start_resp.status_code == 200
    assert start_resp.json()["status"] == "info"

    stop_resp = client.post("/ops/stop")
    assert stop_resp.status_code == 200
    assert stop_resp.json()["status"] == "already_stopped"
