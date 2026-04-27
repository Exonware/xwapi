#exonware/xwapi/engines/websocket.py
"""
WebSocket Server Engine Implementation
WebSocket-based API server engine using FastAPI WebSocket support.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.12
"""

from typing import Any
from .http_base import AHttpServerEngineBase
from .contracts import ProtocolType
from exonware.xwapi.config import XWAPIConfig
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


class WebSocketServerEngine(AHttpServerEngineBase):
    """
    WebSocket Server Engine (FastAPI-based)
    Implements API server using FastAPI with WebSocket support.
    WebSocket provides persistent bidirectional communication.
    """

    def __init__(self):
        """Initialize WebSocket server engine."""
        super().__init__("websocket", protocol_type=ProtocolType.WEBSOCKET)
        self._app: Any | None = None
        self._websocket_endpoints: dict[str, Any] = {}  # Track WebSocket endpoints
    @property

    def protocol_type(self) -> ProtocolType:
        """Get protocol type (WEBSOCKET)."""
        return ProtocolType.WEBSOCKET
    @property

    def supports_admin_endpoints(self) -> bool:
        """WebSocket engine can support HTTP admin endpoints via FastAPI."""
        return True

    def create_app(self, config: XWAPIConfig) -> Any:
        """
        Create FastAPI application with WebSocket support.
        Args:
            config: XWAPI configuration
        Returns:
            FastAPI application instance with WebSocket support
        """
        from fastapi import FastAPI
        # Use FastAPIServerEngine logic for base app creation
        from exonware.xwapi.server.engines.fastapi import FastAPIServerEngine
        fastapi_engine = FastAPIServerEngine()
        app = fastapi_engine.create_app(config)
        self._app = app
        return app

    def _register_http_action(self, app: Any, action: Any, 
                             path: str, method: str) -> bool:
        """
        Register XWAction as WebSocket endpoint.
        Args:
            app: FastAPI application instance
            action: XWAction instance
            path: WebSocket endpoint path (e.g., '/ws/chat')
            method: Ignored for WebSocket (always uses WebSocket protocol)
        Returns:
            True if registration successful
        """
        from fastapi import WebSocket, WebSocketDisconnect
        # Get action function
        func = getattr(action, 'func', None)
        if not func and hasattr(action, '__call__'):
            func = action
        if not func:
            logger.error(f"Cannot register WebSocket action: no function found")
            return False
        # Create WebSocket endpoint handler
        async def websocket_handler(websocket: WebSocket):
            """
            WebSocket connection handler.
            Manages WebSocket lifecycle: accept, receive messages, execute action, send responses.
            """
            await websocket.accept()
            logger.info(f"WebSocket connection accepted at {path}")
            try:
                # Handle WebSocket messages
                while True:
                    # Receive message from client
                    data = await websocket.receive_json()
                    # Execute action with WebSocket context
                    try:
                        if hasattr(action, 'execute'):
                            # XWAction-like interface
                            from exonware.xwaction.context import ActionContext
                            context = ActionContext(
                                actor="websocket",
                                source="fastapi",
                                websocket=websocket  # Pass websocket to context
                            )
                            result = action.execute(context, **data)
                            # Handle async results
                            if hasattr(result, '__await__'):
                                result = await result
                            # Send response back to client
                            if hasattr(result, 'success') and not result.success:
                                await websocket.send_json({
                                    "error": getattr(result, 'error', 'Action execution failed'),
                                    "success": False
                                })
                            else:
                                response_data = getattr(result, 'data', result) if hasattr(result, 'data') else result
                                await websocket.send_json({
                                    "data": response_data,
                                    "success": True
                                })
                        else:
                            # Simple function call
                            # Pass websocket as first argument if function expects it
                            import inspect
                            sig = inspect.signature(func)
                            params = list(sig.parameters.keys())
                            if params and params[0] == 'websocket':
                                result = func(websocket, **data)
                            else:
                                result = func(**data)
                            if hasattr(result, '__await__'):
                                result = await result
                            await websocket.send_json({
                                "data": result,
                                "success": True
                            })
                    except Exception as e:
                        logger.error(f"Error executing WebSocket action: {e}")
                        await websocket.send_json({
                            "error": str(e),
                            "success": False
                        })
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected at {path}")
            except Exception as e:
                logger.error(f"WebSocket error at {path}: {e}")
                try:
                    await websocket.close()
                except Exception:
                    pass
        # Register WebSocket endpoint
        app.websocket(path)(websocket_handler)
        self._websocket_endpoints[path] = action
        logger.info(f"Registered WebSocket action at {path}")
        return True

    def generate_openapi(self, app: Any, actions: list[Any], 
                        config: XWAPIConfig) -> dict[str, Any]:
        """
        Generate OpenAPI specification for WebSocket endpoints.
        Args:
            app: FastAPI application instance
            actions: List of registered XWAction instances
            config: XWAPI configuration
        Returns:
            OpenAPI 3.1 specification dictionary
        """
        # FastAPI has built-in OpenAPI generation
        if hasattr(app, 'openapi'):
            spec = app.openapi()
        else:
            # Fallback to base implementation
            spec = super().generate_openapi(app, actions, config)
        # Add WebSocket endpoints to OpenAPI spec
        # OpenAPI 3.1 supports WebSocket (though Swagger UI may not fully support it)
        for path, action in self._websocket_endpoints.items():
            if path not in spec["paths"]:
                spec["paths"][path] = {}
            spec["paths"][path]["get"] = {  # WebSocket connections start with HTTP GET/UPGRADE
                "summary": f"WebSocket endpoint: {getattr(action, 'api_name', path)}",
                "description": "WebSocket connection endpoint",
                "x-websocket": True,  # Custom extension to indicate WebSocket
                "responses": {
                    "101": {
                        "description": "Switching Protocols (WebSocket upgrade)"
                    }
                }
            }
        return spec

    def start_server(self, app: Any, host: str = "0.0.0.0", 
                    port: int = 8000, **kwargs) -> None:
        """
        Start WebSocket server using uvicorn.
        Args:
            app: FastAPI application instance
            host: Host to bind to
            port: Port to bind to
            **kwargs: Additional uvicorn options
        """
        import uvicorn
        # Default uvicorn options
        uvicorn_kwargs = {
            "host": host,
            "port": port,
            "log_level": kwargs.pop("log_level", "info"),
            **kwargs
        }
        logger.info(f"Starting WebSocket server on {host}:{port}")
        uvicorn.run(app, **uvicorn_kwargs)

    def stop_server(self, app: Any) -> None:
        """
        Stop WebSocket server.
        Args:
            app: FastAPI application instance
        """
        logger.info("Stopping WebSocket server")
        # Handled by uvicorn shutdown signals
