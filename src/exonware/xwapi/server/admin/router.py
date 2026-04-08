#exonware/xwapi/src/exonware/xwapi/server/admin/router.py
"""
Admin router for FastAPI engine.
Creates FastAPI router with server management endpoints.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.4
"""

from typing import Any
from datetime import datetime
from exonware.xwapi.server.base import AApiServer
from exonware.xwapi.errors import (
    ServerLifecycleError,
    create_error_response,
    get_http_status_code,
)
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


def create_admin_router(server: AApiServer, prefix: str = "/server", tag: str = "Server") -> Any:
    """
    Create HTTP framework router with admin endpoints.
    Supports both FastAPI (APIRouter) and Flask (Blueprint).
    Args:
        server: AApiServer instance to manage
        prefix: URL prefix for admin endpoints (default: "/server")
        tag: OpenAPI tag name (default: "Server")
    Returns:
        Framework-specific router (FastAPI APIRouter or Flask Blueprint)
    Raises:
        ImportError: If neither FastAPI nor Flask is available
    """
    # Try FastAPI first
    try:
        from fastapi import APIRouter
        from pydantic import BaseModel
        return _create_fastapi_admin_router(server, prefix, tag, APIRouter, BaseModel)
    except ImportError:
        pass
    # Fallback to Flask
    try:
        from flask import Blueprint
        return _create_flask_admin_router(server, prefix, tag, Blueprint)
    except ImportError:
        raise ImportError("FastAPI or Flask is required for admin endpoints. Install with: pip install fastapi or pip install flask")


