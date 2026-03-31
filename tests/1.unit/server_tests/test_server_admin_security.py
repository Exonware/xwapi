from __future__ import annotations

import pytest

from exonware.xwapi.errors import XWAPIError
from exonware.xwapi.server import XWApiServer


@pytest.mark.xwapi_unit
def test_production_requires_admin_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_ENV", "production")
    monkeypatch.delenv("XWAPI_ADMIN_TOKEN", raising=False)
    monkeypatch.delenv("XWAPI_ALLOW_INSECURE_ADMIN", raising=False)
    with pytest.raises(XWAPIError):
        XWApiServer(engine="fastapi")


@pytest.mark.xwapi_unit
def test_production_enables_admin_read_protection(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XWAPI_ENV", "production")
    monkeypatch.setenv("XWAPI_ADMIN_TOKEN", "secret-token")
    monkeypatch.delenv("XWAPI_ADMIN_PROTECT_READ", raising=False)
    server = XWApiServer(engine="fastapi")
    assert getattr(server, "_admin_protect_reads", False) is True
