#exonware/xwapi/engines/flask.py
"""
Alternate HTTP **server engine**: Flask (WSGI) for the same exposable-action registration model.

Swap with ``engine="flask"`` at app/server construction when deployment targets WSGI stacks;
default remains FastAPI for OpenAPI/async-first apps.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.4
"""

from typing import Any, Optional
from uuid import uuid4
from datetime import datetime
from .http_base import AHttpServerEngineBase
from .contracts import ProtocolType
from exonware.xwapi.config import XWAPIConfig
from exonware.xwapi.errors import (
    XWAPIError,
    InternalError,
    create_error_response,
    get_http_status_code,
)
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


class FlaskServerEngine(AHttpServerEngineBase):
    """
    Flask Server Engine
    Implements API server using Flask framework.
    Uses XWAction's FlaskActionEngine internally for action execution.
    """

    def __init__(self):
        """Initialize Flask server engine."""
        super().__init__("flask")
        self._app: Any | None = None
        self._protocol_type = ProtocolType.HTTP_REST  # Flask is HTTP REST
    @property

    def protocol_type(self) -> ProtocolType:
        """Get protocol type (HTTP_REST)."""
        return self._protocol_type

    def create_app(self, config: XWAPIConfig) -> Any:
        """
        Create Flask application with xwapi features.
        Features:
        - Automatic OpenAPI generation
        - Versioning support
        - Uniform error model with trace_id
        - Global exception handlers
        Args:
            config: XWAPI configuration
        Returns:
            Flask application instance
        """
        from flask import Flask, request, g, jsonify, make_response
        from werkzeug.exceptions import HTTPException as WerkzeugHTTPException
        # Create Flask app
        app = Flask(__name__)
        # Set app configuration from XWAPIConfig
        app.config['API_TITLE'] = config.title
        app.config['API_VERSION'] = config.version
        app.config['API_DESCRIPTION'] = config.description or ""
        # Apply OpenAPI tags if configured
        if config.openapi_tags:
            app.config['OPENAPI_TAGS'] = config.openapi_tags
            logger.debug(f"Applied {len(config.openapi_tags)} OpenAPI tags")
        # Register middleware (trace_id, etc.)
        self._register_middleware(app)
        # Register global exception handlers
        self._register_error_handlers(app)
        # Add OpenAPI endpoint
        @app.route("/openapi.json", methods=["GET"])
        def openapi_json():
            # Generate fresh spec (or use cached)
            actions = [] # TODO: Need a way to get registered actions if using XWAction
            # Note: For now we return the spec generated from registered routes
            # Real implementation might need access to action registry
            spec = self.generate_openapi(app, [], config)
            return jsonify(spec)
        self._app = app
        return app

    def _register_middleware(self, app: Any) -> None:
        """Register Flask middleware (before/after request)."""
        from flask import request, g
        @app.before_request
        def set_trace_id():
            """Set trace_id for request."""
            trace_id = request.headers.get("X-Trace-Id")
            if not trace_id:
                trace_id = str(uuid4())
            g.trace_id = trace_id
        @app.after_request
        def add_headers(response):
            """Add X-Trace-Id and other headers."""
            if hasattr(g, "trace_id"):
                response.headers["X-Trace-Id"] = g.trace_id
            # Add version info (lazy-import to avoid circular import)
            from exonware.xwapi.version import __version__
            response.headers["X-XWAPI-Version"] = __version__
            # Handle deprecation (if set in g)
            if hasattr(g, "deprecated") and g.deprecated:
                response.headers["Deprecation"] = "true"
                if hasattr(g, "sunset") and g.sunset:
                    response.headers["Sunset"] = g.sunset
            return response

    def _register_error_handlers(self, app: Any) -> None:
        """Register uniform error handlers."""
        from flask import jsonify, request, g
        from werkzeug.exceptions import HTTPException as WerkzeugHTTPException
        def get_trace_id():
            return getattr(g, "trace_id", str(uuid4()))
        @app.errorhandler(XWAPIError)
        def handle_xwapi_error(exc):
            trace_id = get_trace_id()
            status_code = get_http_status_code(exc)
            # Log error
            logger.error(
                f"API error: {exc.code} - {exc.message}",
                extra={
                    "trace_id": trace_id,
                    "error_code": exc.code,
                    "path": request.path,
                    "method": request.method,
                    "details": exc.details,
                }
            )
            response = create_error_response(exc, trace_id=trace_id)
            return jsonify(response), status_code
        @app.errorhandler(WerkzeugHTTPException)
        def handle_http_exception(exc):
            trace_id = get_trace_id()
            error = XWAPIError(
                message=exc.description,
                code=f"HTTP_{exc.code}",
                details={"status_code": exc.code},
            )
            response = create_error_response(error, trace_id=trace_id)
            return jsonify(response), exc.code
        @app.errorhandler(Exception)
        def handle_generic_exception(exc):
            trace_id = get_trace_id()
            # Similar logic to app.py generic_exception_handler
            error_type = type(exc).__name__
            error_message = str(exc) or "Internal server error"
            # Map known errors
            if any(k in error_type.lower() for k in ['connection', 'timeout']):
                error = InternalError(
                    message=f"Connection error: {error_message}",
                    code="ConnectionError",
                    details={"exception_type": error_type}
                )
            else:
                error = InternalError(
                    message=error_message,
                    code="InternalError",
                    details={"exception_type": error_type}
                )
            logger.exception(
                f"Unhandled exception: {error_type}",
                extra={"trace_id": trace_id}
            )
            response = create_error_response(error, trace_id=trace_id)
            return jsonify(response), 500

    def _register_http_action(self, app: Any, action: Any, 
                              path: str, method: str) -> bool:
        """
        Register XWAction as Flask endpoint.
        Uses XWAction's FlaskActionEngine.register_action() method if available,
        otherwise uses fallback registration.
        Args:
            app: Flask application instance
            action: XWAction instance
            path: Endpoint path
            method: HTTP method
        Returns:
            True if registration successful
        """
        from exonware.xwaction.engines.flask import FlaskActionEngine
        # Get or create FlaskActionEngine
        flask_action_engine = self._action_engine_registry.get_engine("flask")
        if not flask_action_engine:
            # Register FlaskActionEngine if not present
            flask_action_engine = FlaskActionEngine()
            self._action_engine_registry.register(flask_action_engine)
        # Setup engine with app
        flask_action_engine.setup({"app": app})
        # Use FlaskActionEngine's register_action method
        success = flask_action_engine.register_action(action, app, path, method)
        if success:
            logger.info(f"Registered action '{getattr(action, 'api_name', 'unknown')}' as {method} {path}")
        else:
            logger.warning(f"Failed to register action '{getattr(action, 'api_name', 'unknown')}', using fallback")
            return self._register_fallback(app, action, path, method)
        return success

    def _register_fallback(self, app: Any, action: Any, 
                          path: str, method: str) -> bool:
        """
        Fallback registration when XWAction is not available.
        Args:
            app: Flask application instance
            action: Action object (may not be XWAction)
            path: Endpoint path
            method: HTTP method
        Returns:
            True if registration successful
        """
        from flask import request, jsonify
        # Get function from action
        func = getattr(action, 'func', None)
        if not func and hasattr(action, '__call__'):
            func = action
        if not func:
            logger.error(f"Cannot register action: no function found")
            return False
        # Create route handler
        # We use async def to support both sync and async actions (Flask 2.0+)
        async def route_handler(**kwargs):
            try:
                # Try to execute action
                if hasattr(action, 'execute'):
                    # XWAction-like interface
                    from exonware.xwaction.context import ActionContext
                    context = ActionContext(actor="api", source="flask")
                    result = action.execute(context, **kwargs)
                    if hasattr(result, 'success') and not result.success:
                        from flask import abort
                        abort(400, getattr(result, 'error', 'Action execution failed'))
                    # Handle async results from execute if it returns a coroutine
                    if hasattr(result, '__await__'):
                        result = await result
                    data = getattr(result, 'data', result) if hasattr(result, 'data') else result
                    return jsonify(data)
                else:
                    # Simple function call
                    result = func(**kwargs)
                    if hasattr(result, '__await__'):
                        result = await result
                    return jsonify(result)
            except Exception as e:
                logger.error(f"Action execution failed: {e}")
                from flask import abort
                abort(500, str(e))
        # Register route
        method_upper = method.upper()
        if method_upper == "GET":
            app.route(path, methods=['GET'])(route_handler)
        elif method_upper == "POST":
            app.route(path, methods=['POST'])(route_handler)
        elif method_upper == "PUT":
            app.route(path, methods=['PUT'])(route_handler)
        elif method_upper == "PATCH":
            app.route(path, methods=['PATCH'])(route_handler)
        elif method_upper == "DELETE":
            app.route(path, methods=['DELETE'])(route_handler)
        else:
            app.route(path, methods=['POST'])(route_handler)
        logger.info(f"Registered action (fallback) as {method} {path}")
        return True

    def generate_openapi(self, app: Any, actions: list[Any], 
                        config: XWAPIConfig) -> dict[str, Any]:
        """
        Generate OpenAPI specification for Flask.
        Flask doesn't have built-in OpenAPI generation like FastAPI,
        so we generate it from registered actions using the base implementation.
        Args:
            app: Flask application instance
            actions: List of registered XWAction instances
            config: XWAPI configuration
        Returns:
            OpenAPI 3.1 specification dictionary
        """
        # Use generic base implementation for action-based generation
        spec = super().generate_openapi(app, actions, config)
        # Extend with Flask-specific route extraction if available
        if hasattr(app, 'url_map'):
            for rule in app.url_map.iter_rules():
                if rule.endpoint != 'static':
                    path = rule.rule
                    # Convert Flask path vars <var> to OpenAPI {var}
                    # Simple regex or string replacement could be done here if needed
                    # For now, we trust Flask rules match reasonably well or require manual cleanup
                    methods = [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]
                    if methods:
                        method = methods[0].lower()
                        if path not in spec["paths"]:
                            spec["paths"][path] = {}
                        # Only add if not already present (prefer action metadata)
                        if method not in spec["paths"][path]:
                            spec["paths"][path][method] = {
                                "summary": f"{rule.endpoint}",
                                "responses": {
                                    "200": {
                                        "description": "Success"
                                    }
                                }
                            }
        return spec

    def start_server(self, app: Any, host: str = "0.0.0.0", 
                    port: int = 8000, **kwargs) -> None:
        """
        Start Flask server.
        Args:
            app: Flask application instance
            host: Host to bind to
            port: Port to bind to
            **kwargs: Additional Flask options (debug, threaded, etc.)
        """
        # Default Flask options
        flask_kwargs = {
            "host": host,
            "port": port,
            "debug": kwargs.pop("debug", False),
            "threaded": kwargs.pop("threaded", True),
            **kwargs
        }
        logger.info(f"Starting Flask server on {host}:{port}")
        app.run(**flask_kwargs)

    def stop_server(self, app: Any) -> None:
        """
        Stop Flask server.
        Note: Flask's app.run() blocks, so this is mainly for graceful shutdown
        in production deployments (e.g., with gunicorn, uWSGI, etc.).
        Args:
            app: Flask application instance
        """
        logger.info("Stopping Flask server")
        # In production, this would be handled by the process manager
        # For development, app.run() handles shutdown signals
