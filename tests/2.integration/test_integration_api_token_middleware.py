from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from exonware.xwaction import ActionProfile, XWAction
from exonware.xwapi.server import XWApiServer


@pytest.mark.xwapi_integration
def test_api_token_middleware_enforces_and_meters_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_API_TOKEN_MIDDLEWARE", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_REQUIRE_BEARER", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_USAGE_AMOUNT", "1")

    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="token_protected_ping", profile=ActionProfile.ENDPOINT)
    def protected_ping() -> dict[str, str]:
        return {"status": "ok"}

    assert server.register_action(protected_ping, path="/protected/ping", method="GET")
    client = TestClient(server.app)

    unauthorized = client.get("/protected/ping")
    assert unauthorized.status_code == 401
    assert unauthorized.json()["code"] == "AuthenticationError"

    create_resp = client.post(
        "/server/tokens/create",
        json={"subject_id": "acct-mw", "name": "middleware token", "scopes": ["invoke"]},
    )
    assert create_resp.status_code == 200
    token = create_resp.json()["token"]

    recharge_resp = client.post(
        "/server/tokens/recharge",
        json={"subject_id": "acct-mw", "amount": 5.0, "currency": "USD"},
    )
    assert recharge_resp.status_code == 200

    authorized = client.get("/protected/ping", headers={"Authorization": f"Bearer {token}"})
    assert authorized.status_code == 200
    assert authorized.json()["status"] == "ok"

    balance_resp = client.get("/server/tokens/balance", params={"subject_id": "acct-mw"})
    assert balance_resp.status_code == 200
    assert balance_resp.json()["balance"] == pytest.approx(4.0)


@pytest.mark.xwapi_integration
def test_api_token_middleware_invalid_bearer_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_API_TOKEN_MIDDLEWARE", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_REQUIRE_BEARER", "true")
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="token_protected_echo", profile=ActionProfile.ENDPOINT)
    def protected_echo() -> dict[str, str]:
        return {"status": "ok"}

    assert server.register_action(protected_echo, path="/protected/echo", method="GET")
    client = TestClient(server.app)

    invalid = client.get("/protected/echo", headers={"Authorization": "Bearer not-a-real-token"})
    assert invalid.status_code == 401
    assert invalid.json()["code"] == "AuthenticationError"


@pytest.mark.xwapi_integration
def test_api_token_middleware_does_not_break_admin_bearer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_ADMIN_TOKEN", "admin-secret")
    monkeypatch.setenv("XWAPI_API_TOKEN_MIDDLEWARE", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_REQUIRE_BEARER", "true")
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    response = client.post("/server/pause", json={}, headers={"Authorization": "Bearer admin-secret"})
    assert response.status_code == 200
    assert response.json()["status"] == "paused"


@pytest.mark.xwapi_integration
def test_api_token_scope_enforcement_blocks_insufficient_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_API_TOKEN_MIDDLEWARE", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_REQUIRE_BEARER", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_ENFORCE_SCOPES", "true")
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="token_scope_read", profile=ActionProfile.ENDPOINT)
    def read_endpoint() -> dict[str, str]:
        return {"status": "read-ok"}

    @XWAction(operationId="token_scope_write", profile=ActionProfile.ENDPOINT)
    def write_endpoint() -> dict[str, str]:
        return {"status": "write-ok"}

    assert server.register_action(read_endpoint, path="/protected/read", method="GET", required_scopes=["read:data"])
    assert server.register_action(write_endpoint, path="/protected/write", method="GET", required_scopes=["write:data"])
    client = TestClient(server.app)

    create_resp = client.post(
        "/server/tokens/create",
        json={"subject_id": "acct-scope", "name": "scope token", "scopes": ["read:data"]},
    )
    assert create_resp.status_code == 200
    token = create_resp.json()["token"]

    allowed = client.get("/protected/read", headers={"Authorization": f"Bearer {token}"})
    assert allowed.status_code == 200
    denied = client.get("/protected/write", headers={"Authorization": f"Bearer {token}"})
    assert denied.status_code == 403
    assert denied.json()["code"] == "AuthorizationError"


