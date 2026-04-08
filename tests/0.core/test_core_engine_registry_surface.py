# exonware/xwapi/tests/0.core/test_core_engine_registry_surface.py
"""Core smoke: global server engine registry lists expected built-in engines."""

from __future__ import annotations

import pytest

from exonware.xwapi.server.engines import ApiServerEngineRegistry, api_server_engine_registry


@pytest.mark.xwapi_core
def test_global_registry_includes_fastapi() -> None:
    names = set(api_server_engine_registry.list_engines())
    assert "fastapi" in names


@pytest.mark.xwapi_core
def test_fresh_registry_includes_flask_when_installed() -> None:
    """Isolated registry so ordering vs other tests (and lazy xwlazy installs) does not matter."""
    try:
        import flask  # noqa: F401
    except ImportError:
        return
    reg = ApiServerEngineRegistry()
    assert "flask" in set(reg.list_engines())


@pytest.mark.xwapi_core
def test_global_registry_lists_email_engines() -> None:
    names = set(api_server_engine_registry.list_engines())
    assert {"smtp", "pop3", "imap"}.issubset(names)


@pytest.mark.xwapi_core
def test_get_engine_unknown_returns_none() -> None:
    assert api_server_engine_registry.get_engine("definitely_not_a_registered_engine_xyz") is None
