#exonware/xwapi/src/exonware/xwapi/agents/__init__.py
"""
API Agent Engine System
Strategy pattern implementation for pluggable API agent engines.
Supports multiple agent types: Core Action, Safety/Trust/Security,
Reliability/Performance, Observability/Operations, Contract/Evolution.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.3
"""

from typing import Any, Optional
from .contracts import IApiAgentEngine, AgentType
from .base import AApiAgentEngineBase
from .native import NativeAgentEngine
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


class ApiAgentEngineRegistry:
    """
    API Agent Engine Registry
    Manages registration and selection of API agent engines using Strategy pattern.
    """

    def __init__(self):
        self._engines: dict[str, IApiAgentEngine] = {}
        self._default_engine: Optional[str] = None

    def register(self, engine: IApiAgentEngine, set_default: bool = False):
        """
        Register an API agent engine.
        Args:
            engine: Engine instance implementing IApiAgentEngine
            set_default: Whether to set this as the default engine
        """
        self._engines[engine.name] = engine
        if set_default or self._default_engine is None:
            self._default_engine = engine.name
        logger.info(f"Registered API agent engine: {engine.name}")

    def get_engine(self, name: Optional[str] = None) -> Optional[IApiAgentEngine]:
        """
        Get engine by name, or default if name is None.
        Args:
            name: Engine name (e.g., 'native', 'router', 'planner'), or None for default
        Returns:
            Engine instance or None if not found
        """
        if name is None:
            name = self._default_engine
        if name is None:
            return None
        return self._engines.get(name)

    def get_all_engines(self) -> dict[str, IApiAgentEngine]:
        """Get all registered engines."""
        return self._engines.copy()

    def list_engines(self) -> list[str]:
        """List all registered engine names."""
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
# Global registry instance
api_agent_engine_registry = ApiAgentEngineRegistry()
# Auto-register default engines
try:
    native_agent_engine = NativeAgentEngine()
    api_agent_engine_registry.register(native_agent_engine, set_default=True)
except Exception as e:
    logger.warning(f"Failed to register Native agent engine: {e}")
__all__ = [
    "IApiAgentEngine",
    "AgentType",
    "AApiAgentEngineBase",
    "ApiAgentEngineRegistry",
    "api_agent_engine_registry",
    "NativeAgentEngine",
]
