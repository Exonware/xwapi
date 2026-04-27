# exonware/xwapi/src/exonware/xwapi/server/control_plane.py
"""
In-process control-plane listener for XWApiServer.

The listener thread is intentionally resilient: command failures are isolated to each
request so the control loop stays alive until an explicit kill/shutdown command.
"""

from __future__ import annotations

from dataclasses import dataclass
from queue import Empty, Queue
from threading import Event, Thread, current_thread
from typing import Any

from exonware.xwsystem import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class ControlPlaneResult:
    ok: bool
    command: str
    payload: dict[str, Any]
    error: str | None = None


@dataclass(slots=True)
class _ControlPlaneEnvelope:
    command: str
    payload: dict[str, Any]
    response_queue: Queue[ControlPlaneResult] | None = None


class XWApiControlPlane:
    """Single-threaded command listener for lifecycle and ops commands."""

    def __init__(self, server: Any) -> None:
        self._server = server
        self._queue: Queue[_ControlPlaneEnvelope] = Queue()
        self._stop_event = Event()
        self._thread: Thread | None = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.is_running:
            return
        self._stop_event.clear()
        self._thread = Thread(target=self._run_loop, name=f"xwapi-control-{id(self._server)}", daemon=True)
        self._thread.start()

    def stop(self, *, timeout_seconds: float = 2.0) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive() and self._thread is not current_thread():
            self._thread.join(timeout=max(0.1, timeout_seconds))

    def submit(
        self,
        command: str,
        payload: dict[str, Any] | None = None,
        *,
        wait: bool = True,
        timeout_seconds: float = 10.0,
    ) -> ControlPlaneResult:
        if not self.is_running:
            self.start()
        response_queue: Queue[ControlPlaneResult] | None = Queue(maxsize=1) if wait else None
        env = _ControlPlaneEnvelope(command=str(command).strip().lower(), payload=payload or {}, response_queue=response_queue)
        self._queue.put(env)
        if not wait or response_queue is None:
            return ControlPlaneResult(ok=True, command=env.command, payload={"queued": True})
        try:
            return response_queue.get(timeout=max(0.1, timeout_seconds))
        except Exception:
            return ControlPlaneResult(
                ok=False,
                command=env.command,
                payload={},
                error=f"control-plane timeout while waiting for '{env.command}'",
            )

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                env = self._queue.get(timeout=0.2)
            except Empty:
                continue
            result = self._dispatch(env.command, env.payload)
            if env.response_queue is not None:
                try:
                    env.response_queue.put_nowait(result)
                except Exception:
                    pass

    def _dispatch(self, command: str, payload: dict[str, Any]) -> ControlPlaneResult:
        try:
            action = self._server.resolve_control_action(command)
            if action is None:
                return ControlPlaneResult(ok=False, command=command, payload={}, error=f"unknown command: {command}")
            raw = action(**payload)
            if isinstance(raw, dict):
                return ControlPlaneResult(ok=True, command=command, payload=raw)
            return ControlPlaneResult(ok=True, command=command, payload={"result": raw})
        except Exception as exc:
            logger.exception("control-plane command failed", extra={"command": command, "error": str(exc)})
            return ControlPlaneResult(ok=False, command=command, payload={}, error=str(exc))
