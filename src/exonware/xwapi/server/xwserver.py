#!/usr/bin/env python3
"""
#exonware/xwapi/src/exonware/xwapi/server/xwserver.py
XWApiServer — production server for *exposable actions* and HTTP APIs.

Registers and serves ``XWAction`` operations through pluggable **server engines** (FastAPI by
default for OpenAPI/ASGI; Flask as an alternate WSGI engine). Same action contracts; choose
the engine when constructing the server. *Build once, publish anywhere* applies to how you
author actions/entities; HTTP engine selection is a deployment concern.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.9
"""

from typing import Any
import sys
import os
import socket
import subprocess
import platform
import inspect
import asyncio
from dataclasses import replace
from exonware.xwapi.server.base import AApiServer
from exonware.xwapi.config import XWAPIConfig
from exonware.xwapi.server.engines import api_server_engine_registry, IApiServerEngine
from exonware.xwapi.server.engines.contracts import ProtocolType
from exonware.xwapi.errors import XWAPIError, ValidationError, ServerLifecycleError
from exonware.xwapi.server.pipeline import ActionPipelineManager
from exonware.xwapi.providers import (
    LocalAuthProvider,
    XWAuthLibraryProvider,
    InMemoryStorageProvider,
    XWStorageProvider,
    InMemoryPaymentProvider,
)
from exonware.xwapi.token_management import APITokenManager
from exonware.xwapi.server.middleware.pause import PauseControlMiddleware
from exonware.xwapi.server.middleware.admin_auth import AdminTokenMiddleware
from exonware.xwapi.server.middleware.api_token import APITokenMiddleware
from exonware.xwsystem import JsonSerializer, get_logger
# Import agent engines for future use
from exonware.xwapi.client.engines import api_agent_engine_registry, IApiAgentEngine
logger = get_logger(__name__)

