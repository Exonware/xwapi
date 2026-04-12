#exonware/xwapi/engines/base.py
"""
API Server Engine Base Classes
Base implementation for API server engines.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.9
"""

from typing import Any, Optional
from abc import ABC
from .contracts import IApiServerEngine
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


class AApiServerEngineBase(ABC):
    """
    Abstract Base Class for API Server Engines
    Provides common functionality and integration with XWAction's engine system.
    """

    def __init__(self, name: str):
        """
        Initialize base engine.
        Args:
            name: Engine name (e.g., 'fastapi', 'flask')
        """
        self._name = name
        self._config: dict[str, Any] | None = None
        self._action_engine_registry = None  # Lazy-loaded to avoid import cycles
    @property

    def name(self) -> str:
        """Get engine name."""
        return self._name

    def _get_action_engine(self, action: Any, engine_name: str | None = None) -> Any | None:
        """
        Get appropriate ActionEngine from XWAction registry.
        Args:
            action: XWAction instance
            engine_name: Optional specific engine name, otherwise uses action's engine config
        Returns:
            IActionEngine instance or None
        """
        if self._action_engine_registry is None:
            try:
                from exonware.xwaction.engines import action_engine_registry  # type: ignore[import-untyped]
                self._action_engine_registry = action_engine_registry
            except Exception as e:
                logger.debug("xwaction.engines import failed: %s", e)
                return None
        if not self._action_engine_registry:
            return None
        # Try to get engine from action configuration
        if engine_name is None:
            # Get from action's engine property
            engines = getattr(action, 'engine', None)
            if isinstance(engines, list) and engines:
                engine_name = engines[0]
            elif isinstance(engines, str):
                engine_name = engines
        # Default to 'native' if not specified
        if not engine_name:
            engine_name = 'native'
        # Get engine from registry
        engine = self._action_engine_registry.get_engine(engine_name)
        # Fallback to native if not found
        if not engine:
            engine = self._action_engine_registry.get_engine('native')
        return engine

    def setup(self, config: dict[str, Any]) -> bool:
        """
        Setup engine with configuration.
        Args:
            config: Engine-specific configuration
        Returns:
            True if setup successful
        """
        self._config = config
        return True

    def stop_server(self, app: Any) -> None:
        """
        Default stop implementation (no-op).
        Override in subclasses if needed.
        Args:
            app: Framework app instance
        """
        logger.info(f"Stopping {self._name} server (default implementation)")
        # Default: no-op, subclasses should override
