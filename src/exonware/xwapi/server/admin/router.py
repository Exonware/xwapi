#exonware/xwapi/src/exonware/xwapi/server/admin/router.py
"""
Admin router for FastAPI engine.
Creates FastAPI router with server management endpoints.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.1
"""

from typing import Any, Optional
from datetime import datetime
from exonware.xwapi.server.base import AApiServer
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
    router = APIRouter(prefix=prefix, tags=[tag])
    # Response models
    class ServerStatusResponse(BaseModel):
        """Server status response model."""
        status: str
        is_running: bool
        services_running: bool = False
        start_time: Optional[str] = None
        uptime_seconds: Optional[float] = None
        engine: Optional[str] = None
        host: Optional[str] = None
        port: Optional[int] = None
        endpoints_count: int = 0
    class HealthResponse(BaseModel):
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
        """Start domain services."""
        if hasattr(server, 'services_running') and server.services_running:
            status_info = server.status()
            return ServerStatusResponse(
                status="already_running",
                is_running=status_info.get("is_running", False),
                services_running=True,
                start_time=status_info.get("start_time"),
                uptime_seconds=status_info.get("uptime_seconds"),
                engine=getattr(server, 'engine_name', None),
                host=getattr(server, '_host', None),
                port=getattr(server, '_port', None),
                endpoints_count=len(getattr(server, 'actions', []))
            )
        try:
            # Start services using lifecycle hooks
            if hasattr(server, 'start_services'):
                server.start_services()
            else:
                # Fallback: call pre_services_start and post_services_start hooks
                server.pre_services_start()
                server.post_services_start()
            status_info = server.status()
            return ServerStatusResponse(
                status="started",
                is_running=status_info.get("is_running", False),
                services_running=status_info.get("services_running", False),
                start_time=status_info.get("start_time"),
                uptime_seconds=status_info.get("uptime_seconds"),
                engine=getattr(server, 'engine_name', None),
                host=getattr(server, '_host', None),
                port=getattr(server, '_port', None),
                endpoints_count=len(getattr(server, 'actions', []))
            )
        except Exception as e:
            logger.error(f"Error starting services: {e}")
            raise
    @router.post("/restart", response_model=ServerStatusResponse, summary="Restart server")
    async def restart_server():
        """Restart the server (HTTP and services)."""
        try:
            # Get current host/port before restart
            host = getattr(server, '_host', "0.0.0.0")
            port = getattr(server, '_port', 8000)
            # Use AApiServer's restart method
            server.restart(host=host, port=port)
            # Start services if they were running before
            if hasattr(server, 'start_services'):
                server.start_services()
            status_info = server.status()
            return ServerStatusResponse(
                status="restarted",
                is_running=status_info.get("is_running", False),
                services_running=status_info.get("services_running", False),
                start_time=status_info.get("start_time"),
                uptime_seconds=status_info.get("uptime_seconds"),
                engine=getattr(server, 'engine_name', None),
                host=getattr(server, '_host', None),
                port=getattr(server, '_port', None),
                endpoints_count=len(getattr(server, 'actions', []))
            )
        except Exception as e:
            logger.error(f"Error restarting server: {e}")
            raise
    @router.post("/stop", response_model=ServerStatusResponse, summary="Stop server")
    async def stop_server():
        """Stop the server (HTTP and services)."""
        if not server.is_running:
            return ServerStatusResponse(
                status="not_running",
                is_running=False,
                services_running=False,
                start_time=None,
                uptime_seconds=None,
                engine=getattr(server, 'engine_name', None),
                host=getattr(server, '_host', None),
                port=getattr(server, '_port', None),
                endpoints_count=len(getattr(server, 'actions', []))
            )
        try:
            # Get uptime before stopping
            status_info = server.status()
            uptime = status_info.get("uptime_seconds")
            # Stop server (includes services)
            server.stop()
            return ServerStatusResponse(
                status="stopped",
                is_running=False,
                services_running=False,
                start_time=None,
                uptime_seconds=uptime,
                engine=getattr(server, 'engine_name', None),
                host=getattr(server, '_host', None),
                port=getattr(server, '_port', None),
                endpoints_count=len(getattr(server, 'actions', []))
            )
        except Exception as e:
            logger.error(f"Error stopping server: {e}")
            raise
    @router.get("/status", response_model=ServerStatusResponse, summary="Get server status")
    async def get_status():
        """Get current server status."""
        status_info = server.status()
        return ServerStatusResponse(
            status=status_info.get("status", "unknown"),
            is_running=status_info.get("is_running", False),
            services_running=status_info.get("services_running", False),
            start_time=status_info.get("start_time"),
            uptime_seconds=status_info.get("uptime_seconds"),
            engine=getattr(server, 'engine_name', None),
            host=getattr(server, '_host', None),
            port=getattr(server, '_port', None),
            endpoints_count=len(getattr(server, 'actions', []))
        )
    @router.get("/health", response_model=HealthResponse, summary="Health check")
    async def health_check():
        """Health check endpoint."""
        health_info = server.health()
        return HealthResponse(
            status=health_info.get("status", "unknown"),
            timestamp=health_info.get("timestamp", datetime.now().isoformat()),
            is_running=health_info.get("is_running", False),
            services_running=getattr(server, 'services_running', False)
        )
    @router.post("/log", response_model=LogResponse, summary="Log a message")
    async def log_message(level: str = "INFO", message: str = ""):
        """Log a message."""
        server.log(level=level, message=message)
        return LogResponse(
            level=level,
            message=message,
            timestamp=datetime.now().isoformat()
        )
    class PauseResumeRequest(BaseModel):
        """Pause/resume request model."""
        endpoint: Optional[str] = None
        service: Optional[str] = None
    class PauseResumeResponse(BaseModel):
        """Pause/resume response model."""
        status: str
        message: str
        endpoint: Optional[str] = None
        service: Optional[str] = None
    @router.post("/pause", response_model=PauseResumeResponse, summary="Pause endpoint or service")
    async def pause_endpoint(request: PauseResumeRequest):
        """Pause a specific endpoint or service."""
        # TODO: Implement endpoint pause/resume via middleware
        return PauseResumeResponse(
            status="not_implemented",
            message="Endpoint pause/resume coming soon",
            endpoint=request.endpoint,
            service=request.service
        )
    @router.post("/resume", response_model=PauseResumeResponse, summary="Resume endpoint or service")
    async def resume_endpoint(request: PauseResumeRequest):
        """Resume a paused endpoint or service."""
        # TODO: Implement endpoint pause/resume via middleware
        return PauseResumeResponse(
            status="not_implemented",
            message="Endpoint pause/resume coming soon",
            endpoint=request.endpoint,
            service=request.service
        )
    return router


def _create_flask_admin_router(server: AApiServer, prefix: str, tag: str, Blueprint) -> Any:
    """Create Flask Blueprint with admin endpoints."""
    from flask import request, jsonify
    from datetime import datetime
    blueprint = Blueprint('admin', __name__, url_prefix=prefix)
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
            return jsonify({"error": str(e)}), 500
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
            return jsonify({"error": str(e)}), 500
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
            return jsonify({"error": str(e)}), 500
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
    logger.info(f"Admin endpoints registered: {prefix}/start, {prefix}/stop, {prefix}/restart, {prefix}/status, {prefix}/health, {prefix}/log, {prefix}/pause, {prefix}/resume")
