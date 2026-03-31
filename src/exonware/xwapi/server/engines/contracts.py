#exonware/xwapi/src/exonware/xwapi/server/engines/contracts.py
"""
API Server Engine Contracts
Interfaces for API server engine implementations (Strategy pattern).
Supports multiple protocol types: HTTP (REST, GraphQL, RPC), gRPC, WebSocket,
Message Queue, Event-Driven, Streaming, etc.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.3
"""

from __future__ import annotations
from typing import Any, Protocol, runtime_checkable, Optional, TYPE_CHECKING
from enum import Enum
from exonware.xwapi.config import XWAPIConfig
# TYPE_CHECKING import to avoid circular dependency at runtime
# XWAction is only used in type hints, not at runtime
if TYPE_CHECKING:
    from exonware.xwaction import XWAction


class ProtocolType(Enum):
    """
    API Server Protocol Types.
    Protocols are defined by engines, not as a separate concept.
    Each engine declares its protocol_type property.
    """
    # Exposure Servers (How clients connect)
    HTTP_REST = "http_rest"  # HTTP REST (JSON, CRUD)
    HTTP_GRAPHQL = "http_graphql"  # HTTP GraphQL (schema query)
    HTTP_RPC = "http_rpc"  # HTTP RPC (JSON-RPC/XML-RPC style)
    GRPC = "grpc"  # gRPC (HTTP/2 + protobuf; unary + streaming)
    WEBSOCKET = "websocket"  # WebSocket (bi-directional sessions)
    SSE = "sse"  # Server-Sent Events (server→client stream)
    WEBHOOK = "webhook"  # Webhook Receiver (external systems push events)
    WEBRTC = "webrtc"  # WebRTC Signaling (real-time media/control)
    TCP_CUSTOM = "tcp_custom"  # TCP Custom Protocol (binary/custom framing)
    UDP = "udp"  # UDP (telemetry / low-latency fire-and-forget)
    UNIX_SOCKET = "unix_socket"  # Unix Domain Socket (local high-trust IPC)
    NAMED_PIPE = "named_pipe"  # Named Pipe (Windows IPC)
    CLI = "cli"  # CLI / STDIN (pipes, commands)
    EMBEDDED = "embedded"  # In-Process Embedded (SDK exposes API without network)
    # Email Protocol Servers (RFC-compliant email handling)
    SMTP = "smtp"  # SMTP Server (RFC 5321) - Sending emails
    POP3 = "pop3"  # POP3 Server (RFC 1939) - Download emails (local)
    IMAP = "imap"  # IMAP Server (RFC 9051) - Sync emails (server-based)
    # Event & Messaging Servers (Async-first integration)
    MESSAGE_QUEUE = "message_queue"  # Message Queue Consumer (RabbitMQ/AMQP)
    KAFKA = "kafka"  # Kafka Consumer (partitioned log ingestion)
    NATS = "nats"  # NATS Subscriber (lightweight pub/sub)
    REDIS_STREAMS = "redis_streams"  # Redis Streams Consumer
    CLOUD_PUBSUB = "cloud_pubsub"  # Cloud Pub/Sub Subscriber
    EVENT_BUS = "event_bus"  # Event Bus Ingress (normalized internal event gateway)
    TASK_QUEUE = "task_queue"  # Task Queue Worker (Celery-like model)
    SCHEDULER = "scheduler"  # Scheduler Server (cron-like + calendar triggers)
    REPLAY = "replay"  # Replay Server (replay events deterministically)
    # Execution & Workflow Servers (Where "work" happens)
    FUNCTION_RUNTIME = "function_runtime"  # Function Runtime Server (FaaS-style)
    WORKFLOW_ORCHESTRATOR = "workflow_orchestrator"  # Workflow Orchestrator (DAG/state machine)
    SAGA = "saga"  # Saga/Compensation Server (rollbacks across systems)
    LONG_RUNNING_JOB = "long_running_job"  # Long-Running Job Server (minutes/hours)
    STREAMING_COMPUTE = "streaming_compute"  # Streaming Compute Server (continuous transforms)
    RULES_ENGINE = "rules_engine"  # Rules Engine Server (deterministic decision tables)
    POLICY_ENGINE = "policy_engine"  # Policy Engine Server (OPA-like)
    SANDBOX = "sandbox"  # Sandbox / Simulation Server (dry-run with limits)
    EDGE_EXECUTION = "edge_execution"  # Edge Execution Server (geo-distributed)
    BATCH_EXECUTION = "batch_execution"  # Batch Execution Server (bulk jobs / ETL)
    CONNECTOR_RUNTIME = "connector_runtime"  # Connector/Adapter Runtime Server
    # Data Plane Servers (State, contracts, knowledge)
    SCHEMA_REGISTRY = "schema_registry"  # Schema/Contract Server (OpenAPI/JSON Schema/Proto)
    VERSIONING = "versioning"  # Versioning & Migration Server
    SECRETS = "secrets"  # Secrets Server (vault-like)
    IDENTITY = "identity"  # Identity Server (users, service identities)
    SESSION = "session"  # Session Server (stateful agent sessions)
    STATE_STORE = "state_store"  # State Store Server (workflow state, checkpoints)
    CACHE = "cache"  # Cache Server (latency optimization)
    VECTOR_KNOWLEDGE = "vector_knowledge"  # Vector/Knowledge Server (retrieval, embeddings)
    ARTIFACT = "artifact"  # Artifact Server (files, blobs, generated outputs)
    AUDIT_LOG = "audit_log"  # Audit Log Server (immutable event/audit trail)
    # Control Plane Servers (Operate, govern, observe)
    ADMIN_CONSOLE = "admin_console"  # Admin/Console Server (UI/API for operators)
    CONFIG = "config"  # Config Server (dynamic config, feature flags)
    RATE_LIMIT = "rate_limit"  # Rate Limit / Quota Server
    TENANT_BILLING = "tenant_billing"  # Tenant & Billing Server
    OBSERVABILITY = "observability"  # Observability Server (metrics)
    TRACING = "tracing"  # Tracing Server (distributed traces)
    LOGGING = "logging"  # Logging Server (structured logs)
    HEALTH_SLO = "health_slo"  # Health & SLO Server
    INCIDENT = "incident"  # Incident/Kill-Switch Server
    COMPLIANCE = "compliance"  # Compliance Server (retention, residency, PDPL/GDPR)