@pytest.mark.xwapi_integration
def test_api_token_metering_honors_idempotency_header(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_API_TOKEN_MIDDLEWARE", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_REQUIRE_BEARER", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_USAGE_AMOUNT", "1")
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="token_idempotent_ping", profile=ActionProfile.ENDPOINT)
    def ping() -> dict[str, str]:
        return {"status": "ok"}

    assert server.register_action(ping, path="/protected/idempotent", method="GET")
    client = TestClient(server.app)

    create_resp = client.post(
        "/server/tokens/create",
        json={"subject_id": "acct-idem", "name": "idem token", "scopes": ["invoke"]},
    )
    assert create_resp.status_code == 200
    token = create_resp.json()["token"]
    client.post("/server/tokens/recharge", json={"subject_id": "acct-idem", "amount": 5.0, "currency": "USD"})

    headers = {"Authorization": f"Bearer {token}", "Idempotency-Key": "request-123"}
    first = client.get("/protected/idempotent", headers=headers)
    second = client.get("/protected/idempotent", headers=headers)
    assert first.status_code == 200
    assert second.status_code == 200

    balance = client.get("/server/tokens/balance", params={"subject_id": "acct-idem"})
    assert balance.status_code == 200
    assert balance.json()["balance"] == pytest.approx(4.0)


@pytest.mark.xwapi_integration
def test_api_token_scope_deny_unmapped_returns_403(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_API_TOKEN_MIDDLEWARE", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_REQUIRE_BEARER", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_ENFORCE_SCOPES", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_SCOPE_DENY_UNMAPPED", "true")
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    create_resp = client.post(
        "/server/tokens/create",
        json={"subject_id": "acct-unmapped", "name": "scope token", "scopes": ["invoke"]},
    )
    assert create_resp.status_code == 200
    token = create_resp.json()["token"]

    denied = client.get("/protected/unmapped-path", headers={"Authorization": f"Bearer {token}"})
    assert denied.status_code == 403
    assert denied.json()["code"] == "AuthorizationError"


@pytest.mark.xwapi_integration
def test_api_token_scope_unmapped_allowed_when_deny_flag_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_API_TOKEN_MIDDLEWARE", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_REQUIRE_BEARER", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_ENFORCE_SCOPES", "true")
    monkeypatch.delenv("XWAPI_API_TOKEN_SCOPE_DENY_UNMAPPED", raising=False)
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    create_resp = client.post(
        "/server/tokens/create",
        json={"subject_id": "acct-unmapped-allow", "name": "scope token", "scopes": ["invoke"]},
    )
    assert create_resp.status_code == 200
    token = create_resp.json()["token"]

    unmapped = client.get("/protected/unmapped-allow", headers={"Authorization": f"Bearer {token}"})
    assert unmapped.status_code == 404


@pytest.mark.xwapi_integration
def test_api_token_scope_template_specificity_prefers_literal_route(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_API_TOKEN_MIDDLEWARE", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_REQUIRE_BEARER", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_ENFORCE_SCOPES", "true")
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="scope_generic_route", profile=ActionProfile.ENDPOINT)
    def generic_route() -> dict[str, str]:
        return {"status": "generic"}

    @XWAction(operationId="scope_literal_route", profile=ActionProfile.ENDPOINT)
    def literal_route() -> dict[str, str]:
        return {"status": "literal"}

    assert server.register_action(generic_route, path="/resources/{rid}", method="GET", required_scopes=["scope:generic"])
    assert server.register_action(literal_route, path="/resources/special", method="GET", required_scopes=["scope:special"])
    client = TestClient(server.app)

    generic_token = client.post(
        "/server/tokens/create",
        json={"subject_id": "acct-generic", "name": "generic token", "scopes": ["scope:generic"]},
    ).json()["token"]
    special_token = client.post(
        "/server/tokens/create",
        json={"subject_id": "acct-special", "name": "special token", "scopes": ["scope:special"]},
    ).json()["token"]

    denied = client.get("/resources/special", headers={"Authorization": f"Bearer {generic_token}"})
    assert denied.status_code == 403
    allowed = client.get("/resources/special", headers={"Authorization": f"Bearer {special_token}"})
    assert allowed.status_code == 200