def _create_fastapi_admin_router(server: AApiServer, prefix: str, tag: str, APIRouter, BaseModel) -> Any:
    """Create FastAPI APIRouter with admin endpoints."""
    from fastapi import Request

    router = APIRouter(prefix=prefix, tags=[tag])

    def _is_running() -> bool:
        value = getattr(server, "is_running", False)
        if callable(value):
            try:
                return bool(value())
            except Exception:
                return False
        return bool(value)

    def _status_snapshot() -> dict[str, Any]:
        if hasattr(server, "_build_status_snapshot"):
            try:
                snapshot = server._build_status_snapshot()
                if isinstance(snapshot, dict):
                    return snapshot
            except Exception:
                pass
        try:
            snapshot = server.status()
            if isinstance(snapshot, dict):
                return snapshot
        except Exception:
            pass
        return {
            "status": "running" if _is_running() else "stopped",
            "is_running": _is_running(),
            "services_running": bool(getattr(server, "_services_running", False)),
        }

    def _health_snapshot() -> dict[str, Any]:
        try:
            health = server.health()
            if isinstance(health, dict):
                return health
        except Exception:
            pass
        return {
            "status": "healthy" if _is_running() else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "is_running": _is_running(),
        }

    # Response models
    class ServerStatusResponse(BaseModel, extra="allow"):
        """Server status response model."""
        status: str
        is_running: bool
        services_running: bool = False
        start_time: str | None = None
        uptime_seconds: float | None = None
        engine: str | None = None
        host: str | None = None
        port: int | None = None
        actions_count: int = 0
    class HealthResponse(BaseModel, extra="allow"):
        """Health check response model."""
        status: str
        timestamp: str
        is_running: bool = False
        services_running: bool = False
    class LogResponse(BaseModel):
        """Log response model."""
        level: str
        message: str
        timestamp: str
    @router.post("/start", response_model=ServerStatusResponse, summary="Start services")
    async def start_services():
        """Mirror XWApiServer semantics: start is process-managed externally."""
        if _is_running():
            snapshot = _status_snapshot()
            snapshot["status"] = "already_running"
            snapshot["message"] = f"Server is already running on {snapshot.get('host')}:{snapshot.get('port')}"
            return ServerStatusResponse(**snapshot)
        snapshot = _status_snapshot()
        snapshot["status"] = "info"
        snapshot["message"] = "Use server.start() or server.run() to start the server. Management endpoints provide status only."
        snapshot["note"] = "Server must be started externally via .start() or .run() method"
        return ServerStatusResponse(**snapshot)
    @router.post("/restart", response_model=ServerStatusResponse, summary="Restart server")
    async def restart_server():
        """Mirror XWApiServer semantics: return guidance for process-managed restart."""
        try:
            if _is_running():
                server.stop()
            snapshot = _status_snapshot()
            snapshot["status"] = "info"
            snapshot["message"] = "Server restart requires external process management. Stop the server process and start it again."
            snapshot["note"] = "For programmatic restart, use server.stop() then server.start() in a separate thread/process"
            return ServerStatusResponse(**snapshot)
        except Exception as e:
            raise ServerLifecycleError(
                message="Failed to process restart request",
                details={"error": str(e)},
            ) from e
    @router.post("/stop", response_model=ServerStatusResponse, summary="Stop server")
    async def stop_server():
        """Stop the server (HTTP and services)."""
        if not _is_running():
            snapshot = _status_snapshot()
            snapshot["status"] = "already_stopped"
            snapshot["message"] = "Server is already stopped"
            return ServerStatusResponse(**snapshot)
        try:
            server.stop()
            snapshot = _status_snapshot()
            snapshot["status"] = "stopped"
            snapshot["message"] = "Server stop signal sent"
            return ServerStatusResponse(**snapshot)
        except Exception as e:
            raise ServerLifecycleError(
                message="Failed to stop server",
                details={"error": str(e)},
            ) from e
    @router.get("/status", response_model=ServerStatusResponse, summary="Get server status")
    async def get_status():
        """Get current server status."""
        return ServerStatusResponse(**_status_snapshot())
    @router.get("/health", response_model=HealthResponse, summary="Health check")
    async def health_check():
        """Health check endpoint."""
        health_info = _health_snapshot()
        return HealthResponse(**health_info)
    @router.post("/log", response_model=LogResponse, summary="Log a message")
    async def log_message(request: Request, level: str = "INFO", message: str = ""):
        """Log a message."""
        payload: dict[str, Any] = {}
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        level = str(payload.get("level", level)).upper()
        message = str(payload.get("message", message))
        server.log(level=level, message=message)
        return LogResponse(
            level=level,
            message=message,
            timestamp=datetime.now().isoformat()
        )
    class PauseResumeRequest(BaseModel):
        """Pause/resume request model."""
        endpoint: str | None = None
        service: str | None = None
        method: str | None = "GET"
    class PauseResumeResponse(BaseModel, extra="allow"):
        """Pause/resume response model."""
        status: str
        message: str
        endpoint: str | None = None
        service: str | None = None
        method: str | None = None
        pause: dict[str, Any] | None = None
    @router.post("/pause", response_model=PauseResumeResponse, summary="Pause endpoint or service")
    async def pause_endpoint(request: PauseResumeRequest):
        """Pause a specific endpoint or service."""
        if request.service:
            if hasattr(server, "stop_services"):
                server.stop_services()
            return PauseResumeResponse(status="paused", message="Service paused", service=request.service)
        if request.endpoint:
            if hasattr(server, "pause_endpoint"):
                server.pause_endpoint(request.endpoint, request.method or "GET")
            pause_state = server.get_pause_state() if hasattr(server, "get_pause_state") else {}
            return {
                "status": "paused",
                "message": "Endpoint paused",
                "endpoint": request.endpoint,
                "service": None,
                "method": (request.method or "GET").upper(),
                "pause": pause_state,
            }
        if hasattr(server, "set_global_pause"):
            server.set_global_pause(True)
        pause_state = server.get_pause_state() if hasattr(server, "get_pause_state") else {}
        return {"status": "paused", "message": "Global pause enabled", "pause": pause_state}
    @router.post("/resume", response_model=PauseResumeResponse, summary="Resume endpoint or service")
    async def resume_endpoint(request: PauseResumeRequest):
        """Resume a paused endpoint or service."""
        if request.service:
            if hasattr(server, "start_services"):
                server.start_services()
            return PauseResumeResponse(status="resumed", message="Service resumed", service=request.service)
        if request.endpoint:
            if hasattr(server, "resume_endpoint"):
                server.resume_endpoint(request.endpoint, request.method or "GET")
            pause_state = server.get_pause_state() if hasattr(server, "get_pause_state") else {}
            return {
                "status": "resumed",
                "message": "Endpoint resumed",
                "endpoint": request.endpoint,
                "service": None,
                "method": (request.method or "GET").upper(),
                "pause": pause_state,
            }
        if hasattr(server, "set_global_pause"):
            server.set_global_pause(False)
        pause_state = server.get_pause_state() if hasattr(server, "get_pause_state") else {}
        return {"status": "resumed", "message": "Global pause disabled", "pause": pause_state}
    return router


