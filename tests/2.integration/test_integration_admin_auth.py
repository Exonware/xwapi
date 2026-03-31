from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from exonware.xwaction import XWAction
from exonware.xwapi.server import XWApiServer
from exonware.xwapi.server.admin.router import register_admin_endpoints


@pytest.mark.xwapi_integration
def test_admin_mutations_open_when_no_token_configured() -> None:
    """Default behavior should remain open without configured admin token."""
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    response = client.post("/server/pause", json={})
    assert response.status_code == 200
    assert response.json()["status"] == "paused"


@pytest.mark.xwapi_integration
def test_admin_mutations_require_token_when_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutating admin endpoints should require token once configured."""
    monkeypatch.setenv("XWAPI_ADMIN_TOKEN", "secret-token")
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    response = client.post("/server/pause", json={})
    body = response.json()
    assert response.status_code == 401
    assert body["code"] == "AuthenticationError"
    assert response.headers.get("X-Trace-Id") == body["trace_id"]


@pytest.mark.xwapi_integration
def test_admin_mutations_accept_bearer_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bearer admin token should authorize mutating admin endpoints."""
    monkeypatch.setenv("XWAPI_ADMIN_TOKEN", "secret-token")
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    response = client.post("/server/pause", json={}, headers={"Authorization": "Bearer secret-token"})
    assert response.status_code == 200
    assert response.json()["status"] == "paused"


@pytest.mark.xwapi_integration
def test_admin_mutations_accept_x_admin_token_header(monkeypatch: pytest.MonkeyPatch) -> None:
    """X-Admin-Token header should authorize mutating admin endpoints."""
    monkeypatch.setenv("XWAPI_ADMIN_TOKEN", "secret-token")
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    response = client.post("/server/pause", json={}, headers={"X-Admin-Token": "secret-token"})
    assert response.status_code == 200
    assert response.json()["status"] == "paused"


@pytest.mark.xwapi_integration
def test_admin_read_endpoints_stay_public_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Read-only admin endpoints remain public unless read protection is enabled."""
    monkeypatch.setenv("XWAPI_ADMIN_TOKEN", "secret-token")
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    status_response = client.get("/server/status")
    health_response = client.get("/health")
    assert status_response.status_code == 200
    assert health_response.status_code == 200


@pytest.mark.xwapi_integration
def test_admin_reads_require_token_when_protect_read_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_ADMIN_TOKEN", "secret-token")
    monkeypatch.setenv("XWAPI_ADMIN_PROTECT_READ", "true")
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    unauthorized = client.get("/server/status")
    assert unauthorized.status_code == 401

    authorized = client.get("/server/status", headers={"Authorization": "Bearer secret-token"})
    assert authorized.status_code == 200


@pytest.mark.xwapi_integration
def test_admin_reads_accept_x_admin_token_when_protect_read_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_ADMIN_TOKEN", "secret-token")
    monkeypatch.setenv("XWAPI_ADMIN_PROTECT_READ", "true")
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    unauthorized = client.get("/server/pipeline")
    assert unauthorized.status_code == 401

    authorized = client.get("/server/pipeline", headers={"X-Admin-Token": "secret-token"})
    assert authorized.status_code == 200


@pytest.mark.xwapi_integration
def test_custom_admin_prefix_also_protected(monkeypatch: pytest.MonkeyPatch) -> None:
    """Token protection should apply to custom admin prefixes as well."""
    monkeypatch.setenv("XWAPI_ADMIN_TOKEN", "secret-token")
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="auth_ops_echo", profile="endpoint")
    def echo() -> dict[str, str]:
        return {"ok": "yes"}

    assert server.register_action(echo, path="/echo-auth-ops", method="GET") is True
    register_admin_endpoints(server.app, server, prefix="/ops", tag="Operations")
    client = TestClient(server.app)

    unauthorized = client.post("/ops/pause", json={"endpoint": "/echo-auth-ops", "method": "GET"})
    assert unauthorized.status_code == 401

    authorized = client.post(
        "/ops/pause",
        json={"endpoint": "/echo-auth-ops", "method": "GET"},
        headers={"Authorization": "Bearer secret-token"},
    )
    assert authorized.status_code == 200
    assert authorized.json()["status"] == "paused"
