#exonware/xwapi/agents/base.py
"""
API Agent Engine Base Classes
Base implementation for API agent engines.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.8
"""

from typing import Any, Optional
from abc import ABC
from .contracts import IApiAgentEngine
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


class AApiAgentEngineBase(ABC):
    """
    Abstract Base Class for API Agent Engines
    Provides common functionality for agent engines.
    """

    def __init__(self, name: str):
        """
        Initialize base agent engine.
        Args:
            name: Engine name (e.g., 'native', 'router', 'planner')
        """
        self._name = name
        self._config: dict[str, Any] | None = None
    @property

    def name(self) -> str:
        """Get engine name."""
        return self._name

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