def _create_flask_admin_router(server: AApiServer, prefix: str, tag: str, Blueprint) -> Any:
    """Create Flask Blueprint with admin endpoints."""
    from flask import request, jsonify, g
    from datetime import datetime
    from uuid import uuid4
    blueprint = Blueprint('admin', __name__, url_prefix=prefix)

    def _server_lifecycle_error_response(message: str, error: Exception):
        trace_id = getattr(g, "trace_id", None) or str(uuid4())
        lifecycle_error = ServerLifecycleError(message=message, details={"error": str(error)})
        body = create_error_response(lifecycle_error, trace_id=trace_id)
        status_code = get_http_status_code(lifecycle_error)
        return jsonify(body), status_code
    @blueprint.route('/start', methods=['POST'])
    def start_services():
        """Start domain services."""
        if hasattr(server, 'services_running') and server.services_running:
            status_info = server.status()
            return jsonify({
                "status": "already_running",
                "is_running": status_info.get("is_running", False),
                "services_running": True,
                "start_time": status_info.get("start_time"),
                "uptime_seconds": status_info.get("uptime_seconds"),
                "engine": getattr(server, 'engine_name', None),
                "host": getattr(server, '_host', None),
                "port": getattr(server, '_port', None),
                "endpoints_count": len(getattr(server, 'actions', []))
            })
        try:
            if hasattr(server, 'start_services'):
                server.start_services()
            else:
                server.pre_services_start()
                server.post_services_start()
            status_info = server.status()
            return jsonify({
                "status": "started",
                "is_running": status_info.get("is_running", False),
                "services_running": status_info.get("services_running", False),
                "start_time": status_info.get("start_time"),
                "uptime_seconds": status_info.get("uptime_seconds"),
                "engine": getattr(server, 'engine_name', None),
                "host": getattr(server, '_host', None),
                "port": getattr(server, '_port', None),
                "endpoints_count": len(getattr(server, 'actions', []))
            })
        except Exception as e:
            logger.error(f"Error starting services: {e}")
            return _server_lifecycle_error_response("Failed to start services", e)
    @blueprint.route('/restart', methods=['POST'])
    def restart_server():
        """Restart the server (HTTP and services)."""
        try:
            host = getattr(server, '_host', "0.0.0.0")
            port = getattr(server, '_port', 8000)
            server.restart(host=host, port=port)
            if hasattr(server, 'start_services'):
                server.start_services()
            status_info = server.status()
            return jsonify({
                "status": "restarted",
                "is_running": status_info.get("is_running", False),
                "services_running": status_info.get("services_running", False),
                "start_time": status_info.get("start_time"),
                "uptime_seconds": status_info.get("uptime_seconds"),
                "engine": getattr(server, 'engine_name', None),
                "host": getattr(server, '_host', None),
                "port": getattr(server, '_port', None),
                "endpoints_count": len(getattr(server, 'actions', []))
            })
        except Exception as e:
            logger.error(f"Error restarting server: {e}")
            return _server_lifecycle_error_response("Failed to restart server", e)
    @blueprint.route('/stop', methods=['POST'])
    def stop_server():
        """Stop the server (HTTP and services)."""
        if not server.is_running:
            return jsonify({
                "status": "not_running",
                "is_running": False,
                "services_running": False,
                "start_time": None,
                "uptime_seconds": None,
                "engine": getattr(server, 'engine_name', None),
                "host": getattr(server, '_host', None),
                "port": getattr(server, '_port', None),
                "endpoints_count": len(getattr(server, 'actions', []))
            })
        try:
            status_info = server.status()
            uptime = status_info.get("uptime_seconds")
            server.stop()
            return jsonify({
                "status": "stopped",
                "is_running": False,
                "services_running": False,
                "start_time": None,
                "uptime_seconds": uptime,
                "engine": getattr(server, 'engine_name', None),
                "host": getattr(server, '_host', None),
                "port": getattr(server, '_port', None),
                "endpoints_count": len(getattr(server, 'actions', []))
            })
        except Exception as e:
            logger.error(f"Error stopping server: {e}")
            return _server_lifecycle_error_response("Failed to stop server", e)
    @blueprint.route('/status', methods=['GET'])
    def get_status():
        """Get current server status."""
        status_info = server.status()
        return jsonify({
            "status": status_info.get("status", "unknown"),
            "is_running": status_info.get("is_running", False),
            "services_running": status_info.get("services_running", False),
            "start_time": status_info.get("start_time"),
            "uptime_seconds": status_info.get("uptime_seconds"),
            "engine": getattr(server, 'engine_name', None),
            "host": getattr(server, '_host', None),
            "port": getattr(server, '_port', None),
            "endpoints_count": len(getattr(server, 'actions', []))
        })
    @blueprint.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        health_info = server.health()
        return jsonify({
            "status": health_info.get("status", "unknown"),
            "timestamp": health_info.get("timestamp", datetime.now().isoformat()),
            "is_running": health_info.get("is_running", False),
            "services_running": getattr(server, 'services_running', False)
        })
    @blueprint.route('/log', methods=['POST'])
    def log_message():
        """Log a message."""
        level = request.args.get('level', 'INFO')
        message = request.args.get('message', '') or (request.get_json() or {}).get('message', '')
        server.log(level=level, message=message)
        return jsonify({
            "level": level,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    @blueprint.route('/pause', methods=['POST'])
    def pause_endpoint():
        """Pause a specific endpoint or service."""
        data = request.get_json() or {}
        endpoint = data.get('endpoint')
        service = data.get('service')
        # TODO: Implement endpoint pause/resume via middleware
        return jsonify({
            "status": "not_implemented",
            "message": "Endpoint pause/resume coming soon",
            "endpoint": endpoint,
            "service": service
        })
    @blueprint.route('/resume', methods=['POST'])
    def resume_endpoint():
        """Resume a paused endpoint or service."""
        data = request.get_json() or {}
        endpoint = data.get('endpoint')
        service = data.get('service')
        # TODO: Implement endpoint pause/resume via middleware
        return jsonify({
            "status": "not_implemented",
            "message": "Endpoint pause/resume coming soon",
            "endpoint": endpoint,
            "service": service
        })
    return blueprint


def register_admin_endpoints(app: Any, server: AApiServer, prefix: str = "/server", tag: str = "Server") -> None:
    """
    Register admin endpoints to an HTTP framework app (FastAPI or Flask).
    Args:
        app: HTTP framework app instance (FastAPI or Flask)
        server: AApiServer instance to manage
        prefix: URL prefix for admin endpoints (default: "/server")
        tag: OpenAPI tag name (default: "Server", only used for FastAPI)
    """
    router = create_admin_router(server, prefix=prefix, tag=tag)
    # Detect framework and register accordingly
    if hasattr(app, 'include_router'):
        # FastAPI - ensure tag is in openapi_tags
        # Get tag description from server if available (server-agnostic)
        tag_descriptions = getattr(server, 'get_openapi_tag_descriptions', lambda: {})()
        tag_description = tag_descriptions.get(tag, f"{tag} endpoints")
        existing_tags = getattr(app, "openapi_tags", None) or []
        tag_names = {t.get("name") if isinstance(t, dict) else t for t in existing_tags}
        if tag not in tag_names:
            tag_info = {"name": tag, "description": tag_description}
            app.openapi_tags = list(existing_tags) + [tag_info]
        app.include_router(router)
    elif hasattr(app, 'register_blueprint'):
        # Flask
        app.register_blueprint(router)
    else:
        raise ValueError(f"Unknown framework app type: {type(app)}. Expected FastAPI or Flask.")
    # Keep admin paths reachable during global pause when server supports pause policy.
    if hasattr(server, "_pause_allow_paths"):
        server._pause_allow_paths.update({
            f"{prefix}/status",
            f"{prefix}/health",
            f"{prefix}/log",
            f"{prefix}/pause",
            f"{prefix}/resume",
            f"{prefix}/start",
            f"{prefix}/stop",
            f"{prefix}/restart",
        })
    if hasattr(server, "_admin_auth_prefixes"):
        server._admin_auth_prefixes.add(prefix)

    logger.info(f"Admin endpoints registered: {prefix}/start, {prefix}/stop, {prefix}/restart, {prefix}/status, {prefix}/health, {prefix}/log, {prefix}/pause, {prefix}/resume")
