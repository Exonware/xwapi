from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from exonware.xwapi.server import XWApiServer


@pytest.mark.xwapi_integration
def test_token_generation_monitoring_and_recharge_endpoints() -> None:
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    create_resp = client.post(
        "/server/tokens/create",
        json={
            "subject_id": "acct-123",
            "name": "sdk token",
            "scopes": ["chat", "embeddings"],
            "expires_in_seconds": 3600,
        },
    )
    assert create_resp.status_code == 200
    create_body = create_resp.json()
    assert create_body["status"] == "created"
    token_id = create_body["token_id"]

    list_resp = client.get("/server/tokens/list", params={"subject_id": "acct-123"})
    assert list_resp.status_code == 200
    tokens = list_resp.json()["tokens"]
    assert any(token["token_id"] == token_id for token in tokens)

    recharge_resp = client.post(
        "/server/tokens/recharge",
        json={"subject_id": "acct-123", "amount": 25.0, "currency": "USD"},
    )
    assert recharge_resp.status_code == 200
    assert recharge_resp.json()["status"] == "recharged"

    usage_resp = client.post(
        "/server/tokens/usage",
        json={"token_id": token_id, "amount": 7.5, "operation": "completion"},
    )
    assert usage_resp.status_code == 200
    assert usage_resp.json()["status"] == "recorded"

    usage_list = client.get("/server/tokens/usage", params={"token_id": token_id})
    assert usage_list.status_code == 200
    assert len(usage_list.json()["usage"]) == 1

    balance_resp = client.get("/server/tokens/balance", params={"subject_id": "acct-123"})
    assert balance_resp.status_code == 200
    assert balance_resp.json()["balance"] == pytest.approx(17.5)

    revoke_resp = client.post("/server/tokens/revoke", json={"token_id": token_id})
    assert revoke_resp.status_code == 200
    assert revoke_resp.json()["status"] == "revoked"


@pytest.mark.xwapi_integration
def test_token_usage_insufficient_balance_returns_validation_error() -> None:
    server = XWApiServer(engine="fastapi")
    client = TestClient(server.app)

    create_resp = client.post(
        "/server/tokens/create",
        json={"subject_id": "acct-empty", "name": "no-balance", "scopes": ["chat"]},
    )
    assert create_resp.status_code == 200
    token_id = create_resp.json()["token_id"]

    usage_resp = client.post(
        "/server/tokens/usage",
        json={"token_id": token_id, "amount": 10.0, "operation": "completion"},
    )
    assert usage_resp.status_code == 400
    body = usage_resp.json()
    assert body["code"] == "ValidationError"
