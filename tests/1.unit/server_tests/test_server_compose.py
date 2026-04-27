# exonware/xwapi/tests/1.unit/server_tests/test_server_compose.py
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from exonware.xwapi.server.compose import (
    XWApiComposeOptions,
    XWApiComposeSpec,
    compose_xwapi_servers,
)


class _ServerWrapper:
    def __init__(self, app: FastAPI) -> None:
        self.app = app


def _new_app(name: str) -> FastAPI:
    app = FastAPI(title=name)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"service": name, "status": "ok"}

    @app.get("/")
    def root() -> dict[str, str]:
        return {"service": name}

    return app


@pytest.mark.xwapi_unit
def test_compose_merges_routes_with_optional_prefixes() -> None:
    host = _new_app("host")
    chat = _new_app("chat")
    bots = _new_app("bots")

    compose_xwapi_servers(
        host,
        [
            XWApiComposeSpec(server_or_app=_ServerWrapper(chat), prefix="/xwchat"),
            XWApiComposeSpec(server_or_app=bots, prefix="/xwbots"),
        ],
        options=XWApiComposeOptions(global_prefix="/power"),
    )

    client = TestClient(host)
    chat_health = client.get("/power/xwchat/health")
    assert chat_health.status_code == 200
    assert chat_health.json().get("service") == "chat"

    bots_health = client.get("/power/xwbots/health")
    assert bots_health.status_code == 200
    assert bots_health.json().get("service") == "bots"


@pytest.mark.xwapi_unit
def test_compose_does_not_include_child_root_by_default() -> None:
    host = _new_app("host")
    child = _new_app("child")

    compose_xwapi_servers(
        host,
        [XWApiComposeSpec(server_or_app=child, prefix="/child")],
    )

    client = TestClient(host)
    assert client.get("/child").status_code == 404
    assert client.get("/child/health").status_code == 200


@pytest.mark.xwapi_unit
def test_compose_conflict_policy_error_raises() -> None:
    host = _new_app("host")
    child = _new_app("child")

    with pytest.raises(ValueError, match="route conflict"):
        compose_xwapi_servers(
            host,
            [XWApiComposeSpec(server_or_app=child, prefix="/x")],
            options=XWApiComposeOptions(global_prefix="/x"),
        )


@pytest.mark.xwapi_unit
def test_compose_conflict_policy_skip_keeps_host_routes() -> None:
    host = _new_app("host")
    child = _new_app("child")

    compose_xwapi_servers(
        host,
        [XWApiComposeSpec(server_or_app=child, prefix="/x")],
        options=XWApiComposeOptions(global_prefix="/x", conflict_policy="skip"),
    )

    client = TestClient(host)
    # Host route remains in place and no duplicate child route is added.
    health = client.get("/x/health")
    assert health.status_code == 200
    assert health.json().get("service") == "host"
