from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from exonware.xwapi.common.app import create_app
from exonware.xwapi.facade import XWAPI
from exonware.xwapi.server.engines import ApiServerEngineRegistry
from exonware.xwapi.server.engines.contracts import ProtocolType


@pytest.mark.xwapi_unit
def test_registry_auto_registers_email_protocol_engines() -> None:
    """Engine registry should expose non-HTTP email engines."""
    registry = ApiServerEngineRegistry()
    names = set(registry.list_engines())
    assert {"smtp", "imap", "pop3"}.issubset(names)


@pytest.mark.xwapi_unit
def test_create_app_dispatches_to_smtp_engine() -> None:
    """Common app factory should resolve SMTP engine via registry."""
    app = create_app(engine="smtp")
    assert app is not None
    assert hasattr(app, "protocol_type")
    assert app.protocol_type == ProtocolType.SMTP


@pytest.mark.xwapi_unit
def test_create_app_dispatches_to_imap_engine() -> None:
    """Common app factory should resolve IMAP engine via registry."""
    app = create_app(engine="imap")
    assert app is not None
    assert hasattr(app, "protocol_type")
    assert app.protocol_type == ProtocolType.IMAP


@pytest.mark.xwapi_unit
def test_create_app_dispatches_to_pop3_engine() -> None:
    """Common app factory should resolve POP3 engine via registry."""
    app = create_app(engine="pop3")
    assert app is not None
    assert hasattr(app, "protocol_type")
    assert app.protocol_type == ProtocolType.POP3


@pytest.mark.xwapi_unit
def test_facade_create_app_prefers_requested_engine_for_action_registration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Facade should use caller-selected engine for action engine lookup."""
    from exonware.xwaction.engines import action_engine_registry

    class _CustomApp:
        pass

    captured: dict[str, str] = {}
    mock_action_engine = MagicMock()
    mock_action_engine.setup.return_value = True
    mock_action_engine.register_action.return_value = True

    def _fake_get_engine(name: str):
        captured["engine_name"] = name
        if name == "flask":
            return mock_action_engine
        return None

    monkeypatch.setattr("exonware.xwapi.facade.create_app", lambda **_: _CustomApp())
    monkeypatch.setattr(action_engine_registry, "get_engine", _fake_get_engine)

    fake_profile = SimpleNamespace(value="query")
    fake_xwaction = SimpleNamespace(
        operationId="engine_probe",
        profile=fake_profile,
        to_openapi=lambda: {"paths": {}, "components": {"schemas": {}}},
    )
    fake_action = SimpleNamespace(__name__="engine_probe", xwaction=fake_xwaction)

    api = XWAPI(actions=[fake_action], title="Engine Probe", version="1.0.0")
    app = api.create_app(engine="flask")

    assert isinstance(app, _CustomApp)
    assert captured["engine_name"] == "flask"
    assert mock_action_engine.register_action.called
