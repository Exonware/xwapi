from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from exonware.xwapi.server import XWApiServer


@pytest.mark.xwapi_unit
def test_stop_flushes_handlers_when_server_not_running() -> None:
    """stop() should flush registered handlers even when server is not running."""
    server = XWApiServer(engine="fastapi")
    handler = MagicMock()
    server.register_flushable(handler)

    server.stop()

    handler.flush.assert_called_once()
    handler.close.assert_called_once()


@pytest.mark.xwapi_unit
def test_stop_flush_continues_after_handler_error() -> None:
    """A broken handler must not prevent remaining handlers from flushing."""
    server = XWApiServer(engine="fastapi")
    failing = MagicMock()
    failing.flush.side_effect = RuntimeError("flush failed")
    healthy = MagicMock()
    server.register_flushable(failing)
    server.register_flushable(healthy)

    server.stop()

    failing.flush.assert_called_once()
    healthy.flush.assert_called_once()
    healthy.close.assert_called_once()


@pytest.mark.xwapi_unit
def test_register_flushable_deduplicates_same_handler() -> None:
    """register_flushable should not register the same object twice."""
    server = XWApiServer(engine="fastapi")
    handler = MagicMock()
    server.register_flushable(handler)
    server.register_flushable(handler)

    server.stop()

    handler.flush.assert_called_once()
