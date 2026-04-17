#exonware/xwapi/engines/__init__.py
"""
Pluggable **server engines** for publishing exposable actions (FastAPI, Flask, …).

Pick an engine when creating the app or ``XWApiServer``; default FastAPI keeps OpenAPI/ASGI
power; Flask supports WSGI. *Build once, publish anywhere* — actions stay stable across engines.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.10
"""

from __future__ import annotations
from typing import Any, Optional
from .contracts import IApiServerEngine, ProtocolType
from .base import AApiServerEngineBase
from .http_base import AHttpServerEngineBase
# Engine-agnostic: engines are imported lazily only when needed
# No module-level imports of specific engines to maintain engine-agnostic design
# Engines are imported dynamically inside functions when actually used
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


class ApiServerEngineRegistry:
    """
    API Server Engine Registry
    Manages registration and selection of API server engines using Strategy pattern.
    """

    def __init__(self):
        self._engines: dict[str, IApiServerEngine] = {}
        self._default_engine: str | None = None

    def register(self, engine: IApiServerEngine, set_default: bool = False):
        """
        Register an API server engine.
        Args:
            engine: Engine instance implementing IApiServerEngine
            set_default: Whether to set this as the default engine
        """
        self._engines[engine.name] = engine
        if set_default or self._default_engine is None:
            self._default_engine = engine.name
        logger.info(f"Registered API server engine: {engine.name}")

    def get_engine(self, name: str | None = None) -> IApiServerEngine | None:
        """
        Get engine by name, or default if name is None.
        Args:
            name: Engine name (e.g., 'fastapi', 'flask'), or None for default
        Returns:
            Engine instance or None if not found
        """
        # Lazy initialization: auto-register engines on first access
        if not self._engines:
            self._auto_register_engines()
        if name is None:
            name = self._default_engine
        if name is None:
            return None
        return self._engines.get(name)

    def get_all_engines(self) -> dict[str, IApiServerEngine]:
        """Get all registered engines."""
        if not self._engines:
            self._auto_register_engines()
        return self._engines.copy()

    def list_engines(self) -> list[str]:
        """List all registered engine names."""
        if not self._engines:
            self._auto_register_engines()
        return list(self._engines.keys())

    def set_default(self, name: str) -> bool:
        """
        Set default engine.
        Args:
            name: Engine name
        Returns:
            True if set, False if engine not found
        """
        if name in self._engines:
            self._default_engine = name
            return True
        return False

    def clear(self):
        """Clear all registered engines."""
        self._engines.clear()
        self._default_engine = None

    def _auto_register_engines(self):
        """
        Auto-register available engines (lazy initialization).
        Engine-agnostic: Only registers engines that are actually available.
        Engines are imported only when this method is called, not at module import time.
        """
        if self._engines:
            return  # Already initialized
        # Lazy import and register FastAPI engine
        try:
            from .fastapi import FastAPIServerEngine
            fastapi_engine = FastAPIServerEngine()
            self.register(fastapi_engine, set_default=True)
        except Exception as e:
            logger.debug(f"FastAPI engine not available: {e}")
        # Lazy import and register Flask engine
        try:
            from .flask import FlaskServerEngine
            flask_engine = FlaskServerEngine()
            self.register(flask_engine, set_default=False)
        except Exception as e:
            logger.debug(f"Flask engine not available: {e}")
        # Lazy import and register gRPC engine
        try:
            from .grpc import GrpcServerEngine
            grpc_engine = GrpcServerEngine()
            self.register(grpc_engine, set_default=False)
        except Exception as e:
            logger.debug(f"gRPC engine not available: {e}")
        # Lazy import and register GraphQL engine
        try:
            from .graphql import GraphQLServerEngine
            graphql_engine = GraphQLServerEngine()
            self.register(graphql_engine, set_default=False)
        except Exception as e:
            logger.debug(f"GraphQL engine not available: {e}")
        # Lazy import and register WebSocket engine
        try:
            from .websocket import WebSocketServerEngine
            websocket_engine = WebSocketServerEngine()
            self.register(websocket_engine, set_default=False)
        except Exception as e:
            logger.debug(f"WebSocket engine not available: {e}")
        # Lazy import and register SMTP engine
        try:
            from .smtp import SMTPServerEngine
            smtp_engine = SMTPServerEngine()
            self.register(smtp_engine, set_default=False)
        except Exception as e:
            logger.debug(f"SMTP engine not available: {e}")
        # Lazy import and register POP3 engine
        try:
            from .pop3 import POP3ServerEngine
            pop3_engine = POP3ServerEngine()
            self.register(pop3_engine, set_default=False)
        except Exception as e:
            logger.debug(f"POP3 engine not available: {e}")
        # Lazy import and register IMAP engine
        try:
            from .imap import IMAPServerEngine
            imap_engine = IMAPServerEngine()
            self.register(imap_engine, set_default=False)
        except Exception as e:
            logger.debug(f"IMAP engine not available: {e}")
        # Optional HTTP frameworks (install matching extras; see docs/REF_25_ENGINES.md)
        _optional = [
            ("starlette", "StarletteServerEngine"),
            ("quart", "QuartServerEngine"),
            ("sanic", "SanicServerEngine"),
            ("aiohttp", "AiohttpServerEngine"),
            ("blacksheep", "BlackSheepServerEngine"),
            ("litestar", "LitestarServerEngine"),
            ("django", "DjangoServerEngine"),
            ("mangum", "MangumServerEngine"),
        ]
        try:
            from . import optional_http_engines as _opt
            for mod_attr, cls_name in _optional:
                try:
                    cls = getattr(_opt, cls_name)
                    inst = cls()
                    self.register(inst, set_default=False)
                except Exception as e:
                    logger.debug("%s engine not available: %s", mod_attr, e)
        except Exception as e:
            logger.debug("optional_http_engines import failed: %s", e)
# Global registry instance
api_server_engine_registry = ApiServerEngineRegistry()
# Engine-agnostic: engines are auto-registered lazily on first access
# This ensures xwapi works even if no engines are installed
# Helper functions for lazy engine imports (engine-agnostic design)

def _get_fastapi_engine():
    """Lazy import FastAPIServerEngine."""
    from .fastapi import FastAPIServerEngine
    return FastAPIServerEngine


def _get_flask_engine():
    """Lazy import FlaskServerEngine."""
    from .flask import FlaskServerEngine
    return FlaskServerEngine


def _get_grpc_engine():
    """Lazy import GrpcServerEngine."""
    from .grpc import GrpcServerEngine
    return GrpcServerEngine


def _get_graphql_engine():
    """Lazy import GraphQLServerEngine."""
    from .graphql import GraphQLServerEngine
    return GraphQLServerEngine


def _get_websocket_engine():
    """Lazy import WebSocketServerEngine."""
    from .websocket import WebSocketServerEngine
    return WebSocketServerEngine
__all__ = [
    "IApiServerEngine",
    "ProtocolType",
    "AApiServerEngineBase",
    "AHttpServerEngineBase",
    "ApiServerEngineRegistry",
    "api_server_engine_registry",
    # Engine classes are available but imported lazily
    # Users can import them directly: from exonware.xwapi.engines.fastapi import FastAPIServerEngine
]
