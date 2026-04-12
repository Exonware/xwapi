#exonware/xwapi/src/exonware/xwapi/governance/lockfile.py
"""
Lockfile management for process-level singleton enforcement.
Manages PID files and lockfiles to prevent concurrent server instances
across processes.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.7
"""

import os
import sys
import time
import atexit
from pathlib import Path
import platform
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


class LockfileManager:
    """
    Manages PID lockfiles for process-level singleton enforcement.
    Creates PID files to track running server instances and prevents
    concurrent instances from starting.
    """

    def __init__(self, server_id: str, runtime_dir: str | None = None):
        """
        Initialize lockfile manager.
        Args:
            server_id: Unique identifier for the server (name/role)
            runtime_dir: Directory for lockfiles (default: system temp directory)
        """
        self.server_id = server_id
        self.runtime_dir = Path(runtime_dir) if runtime_dir else Path.cwd() / ".xwapi_runtime"
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        # Lockfile path: {runtime_dir}/{server_id}.pid
        self.lockfile_path = self.runtime_dir / f"{server_id}.pid"
        self._pid: int | None = None
        # Register cleanup on exit
        atexit.register(self.cleanup)

    def acquire(self, takeover: bool = False) -> bool:
        """
        Acquire lockfile (create PID file).
        Args:
            takeover: If True, kill existing process and take over lock
        Returns:
            True if lock acquired, False if another process holds the lock
        """
        # Check if lockfile exists
        if self.lockfile_path.exists():
            # Read existing PID
            try:
                existing_pid = int(self.lockfile_path.read_text().strip())
            except (ValueError, OSError) as e:
                logger.warning(f"Invalid lockfile {self.lockfile_path}: {e}, removing")
                self.lockfile_path.unlink(missing_ok=True)
                existing_pid = None
            if existing_pid is not None:
                # Check if process is still running
                if self._is_process_running(existing_pid):
                    if takeover:
                        logger.info(f"Taking over lock from process {existing_pid}")
                        self._kill_process(existing_pid)
                        # Wait a moment for process to terminate
                        time.sleep(0.5)
                    else:
                        logger.warning(
                            f"Lockfile exists and process {existing_pid} is running. "
                            f"Use takeover=True to take over."
                        )
                        return False
                else:
                    # Stale lockfile - process is not running
                    logger.info(f"Removing stale lockfile (process {existing_pid} not running)")
                    self.lockfile_path.unlink(missing_ok=True)
        # Create lockfile with current PID
        self._pid = os.getpid()
        try:
            self.lockfile_path.write_text(str(self._pid))
            logger.debug(f"Acquired lockfile: {self.lockfile_path} (PID: {self._pid})")
            return True
        except OSError as e:
            logger.error(f"Failed to create lockfile {self.lockfile_path}: {e}")
            return False

    def release(self) -> None:
        """
        Release lockfile (remove PID file).
        """
        if self.lockfile_path.exists():
            try:
                # Verify it's our PID before removing
                existing_pid = int(self.lockfile_path.read_text().strip())
                if existing_pid == os.getpid():
                    self.lockfile_path.unlink(missing_ok=True)
                    logger.debug(f"Released lockfile: {self.lockfile_path}")
                else:
                    logger.warning(
                        f"Lockfile PID mismatch: expected {os.getpid()}, "
                        f"found {existing_pid}. Not removing."
                    )
            except (ValueError, OSError) as e:
                logger.warning(f"Error releasing lockfile {self.lockfile_path}: {e}")
                # Remove anyway if we can't read it
                self.lockfile_path.unlink(missing_ok=True)

    def cleanup(self) -> None:
        """Cleanup lockfile on exit."""
        self.release()

    def _is_process_running(self, pid: int) -> bool:
        """
        Check if a process is running.
        Args:
            pid: Process ID to check
        Returns:
            True if process is running, False otherwise
        """
        try:
            if platform.system() == "Windows":
                # Windows: use tasklist or try to signal process
                import subprocess
                result = subprocess.run(
                    ['tasklist', '/FI', f'PID eq {pid}'],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    shell=True
                )
                return str(pid) in result.stdout
            else:
                # Unix/Linux/macOS: use os.kill with signal 0
                os.kill(pid, 0)
                return True
        except (OSError, subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _kill_process(self, pid: int) -> bool:
        """
        Kill a process by PID.
        Args:
            pid: Process ID to kill
        Returns:
            True if process was killed, False otherwise
        """
        try:
            if platform.system() == "Windows":
                import subprocess
                result = subprocess.run(
                    ['taskkill', '/F', '/PID', str(pid)],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    shell=True
                )
                return result.returncode == 0
            else:
                import signal
                os.kill(pid, signal.SIGTERM)
                # Wait a moment for graceful shutdown
                time.sleep(0.5)
                # Force kill if still running
                if self._is_process_running(pid):
                    os.kill(pid, signal.SIGKILL)
                return True
        except (OSError, subprocess.TimeoutExpired, FileNotFoundError, ImportError) as e:
            logger.warning(f"Failed to kill process {pid}: {e}")
            return False
    @property

    def is_locked(self) -> bool:
        """Check if lockfile exists and is held by running process."""
        if not self.lockfile_path.exists():
            return False
        try:
            existing_pid = int(self.lockfile_path.read_text().strip())
            return self._is_process_running(existing_pid)
        except (ValueError, OSError):
            return False


def create_lockfile_manager(server_id: str, runtime_dir: str | None = None) -> LockfileManager:
    """
    Create a lockfile manager instance.
    Args:
        server_id: Unique identifier for the server
        runtime_dir: Directory for lockfiles (optional)
    Returns:
        LockfileManager instance
    """
    return LockfileManager(server_id, runtime_dir)
