#exonware/xwapi/agents/native.py
"""
Native Agent Engine Implementation
Native agent engine - the default XWApiAgent behavior.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.2
"""

from typing import Any
from inspect import getmembers, isfunction, ismethod
from .base import AApiAgentEngineBase
from .contracts import AgentType
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


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
        actions = []
        discovered_names = set()  # Track discovered method names to avoid duplicates
        # Traverse Method Resolution Order (MRO) to find all @XWAction methods
        for cls in agent_instance.__class__.__mro__:
            # Skip object base class
            if cls is object:
                continue
            # Get all members from this class
            for name, attr in getmembers(cls, predicate=lambda x: ismethod(x) or isfunction(x)):
                # Skip private methods and special methods
                if name.startswith('_'):
                    continue
                # Skip if we've already discovered this method name (subclass override)
                if name in discovered_names:
                    continue
                # Get the method from the instance (bound method)
                try:
                    method = getattr(agent_instance, name)
                except AttributeError:
                    continue
                # Check if method/function is decorated with XWAction
                if hasattr(method, 'xwaction'):
                    actions.append(method)
                    discovered_names.add(name)
                    logger.debug(f"Discovered action: {name} from class {cls.__name__}")
        logger.info(f"Discovered {len(actions)} actions for agent {getattr(agent_instance, '_name', 'unknown')}")
        return actions

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
        # Standard XWAction execution
        if hasattr(action, 'execute'):
            return action.execute(context, **kwargs)
        elif hasattr(action, '__call__'):
            return action(**kwargs)
        else:
            raise ValueError(f"Action {getattr(action, '__name__', 'unknown')} is not callable")
