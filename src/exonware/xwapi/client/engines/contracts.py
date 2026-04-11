#exonware/xwapi/agents/contracts.py
"""
API Agent Engine Contracts
Interfaces for API agent engine implementations (Strategy pattern).
Supports multiple agent types: Core Action, Safety/Trust/Security,
Reliability/Performance, Observability/Operations, Contract/Evolution.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.6
"""

from typing import Any, Protocol, runtime_checkable, TYPE_CHECKING, Optional
from enum import Enum
if TYPE_CHECKING:
    from exonware.xwaction import XWAction


class AgentType(Enum):
    """
    API Agent Types.
    Agents are categorized by their role in the API platform.
    Each agent engine declares its agent_type property.
    """
    # Core Action Agents (what to do)
    CALLER = "caller"  # Initiates actions
    ROUTER = "router"  # Chooses protocol/endpoint
    PLANNER = "planner"  # Multi-step plan
    EXECUTOR = "executor"  # Runs plan
    TOOL_CONNECTOR = "tool_connector"  # Calls external systems
    STATE = "state"  # Reads/writes state correctly
    DECISION = "decision"  # Act vs don't act
    VERIFICATION = "verification"  # Checks results vs intent
    CRITIC = "critic"  # Finds flaws before commit
    # Safety, Trust, Security Agents (what must not happen)
    AUTHZ = "authz"  # Permission checks
    POLICY = "policy"  # Business/geo/compliance policy
    PII_GUARD = "pii_guard"  # PII/Data Guard (redaction, minimization)
    PROMPT_FIREWALL = "prompt_firewall"  # Prompt-Injection/Context Firewall
    FRAUD_ABUSE = "fraud_abuse"  # Fraud/Abuse (anomaly + misuse)
    SANDBOXING = "sandboxing"  # Constrains execution
    ESCALATION = "escalation"  # Escalation/Human-in-the-loop
    KILL_SWITCH = "kill_switch"  # Stop authority
    # Reliability & Performance Agents (keep it alive)
    RETRY = "retry"  # Smart retry rules
    CIRCUIT_BREAKER = "circuit_breaker"  # Circuit breaker
    BACKPRESSURE = "backpressure"  # Backpressure/Load-shed
    TIMEOUT = "timeout"  # Timeout/Deadline
    COMPENSATION = "compensation"  # Undo/rollback
    QUEUE_TUNING = "queue_tuning"  # Consumer scaling
    PERFORMANCE_OPTIMIZER = "performance_optimizer"  # Latency/cost routing
    # Observability & Operations Agents (see and fix)
    TELEMETRY = "telemetry"  # Metrics/logs/traces
    ROOT_CAUSE = "root_cause"  # Correlation + diagnosis
    SELF_HEALING = "self_healing"  # Restart/re-route/redeploy
    SLO = "slo"  # Error budget enforcement
    RELEASE_CANARY = "release_canary"  # Safe rollout
    CONFIG_DRIFT = "config_drift"  # Detect misconfig
    # Contract & Evolution Agents (don't break clients)
    SCHEMA_REASONER = "schema_reasoner"  # Understands contracts
    COMPATIBILITY = "compatibility"  # Breaking change detection
    MIGRATION = "migration"  # Data + contract upgrades
    DEPRECATION = "deprecation"  # Sunset planning
    TEST_GENERATION = "test_generation"  # Contract tests, fuzzing
    # Native/Generic Agent (default implementation)
    NATIVE = "native"  # Native agent (current XWApiAgent behavior)
@runtime_checkable

class IApiAgentEngine(Protocol):
    """
    API Agent Engine Interface (Strategy Pattern)
    Defines the contract that all API agent engines must implement.
    Each engine represents a different agent type/role.
    Examples:
    - Native: Standard XWApiAgent behavior (action discovery, auth, sessions)
    - Router: Routes actions to appropriate endpoints/protocols
    - Planner: Creates multi-step plans for complex operations
    - Executor: Executes plans deterministically
    - Policy: Enforces business/security policies
    """
    @property

    def name(self) -> str:
        """
        Get engine name (e.g., 'native', 'router', 'planner').
        Returns:
            Engine name string
        """
        ...
    @property

    def agent_type(self) -> AgentType:
        """
        Get agent type this engine implements.
        Returns:
            AgentType enum value
        """
        ...

    def discover_actions(self, agent_instance: Any) -> list[Any]:
        """
        Discover actions from an agent instance.
        Args:
            agent_instance: Agent instance to discover actions from
        Returns:
            List of discovered actions
        """
        ...

    def register_action(self, agent_instance: Any, action: Any) -> bool:
        """
        Register an action with the agent.
        Args:
            agent_instance: Agent instance
            action: Action to register
        Returns:
            True if registration successful
        """
        ...

    def execute_action(self, agent_instance: Any, action: Any, context: Any, **kwargs) -> Any:
        """
        Execute an action with the agent's execution model.
        Args:
            agent_instance: Agent instance
            action: Action to execute
            context: Action context
            **kwargs: Action parameters
        Returns:
            Action result
        """
        ...

    def setup(self, config: dict[str, Any]) -> bool:
        """
        Setup engine with configuration.
        Args:
            config: Engine-specific configuration
        Returns:
            True if setup successful
        """
        ...