class XWApiServer(AApiServer):
    """
    Concrete API server: publish exposable actions over a chosen HTTP engine.

    Strategy pattern over registered engines (``fastapi``, ``flask``, …) so you keep one
    action model and swap framework at construction time. FastAPI unlocks the full async/OpenAPI
    stack; Flask supports WSGI-oriented deployments. Integrates with XWAction engines for routes.

    Example:
        >>> from exonware.xwapi import XWApiServer, XWAPIConfig
        >>> from exonware.xwaction import XWAction
        >>> 
        >>> @XWAction(operationId="hello", profile="endpoint")
        >>> def hello(name: str = "World") -> dict:
        ...     return {"message": f"Hello, {name}!"}
        >>> 
        >>> config = XWAPIConfig(title="My API", version="1.0.0")
        >>> server = XWApiServer(engine="fastapi", config=config)
        >>> server.register_action(hello, path="/hello", method="GET")
        >>> server.start(host="0.0.0.0", port=8000)
    """

    def __init__(
        self,
        engine: str = "fastapi",
        config: XWAPIConfig | None = None,
        server_id: str | None = None,
        max_instances: int = 1,
        runtime_dir: str | None = None,
        services: Any | None = None,
        auth: Any | None = None,
        storage: Any | None = None,
        auth_provider: Any | None = None,
        storage_provider: Any | None = None,
        payment_provider: Any | None = None,
        admin_token: str | None = None,
        **kwargs
    ):
        """
        Initialize XWApiServer with chosen engine strategy.
        Args:
            engine: Engine name ('fastapi', 'flask', etc.)
            config: Optional XWAPIConfig instance
            server_id: Unique identifier for this server instance (for governance)
            max_instances: Maximum number of instances per server_id (default: 1)
            runtime_dir: Directory for lockfiles (default: .xwapi_runtime in current dir)
            services: Optional services configuration. Can be:
                - A list [prefix, services_obj] (e.g., ["", xwauth services provider])
                - A services object with AUTH_SERVICES attribute
            auth: Optional xwauth library instance
            storage: Optional xwstorage library instance
            auth_provider: Optional auth provider adapter (defaults to xwauth adapter or local provider)
            storage_provider: Optional storage provider adapter (defaults to xwstorage adapter or in-memory)
            payment_provider: Optional payment provider adapter (defaults to in-memory)
            admin_token: Optional token to protect mutating admin endpoints.
            **kwargs: Additional config options (merged into config)
        Raises:
            XWAPIError: If engine not found or initialization fails
        """
        super().__init__()
        # Validate engine parameter
        if engine is None:
            raise TypeError("Engine cannot be None. Please provide a valid engine name (e.g., 'fastapi').")
        if not isinstance(engine, str):
            raise TypeError(f"Engine must be a string, got {type(engine).__name__}. Please provide a valid engine name (e.g., 'fastapi').")
        # Instance governance
        self._server_id = server_id or f"xwapi_server_{id(self)}"
        self._max_instances = max_instances
        self._runtime_dir = runtime_dir
        # Register with instance registry
        from exonware.xwapi.server.governance import get_registry
        registry = get_registry(max_instances=max_instances)
        if not registry.register(self._server_id, self):
            raise XWAPIError(
                f"Max instances ({max_instances}) exceeded for server_id: {self._server_id}. "
                f"Another instance is already running."
            )
        # Initialize lockfile manager
        self._lockfile_manager = None
        from exonware.xwapi.server.governance import create_lockfile_manager
        self._lockfile_manager = create_lockfile_manager(self._server_id, runtime_dir)
        # Get engine strategy from registry
        self._engine: IApiServerEngine | None = api_server_engine_registry.get_engine(engine)
        if not self._engine:
            available = ", ".join(api_server_engine_registry.list_engines())
            raise XWAPIError(
                f"Unknown API server engine: '{engine}'. "
                f"Available engines: {available}"
            )
        self._engine_name = engine
        # Merge kwargs into config
        if config:
            # Create a copy of the config to ensure immutability
            self.config = replace(config)
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
        else:
            self.config = XWAPIConfig(**kwargs)
        # Admin endpoints configuration
        self._admin_enabled = True  # Enable admin endpoints by default
        self._admin_prefix = "/server"
        self._admin_tag = "Server"
        token_from_env = os.environ.get("XWAPI_ADMIN_TOKEN", "")
        self._admin_token = (admin_token if admin_token is not None else token_from_env).strip() or None
        self._admin_protect_reads = os.environ.get("XWAPI_ADMIN_PROTECT_READ", "").strip().lower() in {"1", "true", "yes", "on"}
        env_mode = os.environ.get("XWAPI_ENV", "").strip().lower()
        insecure_admin_override = os.environ.get("XWAPI_ALLOW_INSECURE_ADMIN", "").strip().lower() in {"1", "true", "yes", "on"}
        if env_mode in {"prod", "production"} and not self._admin_token and not insecure_admin_override:
            raise XWAPIError(
                "Admin token is required in production mode. "
                "Set XWAPI_ADMIN_TOKEN or explicitly opt in with XWAPI_ALLOW_INSECURE_ADMIN=1."
            )
        if env_mode in {"prod", "production"} and self._admin_token:
            # In production, keep operational reads protected by default when token auth is enabled.
            self._admin_protect_reads = True
        self._admin_auth_prefixes: set[str] = {self._admin_prefix}
        self._api_token_middleware_enabled = (
            os.environ.get("XWAPI_API_TOKEN_MIDDLEWARE", "").strip().lower() in {"1", "true", "yes", "on"}
        )
        self._api_token_require_bearer = (
            os.environ.get("XWAPI_API_TOKEN_REQUIRE_BEARER", "").strip().lower() in {"1", "true", "yes", "on"}
        )
        self._api_token_enforce_scopes = (
            os.environ.get("XWAPI_API_TOKEN_ENFORCE_SCOPES", "").strip().lower() in {"1", "true", "yes", "on"}
        )
        self._api_token_scope_deny_unmapped = (
            os.environ.get("XWAPI_API_TOKEN_SCOPE_DENY_UNMAPPED", "").strip().lower() in {"1", "true", "yes", "on"}
        )
        try:
            self._api_token_usage_amount = float(os.environ.get("XWAPI_API_TOKEN_USAGE_AMOUNT", "0") or 0.0)
        except Exception:
            self._api_token_usage_amount = 0.0
        default_scopes_raw = os.environ.get("XWAPI_API_TOKEN_DEFAULT_REQUIRED_SCOPES", "")
        self._api_token_default_required_scopes: set[str] = {
            s.strip() for s in default_scopes_raw.split(",") if s.strip()
        }
        extra_exempt_raw = os.environ.get("XWAPI_API_TOKEN_EXEMPT_PATHS", "")
        extra_exempt = {p.strip() for p in extra_exempt_raw.split(",") if p.strip()}
        self._api_token_exempt_paths: set[str] = {
            "/",
            "/health",
            "/openapi.json",
            "/openapi.yaml",
            "/docs",
            "/redoc",
            *extra_exempt,
        }
        self._api_token_scope_rules: list[dict[str, Any]] = []
        self._tenant_reject_conflicting_override = (
            os.environ.get("XWAPI_TENANT_REJECT_CONFLICTING_OVERRIDE", "").strip().lower() in {"1", "true", "yes", "on"}
        )
        self._tenant_require_authenticated_source = (
            os.environ.get("XWAPI_TENANT_REQUIRE_AUTH_SOURCE", "").strip().lower() in {"1", "true", "yes", "on"}
        )

        # Initialize core state BEFORE engine/app creation so attributes exist
        # even if engines access them during startup.
        self._actions: list[Any] = []
        self._collected_schemas: dict[str, dict[str, Any]] = {}  # Store collected schemas for OpenAPI
        # Initialize handlers list to prevent AttributeError in stop()
        self._flushable_handlers: list[Any] = []
        self._global_paused = False
        self._paused_routes: set[tuple[str, str]] = set()
        self._pause_allow_paths: set[str] = {
            "/health",
            "/server/status",
            "/server/pipeline",
            "/server/pause",
            "/server/resume",
            "/server/start",
            "/server/stop",
            "/server/restart",
        }
        # Outbox + singleton worker pipeline:
        # - outbox layer keeps durable job intent
        # - worker layer executes jobs serially in one singleton worker
        self._pipeline = ActionPipelineManager(owner_id=self._server_id)
        self._registered_action_handlers: dict[str, Any] = {}
        # Provider-style integrations (library-first: xwauth/xwstorage adapters).
        self._auth_instance = auth
        self._storage_instance = storage
        self._auth_provider = auth_provider or (
            XWAuthLibraryProvider(auth) if auth is not None else LocalAuthProvider()
        )
        self._storage_provider = storage_provider or (
            XWStorageProvider(storage) if storage is not None else InMemoryStorageProvider()
        )
        self._payment_provider = payment_provider or InMemoryPaymentProvider()
        self._token_manager = APITokenManager(
            auth_provider=self._auth_provider,
            storage_provider=self._storage_provider,
            payment_provider=self._payment_provider,
            storage_prefix=f"xwapi/{self._server_id}/token_mgmt",
        )

        # Create app using strategy
        try:
            self._app = self._engine.create_app(self.config)
            # Store server reference in app state
            if hasattr(self._app, 'state'):
                self._app.state.xwapi_server = self
                # Initialize collected schemas in app state
                self._app.state.xwapi_collected_schemas = self._collected_schemas
                # Register generic callback for action registration (engine-agnostic)
                # FastAPIActionEngine will call this when actions are registered
                def on_action_registered(action: Any) -> None:
                    """Callback for when actions are registered by engines."""
                    self._collect_action_schemas(action)
                    # Update app state with latest schemas
                    self._app.state.xwapi_collected_schemas = self._collected_schemas
                self._app.state.on_action_registered = on_action_registered
                # Request-level pause control for endpoint/service freezing.
                if hasattr(self._app, "add_middleware"):
                    self._app.add_middleware(PauseControlMiddleware)
                    if self._api_token_middleware_enabled:
                        self._app.add_middleware(APITokenMiddleware)
                    self._app.add_middleware(AdminTokenMiddleware)
            # Register admin endpoints if enabled
            if self._admin_enabled:
                self.register_admin_endpoints(
                    enabled=True,
                    prefix=self._admin_prefix,
                    tag=self._admin_tag
                )
        except Exception as e:
            raise XWAPIError(f"Failed to create {engine} app: {e}") from e
        # Track server state
        self._is_running = False
        self._services_running = False
        self._host: str | None = None
        self._port: int | None = None
        # Services configuration (for xwauth-style services)
        self._services_config: Any | None = None
        self._auth_instance = auth
        # Auto-register services if provided
        if services is not None:
            # services can be a list [prefix, services_obj] or just services_obj
            if isinstance(services, list) and len(services) >= 2:
                prefix, services_obj = services[0], services[1]
                self._services_config = services_obj
            else:
                self._services_config = services
            # Store auth instance
            self._auth_instance = auth
            # Auto-register services (will create auth if needed)
            self._auto_register_services()
        logger.info(f"Initialized XWApiServer with engine: {engine}, server_id: {self._server_id}")

    def _auto_register_services(self) -> None:
        """Auto-register services if services config and auth are available."""
        if self._services_config is None:
            return
        # Try to create auth if not provided
        if self._auth_instance is None:
            try:
                import os
                from exonware.xwauth import XWAuth
                from exonware.xwauth.config import XWAuthConfig, DEFAULT_TEST_CLIENTS
                storage = self._storage_instance
                config_obj = XWAuthConfig(
                    jwt_secret=os.environ.get("XWAUTH_JWT_SECRET", "xwauth-lib-integration-change-in-production"),
                    registered_clients=DEFAULT_TEST_CLIENTS,
                )
                self._auth_instance = XWAuth(config=config_obj, storage=storage)
            except ImportError:
                logger.warning("xwauth not available, skipping auto-registration")
                return
        # Determine issuer
        host = os.environ.get("XWAUTH_HOST", "127.0.0.1")
        port = int(os.environ.get("XWAUTH_PORT", "8000"))
        issuer = f"http://{host}:{port}"
        # Register services
        self.register_services(
            services=self._services_config,
            auth=self._auth_instance,
            issuer=issuer
        )
        # After registering services, collect schemas from all registered actions
        # Services may have registered actions via FastAPIActionEngine, which will have
        # triggered the on_action_registered callback. But we also collect from routes
        # to ensure we catch everything.
        if hasattr(self, '_actions'):
            for action in self._actions:
                self._collect_action_schemas(action)
        # Also scan app routes to collect schemas from any actions registered directly
        # (e.g., via manual service handler registration)
        if hasattr(self, '_app') and self._app and hasattr(self._app, 'routes'):
            for route in self._app.routes:
                if hasattr(route, 'endpoint'):
                    handler = route.endpoint
                    # Try to find xwaction attribute in handler
                    action_attr = getattr(handler, 'xwaction', None)
                    if not action_attr and hasattr(handler, '__wrapped__'):
                        action_attr = getattr(handler.__wrapped__, 'xwaction', None)
                    if action_attr:
                        self._collect_action_schemas(action_attr)
        # Update app state with latest collected schemas
        if hasattr(self, '_app') and self._app and hasattr(self._app, 'state'):
            self._app.state.xwapi_collected_schemas = self._collected_schemas
    @property

    def app(self) -> Any:
        """
        Get underlying framework app instance.
        Returns:
            Framework-specific app (FastAPI, Flask, etc.)
        """
        return self._app
    @property

    def engine(self) -> IApiServerEngine:
        """
        Get the engine instance.
        Returns:
            IApiServerEngine instance
        """
        return self._engine
    @property

    def actions(self) -> list[Any]:
        """
        Get list of registered actions.
        Returns:
            List of registered XWAction instances
        """
        return self._actions.copy()
    @property

    def is_running(self) -> bool:
        """Check if HTTP server is running."""
        return self._is_running
    @property

    def services_running(self) -> bool:
        """Check if domain services are running."""
        return self._services_running
    @property

    def engine_name(self) -> str:
        """Get the engine name (read-only)."""
        return self._engine_name
    @property

    def is_http_based(self) -> bool:
        """Check if current engine uses HTTP."""
        # Use getattr to be safe if engine implementation is incomplete
        protocol = getattr(self._engine, 'protocol_type', None)
        if not protocol:
            return False
        # Check against basic HTTP type or specific variants
        # Assuming ProtocolType enum might have both simple and specific types
        # Safely check if it starts with HTTP or is the HTTP enum member
        # ProtocolType is an Enum, so check equality or containment
        # Check for generic HTTP if it exists in Enum (some versions might have it)
        if hasattr(ProtocolType, 'HTTP') and protocol == ProtocolType.HTTP:
            return True
        return protocol in [
            ProtocolType.HTTP_REST,
            ProtocolType.HTTP_GRAPHQL,
            ProtocolType.HTTP_RPC
        ]

    @staticmethod
    def _normalize_route_path(path: str) -> str:
        """Normalize route paths for pause-policy matching."""
        if not path:
            return "/"
        normalized = "/" + path.strip("/")
        return normalized if normalized != "" else "/"

    @staticmethod
    def _normalize_method(method: str) -> str:
        """Normalize HTTP method names."""
        normalized = (method or "GET").upper()
        # HEAD requests are semantically tied to GET for pause policy.
        if normalized == "HEAD":
            return "GET"
        return normalized

    def should_block_request(self, method: str, path: str) -> bool:
        """Return whether a request should be blocked by pause policy."""
        normalized_path = self._normalize_route_path(path)
        if normalized_path in self._pause_allow_paths:
            return False
        if self._global_paused:
            return True
        key = (self._normalize_method(method), normalized_path)
        return key in self._paused_routes

    def pause_endpoint(self, path: str, method: str = "GET") -> tuple[str, str]:
        """Pause an endpoint route and return its normalized key."""
        key = (self._normalize_method(method), self._normalize_route_path(path))
        self._paused_routes.add(key)
        return key

    def resume_endpoint(self, path: str, method: str = "GET") -> tuple[str, str]:
        """Resume an endpoint route and return its normalized key."""
        key = (self._normalize_method(method), self._normalize_route_path(path))
        self._paused_routes.discard(key)
        return key

    def set_global_pause(self, paused: bool) -> None:
        """Enable or disable global request pause."""
        self._global_paused = paused

    def get_pause_state(self) -> dict[str, Any]:
        """Return current pause policy state."""
        return {
            "global_paused": self._global_paused,
            "paused_routes": sorted([{"method": method, "path": path} for method, path in self._paused_routes], key=lambda item: (item["path"], item["method"])),
        }

    def pause_all_requests(self) -> None:
        """Pause all non-allowlisted HTTP requests."""
        self.set_global_pause(True)

    def resume_all_requests(self) -> None:
        """Resume all globally paused HTTP requests."""
        self.set_global_pause(False)

    def _build_status_snapshot(self) -> dict[str, Any]:
        """Build a canonical status payload for Python and HTTP surfaces."""
        return {
            "status": "running" if self._is_running else "stopped",
            "is_running": self._is_running,
            "host": self._host or "0.0.0.0",
            "port": self._port or 8000,
            "engine": self._engine_name,
            "actions_count": len(self._actions),
            "services_running": self._services_running,
            "pause": self.get_pause_state(),
            "pipeline": self._pipeline.status(),
        }

    def status(self) -> dict[str, Any]:
        """Return rich runtime status for production operations."""
        return self._build_status_snapshot()

    def health(self) -> dict[str, Any]:
        """Return health snapshot with pause and service context."""
        from datetime import datetime

        return {
            "status": "healthy" if self._is_running else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "is_running": self._is_running,
            "services_running": self._services_running,
            "pause": {"global_paused": self._global_paused},
            "pipeline": self._pipeline.status(),
            "engine": self._engine_name,
            "server_id": self._server_id,
        }

    @staticmethod
    def _invoke_action_callable(action: Any, args: list[Any] | None = None, kwargs: dict[str, Any] | None = None) -> Any:
        """Invoke sync/async action callables from pipeline jobs."""
        call_args = list(args or [])
        call_kwargs = dict(kwargs or {})
        result = action(*call_args, **call_kwargs)
        if inspect.isawaitable(result):
            return asyncio.run(result)
        return result

    def register_pipeline_handler(self, job_type: str, handler: Any) -> None:
        """Register custom pipeline job handler."""
        self._pipeline.register_handler(job_type, handler)

    def enqueue_pipeline_job(
        self,
        job_type: str,
        payload: dict[str, Any],
        *,
        run_after: Any | None = None,
        max_attempts: int = 5,
    ) -> str:
        """Enqueue a job into the outbox layer."""
        return self._pipeline.enqueue(
            job_type=job_type,
            payload=payload,
            run_after=run_after,
            max_attempts=max_attempts,
        )

    def enqueue_action_job(
        self,
        action_name: str,
        *,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
        max_attempts: int = 5,
    ) -> str:
        """Enqueue execution of a registered action via the background worker."""
        if action_name not in self._registered_action_handlers:
            raise ValidationError(
                message=f"Unknown action for pipeline: {action_name}",
                details={"action_name": action_name},
            )
        payload = {
            "args": list(args or []),
            "kwargs": dict(kwargs or {}),
        }
        return self.enqueue_pipeline_job(action_name, payload, max_attempts=max_attempts)

    def start_pipeline_worker(self) -> None:
        """Start singleton background worker."""
        try:
            self._pipeline.start()
        except RuntimeError as exc:
            raise ServerLifecycleError(
                message="Failed to start pipeline worker singleton",
                details={"owner": self._server_id, "error": str(exc)},
            ) from exc

    def stop_pipeline_worker(self) -> None:
        """Stop background worker."""
        self._pipeline.stop()

    async def create_api_token(
        self,
        *,
        subject_id: str,
        name: str,
        scopes: list[str],
        expires_in_seconds: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self._token_manager.create_token(
            subject_id=subject_id,
            name=name,
            scopes=scopes,
            expires_in_seconds=expires_in_seconds,
            metadata=metadata,
        )

    async def revoke_api_token(self, token_id: str) -> bool:
        return await self._token_manager.revoke_token(token_id)

    async def list_api_tokens(self, subject_id: str | None = None) -> list[dict[str, Any]]:
        return await self._token_manager.list_tokens(subject_id=subject_id)

    async def record_api_token_usage(
        self,
        *,
        token_id: str,
        amount: float,
        operation: str,
        metadata: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        return await self._token_manager.record_usage(
            token_id=token_id,
            amount=amount,
            operation=operation,
            metadata=metadata,
            idempotency_key=idempotency_key,
        )

    async def recharge_subject(
        self,
        *,
        subject_id: str,
        amount: float,
        currency: str = "USD",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self._token_manager.recharge(
            subject_id=subject_id,
            amount=amount,
            currency=currency,
            metadata=metadata,
        )

    async def get_subject_balance(self, subject_id: str) -> float:
        return await self._token_manager.get_balance(subject_id)

    @staticmethod
    def _normalize_scope_set(value: Any) -> set[str]:
        if isinstance(value, str):
            candidate = value.strip()
            return {candidate} if candidate else set()
        if isinstance(value, (list, tuple, set)):
            return {str(item).strip() for item in value if str(item).strip()}
        return set()

    def _extract_required_scopes_from_action(self, action: Any) -> set[str]:
        scopes: set[str] = set()
        security_config = getattr(action, "security_config", None)
        if isinstance(security_config, dict):
            for _, configured_scopes in security_config.items():
                scopes.update(self._normalize_scope_set(configured_scopes))
            return scopes
        scopes.update(self._normalize_scope_set(security_config))
        return scopes

    def _register_api_token_scope_rule(
        self,
        *,
        method: str,
        path: str,
        required_scopes: set[str],
    ) -> None:
        normalized_method = str(method or "GET").upper()
        normalized_path = str(path or "/").strip() or "/"
        existing = next(
            (
                rule
                for rule in self._api_token_scope_rules
                if rule.get("method") == normalized_method and rule.get("path") == normalized_path
            ),
            None,
        )
        if existing is not None:
            existing["scopes"] = set(required_scopes)
            return
        self._api_token_scope_rules.append(
            {
                "method": normalized_method,
                "path": normalized_path,
                "scopes": set(required_scopes),
            }
        )

    @staticmethod
    async def _parse_request_json_payload(request: Any) -> dict[str, Any]:
        """Parse request payload into a JSON object using shared xwsystem serializer fallback."""
        if isinstance(request, dict):
            return request
        if request is None:
            return {}
        if hasattr(request, "json"):
            try:
                parsed = await request.json()
                if isinstance(parsed, dict):
                    return parsed
                raise ValueError("JSON payload must be an object")
            except ValueError:
                raise
            except Exception:
                pass
        if hasattr(request, "body"):
            raw = await request.body()
            if not raw:
                return {}
            parsed = JsonSerializer().loads(raw.decode("utf-8"))
            if isinstance(parsed, dict):
                return parsed
            raise ValueError("JSON payload must be an object")
        return {}

    def register_action(
        self,
        action: Any,
        path: str | None = None,
        method: str = "POST",
        route_info: dict[str, Any] | None = None,
        required_scopes: list[str] | None = None,
    ) -> bool:
        """
        Register XWAction as API endpoint/route.
        Uses the engine's register_action method, which internally
        uses XWAction's engine system for execution.
        This method implements the registration pipeline:
        1. pre_register_action() hook - transform action before registration
        2. Register action with engine (protocol-specific)
        3. post_register_action() hook - perform post-registration tasks
        Args:
            action: XWAction instance or decorated function
            path: Optional endpoint path (defaults to action.api_name)
                Used for HTTP engines. For other protocols, use route_info.
            method: HTTP method ('GET', 'POST', 'PUT', 'DELETE', etc.)
                Used for HTTP engines. For other protocols, use route_info.
            route_info: Optional protocol-specific route information
                - HTTP: {'path': '/users', 'method': 'GET'}
                - gRPC: {'service': 'UserService', 'method': 'GetUser'}
                - WebSocket: {'path': '/ws/chat'}
                - Message Queue: {'topic': 'user.events'}
                If None, constructs from path/method (HTTP default)
        Returns:
            True if registration successful
        Example:
            >>> # HTTP engine
            >>> server.register_action(get_user, path="/users/{user_id}", method="GET")
            >>> 
            >>> # gRPC engine
            >>> server.register_action(get_user, route_info={'service': 'UserService', 'method': 'GetUser'})
        """
        # Validate action parameter
        if action is None:
            raise TypeError("Action cannot be None for registration.")
        # Validate method parameter
        if method is None:
            raise TypeError("Method cannot be None for action registration.")
        # Call pre_register_action hook to transform action
        action = self.pre_register_action(action)
        # For bound methods (from get_actions()), pass the bound method directly
        # The engine will detect it's a bound method and handle it correctly
        # For standalone functions or XWAction instances, extract xwaction if needed
        action_to_register = action
        if hasattr(action, 'xwaction') and not inspect.ismethod(action):
            # Only extract xwaction if action is NOT a bound method
            # Bound methods should be passed directly to preserve self context
            action_to_register = action.xwaction
        # Build route_info (protocol-specific)
        if route_info is None:
            # Default: HTTP-style route info
            if path is None:
                api_name = getattr(action_to_register, 'api_name', None) or getattr(action, '__name__', 'unknown')
                path = f"/{api_name}"
            route_info = {'path': path, 'method': method}
        else:
            # Use provided route_info, but merge path/method if provided
            if path:
                route_info['path'] = path
            if method:
                route_info['method'] = method
        # Register using engine strategy
        try:
            success = self._engine.register_action(
                self._app,
                action_to_register,
                route_info
            )
            if success:
                self._actions.append(action_to_register)
                logger.info(f"Registered action at {method} {path}")
                route_method = str(route_info.get("method") if isinstance(route_info, dict) else method or "GET").upper()
                route_path = str(route_info.get("path") if isinstance(route_info, dict) else path or "/")
                resolved_scopes = (
                    self._normalize_scope_set(required_scopes)
                    or self._extract_required_scopes_from_action(action_to_register)
                    or set(self._api_token_default_required_scopes)
                )
                self._register_api_token_scope_rule(
                    method=route_method,
                    path=route_path,
                    required_scopes=resolved_scopes,
                )
                # Register action handler for outbox/background execution by api name.
                action_name = getattr(action_to_register, 'api_name', None) or getattr(action, '__name__', 'unknown')
                if callable(action):
                    self._registered_action_handlers[action_name] = action
                    self._pipeline.register_handler(
                        action_name,
                        lambda payload, _action=action: self._invoke_action_callable(
                            _action,
                            args=payload.get("args", []),
                            kwargs=payload.get("kwargs", {}),
                        ),
                    )
                # Collect schemas from the action (smart schema collection)
                self._collect_action_schemas(action_to_register)
                # Call post_register_action hook
                route_info_with_meta = {
                    **route_info,
                    "action": action_to_register,
                    "api_name": action_name,
                }
                self.post_register_action(action_to_register, route_info_with_meta)
            else:
                logger.warning(f"Failed to register action at {method} {path}")
            return success
        except Exception as e:
            logger.error(f"Error registering action: {e}")
            return False

    def register_actions(
        self,
        actions: list[Any],
        path_prefix: str = ""
    ) -> int:
        """
        Register multiple actions at once.
        Args:
            actions: List of XWAction instances or decorated functions
            path_prefix: Optional prefix for all paths
        Returns:
            Number of successfully registered actions
        Example:
            >>> actions = [get_user, create_user, update_user]
            >>> server.register_actions(actions, path_prefix="/api/v1")
        """
        registered = 0
        for action in actions:
            # Try to determine method from action profile
            method = "POST"
            if hasattr(action, 'xwaction'):
                profile = getattr(action.xwaction, 'profile', None)
                if hasattr(profile, 'value') and profile.value == "query":
                    method = "GET"
            # Determine path
            path = None
            if path_prefix:
                api_name = getattr(action, 'api_name', None) or getattr(action, '__name__', 'unknown')
                if hasattr(action, 'xwaction'):
                    api_name = getattr(action.xwaction, 'api_name', None) or api_name
                path = f"{path_prefix}/{api_name}"
            if self.register_action(action, path=path, method=method):
                registered += 1
        return registered

    def generate_openapi(self) -> dict:
        """
        Generate OpenAPI specification for registered actions.
        Returns:
            OpenAPI 3.1 specification dictionary
        """
        return self._engine.generate_openapi(
            self._app,
            self._actions,
            self.config
        )

    def _kill_process_on_port(self, port: int) -> bool:
        """
        Kill any process using the specified port using cross-platform safe subprocess.
        Args:
            port: Port number to check
        Returns:
            True if a process was killed, False otherwise
        """
        import time
        system = platform.system().lower()
        try:
            # Check if port is open
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('127.0.0.1', port)) != 0:
                    return False # Port not in use
            pid = None
            if system == "windows":
                # Windows: Get PID safely
                # Avoid shell=True for security
                cmd = ["netstat", "-ano"]
                output = subprocess.check_output(cmd, text=True)
                for line in output.splitlines():
                    # Look for lines like: TCP    0.0.0.0:8000    0.0.0.0:0    LISTENING    12345
                    if f":{port}" in line and "LISTENING" in line:
                        pid = line.strip().split()[-1]
                        break
                if pid:
                    # Kill force
                    subprocess.run(["taskkill", "/F", "/PID", pid], check=True, capture_output=True)
            else:
                # Linux/MacOS: Use lsof safely
                # -t: terse (pid only), -i: internet stuff
                try:
                    pids_str = subprocess.check_output(["lsof", "-t", "-i", f":{port}"], text=True).strip()
                    if pids_str:
                        pids = pids_str.split('\n')
                        killed = False
                        for pid in pids:
                            pid = pid.strip()
                            if pid:
                                # SIGKILL
                                subprocess.run(["kill", "-9", pid], check=True, capture_output=True)
                                killed = True
                        if killed:
                            logger.info(f"Killed process(es) {', '.join(pids)} using port {port}")
                            time.sleep(1) # Give OS time to release resource
                            return True
                except subprocess.CalledProcessError:
                    return False
            if pid:
                logger.info(f"Killed process {pid} using port {port}")
                time.sleep(1) # Give OS time to release resource
                return True
        except Exception as e:
            logger.warning(f"Failed to kill process on port {port}: {e}")
        return False

    def start(self, host: str = "0.0.0.0", port: int = 8000, force_kill_port: bool = True, takeover: bool = False, **kwargs) -> None:
        """
        Start the HTTP server.
        This method starts only the HTTP server. To start domain services,
        call start_services() separately. This separation allows HTTP server
        to be available while services can be started/stopped independently.
        Args:
            host: Host to bind to
            port: Port to bind to
            force_kill_port: If True, kill any process using the port before starting
            takeover: If True, take over lockfile from existing process
            **kwargs: Additional server-specific options
        Example:
            >>> server.start(host="0.0.0.0", port=8000, reload=True)
            >>> server.start_services()  # Start domain services separately
        """
        if self._is_running:
            logger.warning(f"HTTP server is already running on {self._host}:{self._port}")
            return
        # Acquire lockfile (process-level singleton enforcement)
        if self._lockfile_manager:
            if not self._lockfile_manager.acquire(takeover=takeover):
                raise XWAPIError(
                    f"Another server instance is running (server_id: {self._server_id}). "
                    f"Use takeover=True to take over."
                )
        self._host = host
        self._port = port
        # 1. Kill port if needed
        # We only force kill if the engine is network-based (usually HTTP)
        # But generally if a port is specified, we assume it's network-based
        if force_kill_port:
             self._kill_process_on_port(port)
        # 2. Set State BEFORE blocking call
        self._is_running = True
        from datetime import datetime
        self._start_time = datetime.now()
        # 3. Pre-start hooks
        if self.is_http_based:
            self.pre_http_start()
        else:
            self.pre_server_start()
        # 4. Post-start hooks (Called before blocking loop, as server is about to take control)
        # This effectively means "server is configured and ready to run"
        if self.is_http_based:
            self.post_http_start()
        else:
            self.post_server_start()
        # 5. Start Server (Blocking)
        try:
            logger.info(f"Starting {self._engine.name} server on {host}:{port}")
            # This will block until CTRL+C or kill signal
            # For non-HTTP engines that don't take host/port, we rely on kwargs or config
            if self.is_http_based:
                self._engine.start_server(self._app, host=host, port=port, **kwargs)
            else:
                 # Generic start
                 self._engine.start_server(self._app, **kwargs)
        except Exception as e:
            self._is_running = False
            logger.error(f"Server crashed: {e}")
            raise
        finally:
            # 5. Cleanup when server stops
            self._is_running = False
            # Call post-start hooks (logic for post_server_start call)
            # Since we are in finally, the server HAS started and stopped (or failed).
            # But post_server_start is usually "after server is UP".
            # If server blocked, we are now DOWN.
            # So calling post_server_start here is technically too late for "running" logic,
            # but correct for "server process lifecycle finished" logic if that's the intent.
            # However, typically post_start is for "server is now ready".
            # Since start_server is blocking, we can't call post_start while it runs unless we thread it.
            # But the blocking model assumes we don't return control.
            # So post_server_start hooks in this architecture only run after server stops?
            # That seems wrong. But consistent with blocking servers.
            # Unless we run hooks inside the engine?
            # For now, let's keep the hook calls but fix duplication.
            # Note: post_stop is the one that matters here.
            self.post_stop() # Ensure stop hooks run even if it crashes

    def start_services(self) -> None:
        """
        Start domain services.
        This method starts domain services (agents, background tasks, etc.)
        separately from the HTTP server. This allows HTTP server to be available
        while services can be started/stopped independently.
        Example:
            >>> server.start(host="0.0.0.0", port=8000)  # Start HTTP server
            >>> server.start_services()  # Start domain services
        """
        if self._services_running:
            logger.warning("Services are already running")
            return
        # Call pre_services_start hook
        self.pre_services_start()
        logger.info("Starting domain services...")
        self.start_pipeline_worker()
        self._services_running = True
        # Call post_services_start hook
        self.post_services_start()
        logger.info("Domain services started successfully")

    def stop(self, dispose: bool = False) -> None:
        """
        Stop the HTTP server and domain services.
        This method stops both domain services and the HTTP server.
        It calls lifecycle hooks and flushes all registered flushable handlers.
        Args:
            dispose: If True, unregister instance from governance registry.
                Keep False for normal stop/restart lifecycle.
        Note: Behavior depends on the engine. For development servers
        (uvicorn), this may not be applicable as they run in the main thread.
        """
        # Call pre_stop hook
        self.pre_stop()
        # Stop domain services first
        if self._services_running:
            logger.info("Stopping domain services...")
            self.stop_pipeline_worker()
            self._services_running = False
        # Stop HTTP server
        if not self._is_running:
            logger.warning("HTTP server is not running")
        else:
            logger.info("Stopping HTTP server...")
            self._engine.stop_server(self._app)
            # State update happens in finally block of start(), but we can set it here too
            self._is_running = False
            self._host = None
            self._port = None
            self._start_time = None
        # Release lockfile to allow clean restart in same process.
        if self._lockfile_manager:
            self._lockfile_manager.release()
        if dispose:
            # Unregister only for final disposal, not normal stop/restart cycle.
            from exonware.xwapi.server.governance import get_registry
            registry = get_registry()
            registry.unregister(self._server_id, self)
        # Flush all registered flushable handlers
        if self._flushable_handlers:
            logger.info(f"Flushing {len(self._flushable_handlers)} handlers...")
            for handler in self._flushable_handlers:
                try:
                    if hasattr(handler, 'flush'):
                        handler.flush()
                    if hasattr(handler, 'close'):
                        handler.close()
                except Exception as e:
                    logger.warning(f"Error flushing handler {type(handler).__name__}: {e}")
        # post_stop hook is now also called in start()'s finally block, 
        # but calling it here explicitly for manual stops is fine as long as hooks are idempotent
        self.post_stop()
        logger.info("Server stopped successfully")

    def stop_services(self) -> None:
        """
        Stop domain services without stopping HTTP server.
        This allows HTTP server to remain available while services are stopped.
        Example:
            >>> server.stop_services()  # Stop services but keep HTTP server running
        """
        if not self._services_running:
            logger.warning("Services are not running")
            return
        logger.info("Stopping domain services...")
        self.stop_pipeline_worker()
        self._services_running = False
        logger.info("Domain services stopped successfully")

    def restart(self) -> None:
        """Restart the API server."""
        logger.info("Restarting server...")
        host = self._host or "0.0.0.0"
        port = self._port or 8000
        self.stop(dispose=False)
        self.start(host=host, port=port)
        logger.info("Server restarted successfully")

    def run(self, host: str | None = None, port: int | None = None, **kwargs) -> None:
        """
        Run the server (alias for start).
        Starts the server and blocks until stopped.
        Args:
            host: Host to bind to (default: from XWAUTH_API_HOST env or "127.0.0.1")
            port: Port to bind to (default: from XWAUTH_API_PORT env or 8000)
            **kwargs: Additional arguments passed to start()
        """
        import os
        if host is None:
            host = os.environ.get("XWAUTH_API_HOST", "127.0.0.1")
        if port is None:
            port = int(os.environ.get("XWAUTH_API_PORT", "8000"))
        self.start(host=host, port=port, **kwargs)

    def register_services(
        self,
        services: Any,
        auth: Any | None = None,
        issuer: str | None = None
    ) -> None:
        """
        Register services from a services module/provider.
        This method automatically registers all services from the provided services
        object, which should have an AUTH_SERVICES attribute containing a list of
        (path, method, handler) tuples.
        Args:
            services: Services module or object with AUTH_SERVICES attribute
            auth: Optional auth instance (for xwauth services)
            issuer: Optional issuer URL for discovery endpoints
        """
        if not self.is_http_based:
            logger.warning("register_services only supported for HTTP engines")
            return
        # Try to get AUTH_SERVICES from services object
        if hasattr(services, 'AUTH_SERVICES'):
            auth_services = services.AUTH_SERVICES
        elif hasattr(services, '__getattr__'):
            auth_services = getattr(services, 'AUTH_SERVICES', [])
        else:
            raise ValueError("services object must have AUTH_SERVICES attribute")
        # Library-first integration: service handlers are registered directly.
        logger.info(f"Registering {len(auth_services)} services manually")
        for path, method, handler in auth_services:
            self.register_action(handler, path=path, method=method)
        logger.info(f"Registered {len(auth_services)} services")

    def _collect_action_schemas(self, action: Any) -> None:
        """
        Collect input and output schemas from an action.
        Smart schema collection: extracts schemas from XWAction's in_types and out_types,
        converts them to OpenAPI JSON schema format, and stores them for OpenAPI documentation.
        Args:
            action: XWAction instance or function with xwaction attribute
        """
        try:
            # Get action instance (could be function with xwaction attribute or XWAction instance)
            action_obj = getattr(action, 'xwaction', action) if hasattr(action, 'xwaction') else action
            if not action_obj:
                return
            api_name = getattr(action_obj, 'api_name', 'unknown')
            # Collect input schemas (in_types)
            if hasattr(action_obj, 'in_types') and action_obj.in_types:
                for param_name, schema in action_obj.in_types.items():
                    # Generate unique schema name
                    schema_name = f"{api_name}_{param_name}_Input"
                    # Normalize schema name (remove special chars, ensure uniqueness)
                    schema_name = schema_name.replace('/', '_').replace('-', '_')
                    if schema_name not in self._collected_schemas:
                        try:
                            # Convert XWSchema to OpenAPI JSON schema
                            if hasattr(schema, 'to_native'):
                                openapi_schema_dict = schema.to_native()
                            elif hasattr(schema, 'to_dict'):
                                openapi_schema_dict = schema.to_dict()
                            elif hasattr(schema, 'to_json_schema'):
                                openapi_schema_dict = schema.to_json_schema()
                            elif isinstance(schema, dict):
                                openapi_schema_dict = schema
                            else:
                                # Fallback: try to get schema dict directly
                                openapi_schema_dict = dict(schema) if hasattr(schema, '__dict__') else {"type": "object", "title": schema_name}
                            # Ensure it's a valid OpenAPI schema
                            if not isinstance(openapi_schema_dict, dict):
                                openapi_schema_dict = {"type": "object", "title": schema_name}
                            self._collected_schemas[schema_name] = openapi_schema_dict
                        except Exception as e:
                            logger.debug(f"Failed to convert input schema for {schema_name}: {e}")
                            # Fallback to generic object schema
                            self._collected_schemas[schema_name] = {"type": "object", "title": schema_name}
            # Collect output schemas (out_types)
            if hasattr(action_obj, 'out_types') and action_obj.out_types:
                for output_name, schema in action_obj.out_types.items():
                    # Generate unique schema name
                    schema_name = f"{api_name}_{output_name}_Output"
                    # Normalize schema name
                    schema_name = schema_name.replace('/', '_').replace('-', '_')
                    if schema_name not in self._collected_schemas:
                        try:
                            # Convert XWSchema to OpenAPI JSON schema
                            if hasattr(schema, 'to_native'):
                                openapi_schema_dict = schema.to_native()
                            elif hasattr(schema, 'to_dict'):
                                openapi_schema_dict = schema.to_dict()
                            elif hasattr(schema, 'to_json_schema'):
                                openapi_schema_dict = schema.to_json_schema()
                            elif isinstance(schema, dict):
                                openapi_schema_dict = schema
                            else:
                                # Fallback: try to get schema dict directly
                                openapi_schema_dict = dict(schema) if hasattr(schema, '__dict__') else {"type": "object", "title": schema_name}
                            # Ensure it's a valid OpenAPI schema
                            if not isinstance(openapi_schema_dict, dict):
                                openapi_schema_dict = {"type": "object", "title": schema_name}
                            self._collected_schemas[schema_name] = openapi_schema_dict
                        except Exception as e:
                            logger.debug(f"Failed to convert output schema for {schema_name}: {e}")
                            # Fallback to generic object schema
                            self._collected_schemas[schema_name] = {"type": "object", "title": schema_name}
        except Exception as e:
            logger.debug(f"Failed to collect schemas from action: {e}")

    def get_collected_schemas(self) -> dict[str, dict[str, Any]]:
        """
        Get all collected schemas for OpenAPI documentation.
        Returns:
            Dictionary mapping schema names to OpenAPI schema definitions
        """
        return self._collected_schemas.copy()

    def get_openapi_tag_descriptions(self) -> dict[str, str]:
        """
        Get OpenAPI tag descriptions for this server.
        Override this method in subclasses to provide server-specific tag descriptions.
        Returns empty dict by default (engine-agnostic).
        Can also be provided via config.openapi_tags - this method is a fallback
        for programmatic access.
        Returns:
            Dictionary mapping tag names to descriptions
        """
        # Extract from config if available
        if self.config and self.config.openapi_tags:
            return {
                tag.get("name"): tag.get("description", f"{tag.get('name')} endpoints")
                for tag in self.config.openapi_tags
                if isinstance(tag, dict) and tag.get("name")
            }
        return {}

    def register_admin_endpoints(self, enabled: bool = True, prefix: str = "/server", tag: str = "Server") -> None:
        """
        Register built-in admin endpoints (start, stop, restart, pause, resume, status).
        Only works for engines that support admin endpoints (typically HTTP engines).
        Args:
            enabled: Whether to enable admin endpoints (default: True)
            prefix: URL prefix for admin endpoints (default: "/server")
            tag: OpenAPI tag name (default: "Server")
        """
        self._admin_enabled = enabled
        self._admin_prefix = prefix
        self._admin_tag = tag
        self._admin_auth_prefixes.add(prefix)
        # Ensure admin paths remain available during pause mode.
        self._pause_allow_paths.update({
            "/health",
            f"{prefix}/status",
            f"{prefix}/health",
            f"{prefix}/pipeline",
            f"{prefix}/tokens/list",
            f"{prefix}/tokens/usage",
            f"{prefix}/tokens/balance",
            f"{prefix}/log",
            f"{prefix}/pause",
            f"{prefix}/resume",
            f"{prefix}/start",
            f"{prefix}/stop",
            f"{prefix}/restart",
        })
        if not enabled:
            logger.debug("Admin endpoints disabled")
            return
        # Check if engine supports admin endpoints
        if not getattr(self._engine, 'supports_admin_endpoints', False):
            logger.debug(f"Engine {self._engine_name} does not support admin endpoints")
            return
        # Only register for HTTP engines
        if not self.is_http_based:
            logger.debug(f"Admin endpoints only supported for HTTP engines, got: {self._engine_name}")
            return
        # Register management endpoints directly
        try:
            from exonware.xwaction import XWAction
            from exonware.xwaction.defs import ActionProfile
        except ImportError:
            logger.warning("XWAction not available, skipping management endpoints")
            return
        action_engine = self._engine_name
        # Store server reference in app state
        if not hasattr(self._app.state, 'xwserver'):
            self._app.state.xwserver = self
        @XWAction(
            operationId="server_status",
            summary="Server Status",
            method="GET",
            description="Get server status and information.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_status(request: Any = None) -> dict[str, Any]:
            """Get server status."""
            return self._build_status_snapshot()

        @XWAction(
            operationId="server_health",
            summary="Server Health",
            method="GET",
            description="Get server health details for liveness/readiness checks.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_health(request: Any = None) -> dict[str, Any]:
            """Return health details."""
            return self.health()

        @XWAction(
            operationId="server_pipeline",
            summary="Server Pipeline",
            method="GET",
            description="Get Outbox + Background Worker pipeline status.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_pipeline(request: Any = None) -> dict[str, Any]:
            """Return pipeline status details."""
            return self._pipeline.status()

        @XWAction(
            operationId="server_tokens_create",
            summary="Create API Token",
            method="POST",
            description="Create API token for a subject with scopes and expiration.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_tokens_create(
            subject_id: str | None = None,
            name: str | None = None,
            scopes: list[str] | None = None,
            expires_in_seconds: int | None = None,
            metadata: dict[str, Any] | None = None,
            request: Any = None,
        ) -> dict[str, Any]:
            payload: dict[str, Any] = {}
            if isinstance(request, dict):
                payload = request
            elif request is not None and hasattr(request, "json"):
                try:
                    payload = await request.json()
                except Exception:
                    payload = {}
            subject_id = str(subject_id or payload.get("subject_id") or "")
            name = str(name or payload.get("name") or "")
            scopes = scopes if isinstance(scopes, list) else payload.get("scopes") or []
            expires_in_seconds = expires_in_seconds if isinstance(expires_in_seconds, int) else payload.get("expires_in_seconds")
            metadata = metadata if isinstance(metadata, dict) else payload.get("metadata") or {}
            if not subject_id.strip() or not name.strip():
                raise ValueError("subject_id and name are required for token creation")
            created = await self.create_api_token(
                subject_id=subject_id,
                name=name,
                scopes=list(scopes) if isinstance(scopes, list) else [],
                expires_in_seconds=expires_in_seconds if isinstance(expires_in_seconds, int) else None,
                metadata=metadata if isinstance(metadata, dict) else {},
            )
            return {"status": "created", **created}

        @XWAction(
            operationId="server_tokens_list",
            summary="List API Tokens",
            method="GET",
            description="List API tokens for a subject.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_tokens_list(subject_id: str | None = None, request: Any = None) -> dict[str, Any]:
            resolved_subject_id = str(subject_id or "")
            if isinstance(request, dict):
                resolved_subject_id = resolved_subject_id or str(request.get("subject_id") or "")
            elif request is not None and hasattr(request, "query_params"):
                resolved_subject_id = resolved_subject_id or str(request.query_params.get("subject_id") or "")
            tokens = await self.list_api_tokens(subject_id=resolved_subject_id or None)
            return {"status": "ok", "subject_id": resolved_subject_id or None, "tokens": tokens}

        @XWAction(
            operationId="server_tokens_revoke",
            summary="Revoke API Token",
            method="POST",
            description="Revoke an API token by token_id.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_tokens_revoke(token_id: str | None = None, request: Any = None) -> dict[str, Any]:
            payload: dict[str, Any] = {}
            if isinstance(request, dict):
                payload = request
            elif request is not None and hasattr(request, "json"):
                try:
                    payload = await request.json()
                except Exception:
                    payload = {}
            resolved_token_id = str(token_id or payload.get("token_id") or "")
            if not resolved_token_id:
                raise ValueError("token_id is required")
            revoked = await self.revoke_api_token(resolved_token_id)
            return {"status": "revoked" if revoked else "not_found", "token_id": resolved_token_id}

        @XWAction(
            operationId="server_tokens_usage_record",
            summary="Record Token Usage",
            method="POST",
            description="Record usage event and consume subject credits.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_tokens_usage_record(
            token_id: str | None = None,
            amount: float | None = None,
            operation: str | None = None,
            metadata: dict[str, Any] | None = None,
            request: Any = None,
        ) -> dict[str, Any]:
            payload: dict[str, Any] = {}
            if isinstance(request, dict):
                payload = request
            elif request is not None and hasattr(request, "json"):
                try:
                    payload = await request.json()
                except Exception:
                    payload = {}
            resolved_token_id = str(token_id or payload.get("token_id") or "")
            resolved_amount = float(amount if amount is not None else payload.get("amount") or 0.0)
            resolved_operation = str(operation or payload.get("operation") or "request")
            resolved_metadata = metadata if isinstance(metadata, dict) else payload.get("metadata") or {}
            if not resolved_token_id or resolved_amount <= 0:
                raise ValueError("token_id and positive amount are required")
            event = await self.record_api_token_usage(
                token_id=resolved_token_id,
                amount=resolved_amount,
                operation=resolved_operation,
                metadata=resolved_metadata if isinstance(resolved_metadata, dict) else {},
            )
            return {"status": "recorded", "usage": event}

        @XWAction(
            operationId="server_tokens_usage_list",
            summary="Get Token Usage",
            method="GET",
            description="Get usage history for token_id.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_tokens_usage_list(token_id: str | None = None, request: Any = None) -> dict[str, Any]:
            resolved_token_id = str(token_id or "")
            if isinstance(request, dict):
                resolved_token_id = resolved_token_id or str(request.get("token_id") or "")
            elif request is not None and hasattr(request, "query_params"):
                resolved_token_id = resolved_token_id or str(request.query_params.get("token_id") or "")
            if not resolved_token_id:
                raise ValueError("token_id is required")
            usage = await self._token_manager.get_usage(resolved_token_id)
            return {"status": "ok", "token_id": resolved_token_id, "usage": usage}

        @XWAction(
            operationId="server_tokens_recharge",
            summary="Recharge Subject Credits",
            method="POST",
            description="Recharge subject credits through payment provider.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_tokens_recharge(
            subject_id: str | None = None,
            amount: float | None = None,
            currency: str | None = None,
            metadata: dict[str, Any] | None = None,
            request: Any = None,
        ) -> dict[str, Any]:
            payload: dict[str, Any] = {}
            if isinstance(request, dict):
                payload = request
            elif request is not None and hasattr(request, "json"):
                try:
                    payload = await request.json()
                except Exception:
                    payload = {}
            resolved_subject_id = str(subject_id or payload.get("subject_id") or "")
            resolved_amount = float(amount if amount is not None else payload.get("amount") or 0.0)
            resolved_currency = str(currency or payload.get("currency") or "USD")
            resolved_metadata = metadata if isinstance(metadata, dict) else payload.get("metadata") or {}
            if not resolved_subject_id or resolved_amount <= 0:
                raise ValueError("subject_id and positive amount are required")
            event = await self.recharge_subject(
                subject_id=resolved_subject_id,
                amount=resolved_amount,
                currency=resolved_currency,
                metadata=resolved_metadata if isinstance(resolved_metadata, dict) else {},
            )
            return {"status": "recharged", "event": event}

        @XWAction(
            operationId="server_tokens_balance",
            summary="Get Subject Balance",
            method="GET",
            description="Get current subject credit balance.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_tokens_balance(subject_id: str | None = None, request: Any = None) -> dict[str, Any]:
            resolved_subject_id = str(subject_id or "")
            if isinstance(request, dict):
                resolved_subject_id = resolved_subject_id or str(request.get("subject_id") or "")
            elif request is not None and hasattr(request, "query_params"):
                resolved_subject_id = resolved_subject_id or str(request.query_params.get("subject_id") or "")
            if not resolved_subject_id:
                raise ValueError("subject_id is required")
            balance = await self.get_subject_balance(resolved_subject_id)
            return {"status": "ok", "subject_id": resolved_subject_id, "balance": balance}

        @XWAction(
            operationId="server_health_root",
            summary="Health Check",
            method="GET",
            description="Root health endpoint kept available during pause mode.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def health_root(request: Any = None) -> dict[str, Any]:
            """Return root health details."""
            return self.health()
        @XWAction(
            operationId="server_start",
            summary="Start Server",
            method="POST",
            description="Start the API server (if not already running).",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_start(request: Any = None) -> dict[str, Any]:
            """Start the server."""
            if self._is_running:
                return {
                    "status": "already_running",
                    "message": f"Server is already running on {self._host}:{self._port}",
                    "host": self._host,
                    "port": self._port
                }
            return {
                "status": "info",
                "message": "Use server.start() or server.run() to start the server. Management endpoints provide status only.",
                "note": "Server must be started externally via .start() or .run() method"
            }
        @XWAction(
            operationId="server_stop",
            summary="Stop Server",
            method="POST",
            description="Stop the API server.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_stop(request: Any = None) -> dict[str, Any]:
            """Stop the server."""
            if not self._is_running:
                return {"status": "already_stopped", "message": "Server is already stopped"}
            try:
                logger.warning(
                    "Admin stop requested",
                    extra={"server_id": self._server_id, "engine": self._engine_name},
                )
                self.stop()
                return {"status": "stopped", "message": "Server stop signal sent"}
            except Exception as e:
                raise ServerLifecycleError(
                    message="Failed to stop server",
                    details={"server_id": self._server_id, "error": str(e)},
                ) from e
        @XWAction(
            operationId="server_restart",
            summary="Restart Server",
            method="POST",
            description="Restart the API server.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_restart(request: Any = None) -> dict[str, Any]:
            """Restart the server."""
            try:
                if self._is_running:
                    logger.warning(
                        "Admin restart requested",
                        extra={"server_id": self._server_id, "engine": self._engine_name},
                    )
                    self.stop()
                # Note: start() is blocking, so restart via API requires external process management
                return {
                    "status": "info",
                    "message": "Server restart requires external process management. Stop the server process and start it again.",
                    "note": "For programmatic restart, use server.stop() then server.start() in a separate thread/process"
                }
            except Exception as e:
                raise ServerLifecycleError(
                    message="Failed to process restart request",
                    details={"server_id": self._server_id, "error": str(e)},
                ) from e

        @XWAction(
            operationId="server_log",
            summary="Server Log",
            method="POST",
            description="Write a log entry through server logger.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_log(request: Any = None) -> dict[str, Any]:
            """Write a log entry with optional level/message payload."""
            payload: dict[str, Any] = {}
            if isinstance(request, dict):
                payload = request
            elif request is not None and hasattr(request, "json"):
                try:
                    payload = await request.json()
                except Exception:
                    payload = {}

            level = str(payload.get("level", "INFO")).upper()
            message = str(payload.get("message", ""))
            self.log(level=level, message=message)
            return {"status": "logged", "level": level, "message": message}
        @XWAction(
            operationId="server_pause",
            summary="Pause Endpoint/Service",
            method="POST",
            description="Pause a specific endpoint or service.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_pause(request: Any = None) -> dict[str, Any]:
            """Pause an endpoint or service."""
            payload: dict[str, Any] = {}
            if isinstance(request, dict):
                payload = request
            elif request is not None and all(hasattr(request, attr) for attr in ("endpoint", "service", "method")):
                payload = {
                    "endpoint": getattr(request, "endpoint", None),
                    "service": getattr(request, "service", None),
                    "method": getattr(request, "method", "GET"),
                }
            elif request is not None:
                try:
                    payload = await self._parse_request_json_payload(request)
                except Exception as exc:
                    raise ValidationError(
                        message="Invalid JSON payload for pause request",
                        details={"server_id": self._server_id},
                    ) from exc
            service_name = payload.get("service")
            endpoint_path = payload.get("endpoint")
            endpoint_method = payload.get("method", "GET")
            if service_name:
                logger.warning(
                    "Pausing service",
                    extra={"server_id": self._server_id, "service": service_name},
                )
                self.stop_services()
                return {"status": "paused", "message": "Service paused", "service": service_name}
            if endpoint_path:
                paused = self.pause_endpoint(endpoint_path, endpoint_method)
                logger.warning(
                    "Pausing endpoint",
                    extra={"server_id": self._server_id, "path": paused[1], "method": paused[0]},
                )
                return {
                    "status": "paused",
                    "message": "Endpoint paused",
                    "endpoint": paused[1],
                    "method": paused[0],
                    "pause": self.get_pause_state(),
                }
            self.set_global_pause(True)
            logger.warning("Global pause enabled", extra={"server_id": self._server_id})
            return {"status": "paused", "message": "Global pause enabled", "pause": self.get_pause_state()}
        @XWAction(
            operationId="server_resume",
            summary="Resume Endpoint/Service",
            method="POST",
            description="Resume a paused endpoint or service.",
            tags=[tag],
            engine=action_engine,
            profile=ActionProfile.ENDPOINT,
        )
        async def server_resume(request: Any = None) -> dict[str, Any]:
            """Resume an endpoint or service."""
            payload: dict[str, Any] = {}
            if isinstance(request, dict):
                payload = request
            elif request is not None and all(hasattr(request, attr) for attr in ("endpoint", "service", "method")):
                payload = {
                    "endpoint": getattr(request, "endpoint", None),
                    "service": getattr(request, "service", None),
                    "method": getattr(request, "method", "GET"),
                }
            elif request is not None:
                try:
                    payload = await self._parse_request_json_payload(request)
                except Exception as exc:
                    raise ValidationError(
                        message="Invalid JSON payload for resume request",
                        details={"server_id": self._server_id},
                    ) from exc
            service_name = payload.get("service")
            endpoint_path = payload.get("endpoint")
            endpoint_method = payload.get("method", "GET")
            if service_name:
                logger.warning(
                    "Resuming service",
                    extra={"server_id": self._server_id, "service": service_name},
                )
                self.start_services()
                return {"status": "resumed", "message": "Service resumed", "service": service_name}
            if endpoint_path:
                resumed = self.resume_endpoint(endpoint_path, endpoint_method)
                logger.warning(
                    "Resuming endpoint",
                    extra={"server_id": self._server_id, "path": resumed[1], "method": resumed[0]},
                )
                return {
                    "status": "resumed",
                    "message": "Endpoint resumed",
                    "endpoint": resumed[1],
                    "method": resumed[0],
                    "pause": self.get_pause_state(),
                }
            self.set_global_pause(False)
            logger.warning("Global pause disabled", extra={"server_id": self._server_id})
            return {"status": "resumed", "message": "Global pause disabled", "pause": self.get_pause_state()}
        # Register management endpoints
        self.register_action(server_status, path=f"{prefix}/status", method="GET")
        self.register_action(server_health, path=f"{prefix}/health", method="GET")
        self.register_action(server_pipeline, path=f"{prefix}/pipeline", method="GET")
        self.register_action(server_tokens_create, path=f"{prefix}/tokens/create", method="POST")
        self.register_action(server_tokens_list, path=f"{prefix}/tokens/list", method="GET")
        self.register_action(server_tokens_revoke, path=f"{prefix}/tokens/revoke", method="POST")
        self.register_action(server_tokens_usage_record, path=f"{prefix}/tokens/usage", method="POST")
        self.register_action(server_tokens_usage_list, path=f"{prefix}/tokens/usage", method="GET")
        self.register_action(server_tokens_recharge, path=f"{prefix}/tokens/recharge", method="POST")
        self.register_action(server_tokens_balance, path=f"{prefix}/tokens/balance", method="GET")
        self.register_action(health_root, path="/health", method="GET")
        self.register_action(server_log, path=f"{prefix}/log", method="POST")
        self.register_action(server_start, path=f"{prefix}/start", method="POST")
        self.register_action(server_stop, path=f"{prefix}/stop", method="POST")
        self.register_action(server_restart, path=f"{prefix}/restart", method="POST")
        self.register_action(server_pause, path=f"{prefix}/pause", method="POST")
        self.register_action(server_resume, path=f"{prefix}/resume", method="POST")
        logger.info(f"Admin endpoints registered at {prefix}")

    def __repr__(self) -> str:
        """String representation."""
        status = "running" if self._is_running else "stopped"
        location = f"{self._host}:{self._port}" if self._is_running else ""
        return f"XWApiServer(engine={self._engine.name}, status={status}, {location}, actions={len(self._actions)})"
