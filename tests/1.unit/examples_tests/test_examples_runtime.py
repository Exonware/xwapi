from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from exonware.xwapi.server.engines.contracts import ProtocolType
from exonware.xwapi.server.engines import api_server_engine_registry

_EXAMPLES_DIR = Path(__file__).resolve().parents[3] / ".examples"


def _load_example_module(filename: str):
    path = _EXAMPLES_DIR / filename
    spec = importlib.util.spec_from_file_location(f"xwapi_example_{path.stem}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.xwapi_unit
def test_fastapi_example_builds_app() -> None:
    module = _load_example_module("fastapi_rest_server.py")

    app = module.build_app()
    assert app is not None
    assert hasattr(app, "routes")


@pytest.mark.xwapi_unit
def test_flask_example_builds_app() -> None:
    if api_server_engine_registry.get_engine("flask") is None:
        pytest.skip("flask engine not available in this environment")
    module = _load_example_module("flask_action_server.py")

    app = module.build_app()
    assert app is not None
    assert hasattr(app, "url_map")


@pytest.mark.xwapi_unit
def test_email_backend_example_builds_protocol_engines() -> None:
    module = _load_example_module("email_backend_server.py")

    smtp, smtp_app, imap, imap_app, pop3, pop3_app = module.build_email_backends()
    assert smtp_app is smtp
    assert imap_app is imap
    assert pop3_app is pop3
    assert smtp.protocol_type == ProtocolType.SMTP
    assert imap.protocol_type == ProtocolType.IMAP
    assert pop3.protocol_type == ProtocolType.POP3