@pytest.mark.xwapi_integration
def test_api_token_metering_skips_debit_on_4xx_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_API_TOKEN_MIDDLEWARE", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_REQUIRE_BEARER", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_USAGE_AMOUNT", "1")
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    created = client.post(
        "/server/tokens/create",
        json={"subject_id": "acct-4xx", "name": "4xx token", "scopes": ["invoke"]},
    )
    token = created.json()["token"]
    client.post("/server/tokens/recharge", json={"subject_id": "acct-4xx", "amount": 5.0, "currency": "USD"})

    missing = client.get("/route/that/does/not/exist", headers={"Authorization": f"Bearer {token}"})
    assert missing.status_code == 404
    balance = client.get("/server/tokens/balance", params={"subject_id": "acct-4xx"})
    assert balance.status_code == 200
    assert balance.json()["balance"] == pytest.approx(5.0)


@pytest.mark.xwapi_integration
def test_api_token_metering_insufficient_balance_returns_403(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_API_TOKEN_MIDDLEWARE", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_REQUIRE_BEARER", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_USAGE_AMOUNT", "10")
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="meter_balance_guard", profile=ActionProfile.ENDPOINT)
    def endpoint_ok() -> dict[str, str]:
        return {"status": "ok"}

    assert server.register_action(endpoint_ok, path="/meter/insufficient", method="GET")
    client = TestClient(server.app)
    token = client.post(
        "/server/tokens/create",
        json={"subject_id": "acct-low", "name": "low token", "scopes": ["invoke"]},
    ).json()["token"]
    client.post("/server/tokens/recharge", json={"subject_id": "acct-low", "amount": 1.0, "currency": "USD"})

    blocked = client.get("/meter/insufficient", headers={"Authorization": f"Bearer {token}"})
    assert blocked.status_code == 403
    assert blocked.json()["code"] == "AuthorizationError"
    balance = client.get("/server/tokens/balance", params={"subject_id": "acct-low"})
    assert balance.json()["balance"] == pytest.approx(1.0)


@pytest.mark.xwapi_integration
def test_api_token_verify_provider_exception_returns_500(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_API_TOKEN_MIDDLEWARE", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_REQUIRE_BEARER", "true")
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="verify_exception_route", profile=ActionProfile.ENDPOINT)
    def verify_exception_route() -> dict[str, str]:
        return {"status": "ok"}

    assert server.register_action(verify_exception_route, path="/protected/verify-exception", method="GET")

    async def broken_verify(_: str):
        raise RuntimeError("verify backend unavailable")

    server._token_manager.verify_token = broken_verify  # type: ignore[method-assign]
    client = TestClient(server.app, raise_server_exceptions=False)
    response = client.get("/protected/verify-exception", headers={"Authorization": "Bearer xw_fake_token"})
    assert response.status_code == 500


@pytest.mark.xwapi_integration
def test_api_token_metering_unexpected_error_returns_403(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_API_TOKEN_MIDDLEWARE", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_REQUIRE_BEARER", "true")
    monkeypatch.setenv("XWAPI_API_TOKEN_USAGE_AMOUNT", "1")
    server = XWApiServer(engine="fastapi")

    @XWAction(operationId="meter_failure_route", profile=ActionProfile.ENDPOINT)
    def meter_failure_route() -> dict[str, str]:
        return {"status": "ok"}

    assert server.register_action(meter_failure_route, path="/meter/unexpected", method="GET")
    client = TestClient(server.app)
    token = client.post(
        "/server/tokens/create",
        json={"subject_id": "acct-meter-fail", "name": "meter fail token", "scopes": ["invoke"]},
    ).json()["token"]
    client.post("/server/tokens/recharge", json={"subject_id": "acct-meter-fail", "amount": 5.0, "currency": "USD"})

    async def broken_meter(*_, **__):
        raise RuntimeError("metering backend failed")

    server.record_api_token_usage = broken_meter  # type: ignore[method-assign]
    response = client.get("/meter/unexpected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json()["code"] == "AuthorizationError"
