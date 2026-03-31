from __future__ import annotations

import os

import pytest

from exonware.xwapi.server.governance.lockfile import LockfileManager


@pytest.mark.xwapi_unit
def test_lockfile_acquire_removes_stale_pid(tmp_path) -> None:
    """Acquire should replace stale lockfile when process is not running."""
    manager = LockfileManager("svc-stale", runtime_dir=str(tmp_path))
    manager.lockfile_path.write_text("12345")

    manager._is_process_running = lambda pid: False  # type: ignore[method-assign]
    assert manager.acquire() is True
    assert manager.lockfile_path.exists()
    assert manager.lockfile_path.read_text().strip() == str(os.getpid())


@pytest.mark.xwapi_unit
def test_lockfile_acquire_rejects_live_process_without_takeover(tmp_path) -> None:
    """Acquire should fail when another process is considered alive."""
    manager = LockfileManager("svc-live", runtime_dir=str(tmp_path))
    manager.lockfile_path.write_text("98765")

    manager._is_process_running = lambda pid: True  # type: ignore[method-assign]
    assert manager.acquire(takeover=False) is False


@pytest.mark.xwapi_unit
def test_lockfile_release_removes_owned_lockfile(tmp_path) -> None:
    """Release should remove lockfile when current process owns it."""
    manager = LockfileManager("svc-release", runtime_dir=str(tmp_path))
    assert manager.acquire() is True
    assert manager.lockfile_path.exists()

    manager.release()
    assert not manager.lockfile_path.exists()
