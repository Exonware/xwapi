from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from exonware.xwaction import XWAction
from exonware.xwapi.server import XWApiServer


@pytest.mark.xwapi_integration
def test_server_pause_resume_endpoint_flow() -> None:
    """Pause/resume admin endpoints should block and restore a route."""
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="echo_pause_test", profile="endpoint")
    def echo() -> dict[str, str]:
        return {"ok": "yes"}

    registered = server.register_action(echo, path="/echo", method="GET")
    assert registered is True

    client = TestClient(server.app)

    baseline = client.get("/echo")
    assert baseline.status_code == 200

    pause_resp = client.post("/server/pause", json={"endpoint": "/echo", "method": "GET"})
    assert pause_resp.status_code == 200
    assert pause_resp.json()["status"] == "paused"

    blocked = client.get("/echo")
    assert blocked.status_code == 503
    assert blocked.json()["code"] == "ServicePaused"

    resume_resp = client.post("/server/resume", json={"endpoint": "/echo", "method": "GET"})
    assert resume_resp.status_code == 200
    assert resume_resp.json()["status"] == "resumed"

    restored = client.get("/echo")
    assert restored.status_code == 200


@pytest.mark.xwapi_integration
def test_server_global_pause_allows_admin_status() -> None:
    """Global pause should block normal routes while admin status remains reachable."""
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="echo_global_pause_test", profile="endpoint")
    def echo() -> dict[str, str]:
        return {"ok": "yes"}

    assert server.register_action(echo, path="/echo-global", method="GET") is True
    client = TestClient(server.app)

    assert client.get("/echo-global").status_code == 200
    pause_resp = client.post("/server/pause", json={})
    assert pause_resp.status_code == 200
    assert pause_resp.json()["pause"]["global_paused"] is True

    blocked = client.get("/echo-global")
    assert blocked.status_code == 503
    assert blocked.headers.get("X-Trace-Id") == blocked.json().get("trace_id")
    status_resp = client.get("/server/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["pause"]["global_paused"] is True
    server_health_resp = client.get("/server/health")
    assert server_health_resp.status_code == 200
    assert server_health_resp.json()["pause"]["global_paused"] is True
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["pause"]["global_paused"] is True

    resume_resp = client.post("/server/resume", json={})
    assert resume_resp.status_code == 200
    assert resume_resp.json()["pause"]["global_paused"] is False
    assert client.get("/echo-global").status_code == 200


@pytest.mark.xwapi_integration
def test_server_pause_is_method_specific() -> None:
    """Pausing GET must not block POST for same path."""
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="method_get_action", profile="endpoint")
    def get_action() -> dict[str, str]:
        return {"method": "get"}

    @XWAction(operationId="method_post_action", profile="endpoint")
    def post_action() -> dict[str, str]:
        return {"method": "post"}

    assert server.register_action(get_action, path="/method-specific", method="GET") is True
    assert server.register_action(post_action, path="/method-specific", method="POST") is True
    client = TestClient(server.app)

    assert client.get("/method-specific").status_code == 200
    assert client.post("/method-specific").status_code == 200

    server.pause_endpoint("/method-specific", "GET")

    assert client.get("/method-specific").status_code == 503
    assert client.post("/method-specific").status_code == 200


@pytest.mark.xwapi_integration
def test_server_pause_get_also_blocks_head() -> None:
    """Pausing GET should block HEAD for the same resource path."""
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="head_pause_target", profile="endpoint")
    def echo() -> dict[str, str]:
        return {"ok": "yes"}

    assert server.register_action(echo, path="/head-pause", method="GET") is True
    client = TestClient(server.app)
    server.pause_endpoint("/head-pause", "GET")

    response = client.head("/head-pause")
    assert response.status_code == 503


@pytest.mark.xwapi_integration
def test_server_pause_invalid_json_returns_validation_error() -> None:
    """Invalid JSON payload to pause endpoint should return validation error."""
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    response = client.post(
        "/server/pause",
        content="{invalid-json",
        headers={"content-type": "application/json"},
    )
    body = response.json()
    assert response.status_code == 400
    assert body["code"] == "ValidationError"
    assert "trace_id" in body


@pytest.mark.xwapi_integration
def test_server_resume_invalid_json_returns_validation_error() -> None:
    """Invalid JSON payload to resume endpoint should return validation error."""
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    response = client.post(
        "/server/resume",
        content="{invalid-json",
        headers={"content-type": "application/json"},
    )
    body = response.json()
    assert response.status_code == 400
    assert body["code"] == "ValidationError"
    assert "trace_id" in body


@pytest.mark.xwapi_integration
def test_server_pause_rejects_non_object_json_payload() -> None:
    """Pause endpoint should reject JSON payloads that are not objects."""
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    response = client.post("/server/pause", json=["not", "an", "object"])
    body = response.json()
    assert response.status_code == 400
    assert body["code"] == "ValidationError"


@pytest.mark.xwapi_integration
def test_pause_response_keeps_incoming_trace_id() -> None:
    """Paused response should preserve incoming trace ID header."""
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="trace_pause_test", profile="endpoint")
    def trace_endpoint() -> dict[str, str]:
        return {"ok": "yes"}

    assert server.register_action(trace_endpoint, path="/trace-check", method="GET") is True
    server.pause_endpoint("/trace-check", "GET")
    client = TestClient(server.app)

    trace_id = "trace-pause-123"
    response = client.get("/trace-check", headers={"X-Trace-Id": trace_id})
    body = response.json()
    assert response.status_code == 503
    assert response.headers.get("X-Trace-Id") == trace_id
    assert body["trace_id"] == trace_id


@pytest.mark.xwapi_integration
def test_server_health_and_status_surfaces_are_consistent() -> None:
    """Management health/status endpoints should expose production status fields."""
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    status_response = client.get("/server/status")
    health_response = client.get("/server/health")
    root_health_response = client.get("/health")

    assert status_response.status_code == 200
    assert health_response.status_code == 200
    assert root_health_response.status_code == 200

    status_body = status_response.json()
    health_body = health_response.json()
    root_health_body = root_health_response.json()

    assert "pause" in status_body
    assert "actions_count" in status_body
    assert health_body["pause"] == root_health_body["pause"]
    assert health_body["server_id"] == root_health_body["server_id"]
