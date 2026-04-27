from __future__ import annotations

import pytest

from exonware.xwapi.server import XWApiServer


@pytest.mark.xwapi_unit
def test_pause_policy_blocks_specific_route_only() -> None:
    """Pause policy should block only configured endpoint/method."""
    server = XWApiServer(engine="fastapi")
    server.pause_endpoint("/echo", "GET")

    assert server.should_block_request("GET", "/echo") is True
    assert server.should_block_request("POST", "/echo") is False
    assert server.should_block_request("GET", "/other") is False


@pytest.mark.xwapi_unit
def test_pause_policy_global_pause_and_allowlist() -> None:
    """Global pause should block routes but still allow admin status."""
    server = XWApiServer(engine="fastapi")
    server.set_global_pause(True)

    assert server.should_block_request("GET", "/anything") is True
    assert server.should_block_request("GET", "/server/status") is False
    assert server.should_block_request("GET", "/health") is False
    assert server.should_block_request("GET", "/server/health") is False
    assert server.should_block_request("POST", "/server/log") is False


@pytest.mark.xwapi_unit
def test_pause_policy_normalizes_paths() -> None:
    """Pause policy should normalize equivalent paths consistently."""
    server = XWApiServer(engine="fastapi")
    server.pause_endpoint("/echo", "GET")

    assert server.should_block_request("GET", "/echo/") is True
    assert server.should_block_request("GET", "echo") is True