@runtime_checkable

class IApiServerEngine(Protocol):
    """
    API Server Engine Interface (Strategy Pattern)
    Protocol-agnostic interface for all API server engines.
    Each engine represents a different protocol/framework combination.
    Examples:
    - HTTP: FastAPI, Flask, Django REST
    - gRPC: grpcio, grpclib
    - WebSocket: FastAPI WebSocket, Socket.IO
    - Message Queue: Kafka, RabbitMQ, NATS
    - Event-Driven: Celery, RQ
    """
    @property

    def name(self) -> str:
        """
        Get engine name (e.g., 'fastapi', 'grpc', 'websocket').
        Returns:
            Engine name string
        """
        ...
    @property

    def protocol_type(self) -> ProtocolType:
        """
        Get protocol type this engine implements.
        Returns:
            ProtocolType enum value
        """
        ...
    @property

    def supports_admin_endpoints(self) -> bool:
        """
        Whether this engine supports built-in admin endpoints.
        HTTP engines typically support admin endpoints.
        Non-HTTP engines may not (or may have protocol-specific admin).
        Returns:
            True if admin endpoints are supported
        """
        ...

    def create_app(self, config: XWAPIConfig) -> Any:
        """
        Create the underlying server application.
        Args:
            config: XWAPI configuration
        Returns:
            Protocol-specific app instance (varies by engine)
        """
        ...

    def register_action(self, app: Any, action: XWAction, 
                       route_info: dict[str, Any]) -> bool:
        """
        Register XWAction as an API endpoint/route.
        Uses XWAction's engine system internally to execute actions.
        Route info is protocol-specific (e.g., path+method for HTTP, 
        service+method for gRPC, topic for Message Queue).
        Args:
            app: Server app instance (from create_app)
            action: XWAction instance to register
            route_info: Protocol-specific route information
                - HTTP: {'path': '/users', 'method': 'GET'}
                - gRPC: {'service': 'UserService', 'method': 'GetUser'}
                - WebSocket: {'path': '/ws/chat'}
                - Message Queue: {'topic': 'user.events', 'consumer_group': 'api'}
                - Event-Driven: {'event_type': 'user.created'}
        Returns:
            True if registration successful, False otherwise
        """
        ...

    def generate_schema(self, app: Any, actions: list[XWAction],
                       config: XWAPIConfig) -> dict[str, Any]:
        """
        Generate API schema/documentation for registered actions.
        Protocol-specific schema format:
        - HTTP: OpenAPI/Swagger
        - gRPC: Protocol Buffer schema
        - WebSocket: Custom schema
        - Message Queue: Topic/event schema
        Args:
            app: Server app instance
            actions: List of registered XWAction instances
            config: XWAPI configuration
        Returns:
            Protocol-specific schema dictionary
        """
        ...

    def start_server(self, app: Any, **kwargs) -> None:
        """
        Start the API server.
        Args:
            app: Server app instance
            **kwargs: Protocol-specific server options
                - HTTP: host, port, reload, etc.
                - gRPC: host, port, max_workers, etc.
                - WebSocket: host, port, etc.
                - Message Queue: broker_url, topics, etc.
        """
        ...

    def stop_server(self, app: Any) -> None:
        """
        Stop the API server.
        Args:
            app: Server app instance
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
