from __future__ import annotations

import threading
import time
from unittest.mock import patch

import pytest

from exonware.xwapi import XWAPI, ServerLifecycleError


class _FakeUvicornServer:
    def __init__(self, _config: object):
        self.should_exit = False
        self.started = threading.Event()

    def run(self) -> None:
        self.started.set()
        while not self.should_exit:
            time.sleep(0.01)


@pytest.mark.xwapi_unit
def test_facade_stop_signals_background_server() -> None:
    """XWAPI.stop should stop a non-blocking uvicorn server."""
    api = XWAPI(title="Lifecycle API", version="1.0.0")
    api.create_app(engine="fastapi")

    with patch("uvicorn.Config"), patch("uvicorn.Server", side_effect=lambda config: _FakeUvicornServer(config)):
        api.start(blocking=False)
        server = api._uvicorn_server
        assert server is not None
        assert server.started.wait(timeout=1.0)

        api.stop()
        assert server.should_exit is True


@pytest.mark.xwapi_unit
def test_facade_restart_requires_prior_start() -> None:
    """Restart should fail before an initial start call."""
    api = XWAPI(title="Lifecycle API", version="1.0.0")
    with pytest.raises(ServerLifecycleError):
        api.restart()


@pytest.mark.xwapi_unit
def test_facade_start_while_running_raises() -> None:
    """Starting twice without stop should raise lifecycle error."""
    api = XWAPI(title="Lifecycle API", version="1.0.0")
    api.create_app(engine="fastapi")

    with patch("uvicorn.Config"), patch("uvicorn.Server", side_effect=lambda config: _FakeUvicornServer(config)):
        api.start(blocking=False)
        with pytest.raises(ServerLifecycleError):
            api.start(blocking=False)
        api.stop()
