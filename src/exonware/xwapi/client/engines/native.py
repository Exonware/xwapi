#exonware/xwapi/agents/native.py
"""
Native Agent Engine Implementation
Native agent engine - the default XWApiAgent behavior.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.12
"""

from typing import Any
from inspect import getmembers, isfunction, ismethod
from .base import AApiAgentEngineBase
from .contracts import AgentType
from exonware.xwsystem import get_logger
from exonware.xwapi.client.runtime_gate import ensure_xwapi_runtime_allows_action
logger = get_logger(__name__)


def discover_xwaction_bound_methods(agent_instance: Any) -> list[Any]:
    """
    Return bound callables on ``agent_instance`` that carry an ``xwaction`` marker.

    Walks the instance class MRO (same rules as :class:`NativeAgentEngine`) so base-class
    actions on ``XWApiAgent`` (for example ``revive_auths``) are discovered for subclasses
    that do not override them.
    """
    actions: list[Any] = []
    discovered_names: set[str] = set()
    for cls in agent_instance.__class__.__mro__:
        if cls is object:
            continue
        for name, _attr in getmembers(cls, predicate=lambda x: ismethod(x) or isfunction(x)):
            if name.startswith("_"):
                continue
            if name in discovered_names:
                continue
            try:
                method = getattr(agent_instance, name)
            except AttributeError:
                continue
            if hasattr(method, "xwaction"):
                actions.append(method)
                discovered_names.add(name)
                logger.debug("Discovered action: %s from class %s", name, cls.__name__)
    # INFO here duplicates callers (e.g. XWApiAgent._discover_actions) and spams logs when
    # discover_xwaction_bound_methods is used for read-only merges (command bot /help, menus).
    logger.debug(
        "Discovered %s actions for agent %s",
        len(actions),
        getattr(agent_instance, "_name", "unknown"),
    )
    return actions


class NativeAgentEngine(AApiAgentEngineBase):
    """
    Native Agent Engine
    Implements the standard XWApiAgent behavior:
    - Action discovery via @XWAction decorator
    - Standard action execution
    - Session and authentication management
    - Entity management
    """

    def __init__(self):
        """Initialize Native agent engine."""
        super().__init__("native")
        self._agent_type = AgentType.NATIVE
    @property

    def agent_type(self) -> AgentType:
        """Get agent type (NATIVE)."""
        return self._agent_type

    def discover_actions(self, agent_instance: Any) -> list[Any]:
        """
        Discover XWAction-decorated methods in agent instance.
        Traverses class hierarchy (MRO) to find all @XWAction methods
        from both current class and parent classes.
        Args:
            agent_instance: Agent instance to discover actions from
        Returns:
            List of discovered actions (bound methods with xwaction attribute)
        """
        return discover_xwaction_bound_methods(agent_instance)

    def register_action(self, agent_instance: Any, action: Any) -> bool:
        """
        Register an action with the agent.
        For native engine, this just adds the action to the agent's action list.
        Args:
            agent_instance: Agent instance
            action: Action to register
        Returns:
            True if registration successful
        """
        if not hasattr(action, 'xwaction'):
            logger.warning(f"Action {getattr(action, '__name__', 'unknown')} does not have xwaction attribute")
            return False
        # Get agent's action list
        if not hasattr(agent_instance, '_actions'):
            agent_instance._actions = []
        if action not in agent_instance._actions:
            agent_instance._actions.append(action)
            logger.debug(f"Registered action: {getattr(action, '__name__', 'unknown')}")
            return True
        else:
            logger.debug(f"Action {getattr(action, '__name__', 'unknown')} already registered")
            return False

    def execute_action(self, agent_instance: Any, action: Any, context: Any, **kwargs) -> Any:
        """
        Execute an action using standard XWAction execution.
        Args:
            agent_instance: Agent instance
            action: Action to execute
            context: Action context
            **kwargs: Action parameters
        Returns:
            Action result
        """
        subject = getattr(action, "__self__", None) or agent_instance
        ensure_xwapi_runtime_allows_action(subject, action)
        # Standard XWAction execution
        if hasattr(action, 'execute'):
            return action.execute(context, **kwargs)
        elif hasattr(action, '__call__'):
            return action(**kwargs)
        else:
            raise ValueError(f"Action {getattr(action, '__name__', 'unknown')} is not callable")
