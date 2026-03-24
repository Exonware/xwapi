# XWAPI Engine Roadmap

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** connect@exonware.com  
**Version:** 1.0.0

## Overview

This document outlines the roadmap for API server engines in XWAPI, following the strategy pattern similar to xwaction's engine system.

## Current Engines

✅ **Implemented:**
- `FastAPIServerEngine` (HTTP_REST) - Default
- `FlaskServerEngine` (HTTP_REST)
- `GrpcServerEngine` (GRPC) - Phase 1
- `GraphQLServerEngine` (HTTP_GRAPHQL) - Phase 1 (Strawberry)
- `WebSocketServerEngine` (WEBSOCKET) - Phase 1 (FastAPI-based)

## Priority 1: High-Value HTTP REST Engines

These are the most commonly used Python web frameworks for REST APIs:

### 1. Django REST Framework Engine
- **Protocol:** `HTTP_REST`
- **Why:** Most popular Python web framework, mature ecosystem
- **Use Case:** Large applications, admin interface, ORM integration
- **Priority:** High
- **Status:** Not implemented

### 2. Starlette Engine
- **Protocol:** `HTTP_REST`
- **Why:** FastAPI is built on Starlette, lightweight, async-native
- **Use Case:** High-performance async APIs, microservices
- **Priority:** Medium
- **Status:** Not implemented

### 3. Quart Engine
- **Protocol:** `HTTP_REST`
- **Why:** Async Flask, drop-in replacement for Flask with async/await
- **Use Case:** Migrating Flask apps to async, async-first APIs
- **Priority:** Medium
- **Status:** Not implemented

### 4. Sanic Engine
- **Protocol:** `HTTP_REST`
- **Why:** High-performance async framework, built for speed
- **Use Case:** High-throughput APIs, real-time applications
- **Priority:** Medium
- **Status:** Not implemented

## Priority 2: Alternative HTTP Protocols

### 5. GraphQL Engine (Strawberry)
- **Protocol:** `HTTP_GRAPHQL`
- **Why:** GraphQL is popular for flexible queries, type-safe with Strawberry
- **Use Case:** APIs with complex query requirements, mobile apps
- **Priority:** High
- **Status:** ✅ Implemented (basic - requires type generation for full functionality)

### 6. GraphQL Engine (Graphene)
- **Protocol:** `HTTP_GRAPHQL`
- **Why:** Alternative GraphQL implementation, Django integration
- **Use Case:** Django-based GraphQL APIs
- **Priority:** Medium
- **Status:** Not implemented

### 7. JSON-RPC Engine
- **Protocol:** `HTTP_RPC`
- **Why:** RPC-style APIs, simpler than REST for some use cases
- **Use Case:** Internal APIs, RPC-style services
- **Priority:** Medium
- **Status:** Not implemented

## Priority 3: Non-HTTP Protocols

### 8. gRPC Engine
- **Protocol:** `GRPC`
- **Why:** High-performance binary protocol, streaming support, type-safe
- **Use Case:** Microservices, high-performance APIs, streaming
- **Priority:** High
- **Status:** ✅ Implemented (basic - requires proto file generation for full functionality)

### 9. WebSocket Engine (FastAPI-based)
- **Protocol:** `WEBSOCKET`
- **Why:** Real-time bidirectional communication
- **Use Case:** Chat, real-time updates, live data feeds
- **Priority:** High
- **Status:** ✅ Implemented

### 10. WebSocket Engine (Socket.IO)
- **Protocol:** `WEBSOCKET`
- **Why:** Popular WebSocket library with fallbacks
- **Use Case:** Real-time apps with browser compatibility
- **Priority:** Medium
- **Status:** Not implemented

### 11. Server-Sent Events (SSE) Engine
- **Protocol:** `SSE`
- **Why:** Server-to-client streaming, simpler than WebSocket
- **Use Case:** Live updates, notifications, progress tracking
- **Priority:** Medium
- **Status:** Not implemented

## Priority 4: Message Queue & Event-Driven

### 12. Celery Engine
- **Protocol:** `TASK_QUEUE`
- **Why:** Most popular Python task queue, integrates with xwaction
- **Use Case:** Background jobs, scheduled tasks, distributed processing
- **Priority:** High (xwaction already has CeleryActionEngine)
- **Status:** Not implemented

### 13. Kafka Consumer Engine
- **Protocol:** `KAFKA`
- **Why:** High-throughput event streaming, partitioned logs
- **Use Case:** Event-driven architectures, log aggregation, real-time analytics
- **Priority:** High
- **Status:** Not implemented

### 14. RabbitMQ Engine
- **Protocol:** `MESSAGE_QUEUE`
- **Why:** Popular message broker, AMQP protocol
- **Use Case:** Message queues, pub/sub, task distribution
- **Priority:** Medium
- **Status:** Not implemented

### 15. NATS Engine
- **Protocol:** `NATS`
- **Why:** Lightweight, high-performance pub/sub
- **Use Case:** Microservices communication, event streaming
- **Priority:** Medium
- **Status:** Not implemented

### 16. Redis Streams Engine
- **Protocol:** `REDIS_STREAMS`
- **Why:** Simple streaming with Redis, good for small-scale
- **Use Case:** Simple event streaming, pub/sub with Redis
- **Priority:** Medium
- **Status:** Not implemented

## Priority 5: Specialized Servers

### 17. Webhook Receiver Engine
- **Protocol:** `WEBHOOK`
- **Why:** Receive webhooks from external systems
- **Use Case:** Integration with third-party services, event ingestion
- **Priority:** Medium
- **Status:** Not implemented

### 18. Embedded/In-Process Engine
- **Protocol:** `EMBEDDED`
- **Why:** SDK-style APIs without network layer
- **Use Case:** Library APIs, testing, in-process communication
- **Priority:** Low
- **Status:** Not implemented

## Implementation Priority

### Phase 1 (Immediate - High Value)
1. ✅ FastAPI (done)
2. ✅ Flask (done)
3. ✅ **gRPC Engine** - High performance, type-safe (basic implementation)
4. ✅ **GraphQL Engine (Strawberry)** - Modern GraphQL (basic implementation)
5. ✅ **WebSocket Engine (FastAPI)** - Real-time support (done)

### Phase 2 (Short-term - Common Use Cases)
6. **Django REST Framework** - Most popular framework
7. **Kafka Consumer** - Event-driven architecture
8. **Celery Engine** - Background tasks (xwaction integration)
9. **JSON-RPC** - RPC-style APIs

### Phase 3 (Medium-term - Specialized)
10. **Quart** - Async Flask
11. **Sanic** - High-performance async
12. **RabbitMQ** - Message queue
13. **NATS** - Lightweight pub/sub
14. **SSE Engine** - Server-sent events

### Phase 4 (Long-term - Niche)
15. **Starlette** - Low-level async
16. **Graphene** - Alternative GraphQL
17. **Socket.IO** - WebSocket with fallbacks
18. **Redis Streams** - Simple streaming
19. **Webhook Receiver** - External integrations
20. **Embedded** - In-process APIs

## Engine Selection Criteria

When choosing which engines to implement, consider:

1. **Adoption Rate** - How widely used is the framework/protocol?
2. **Performance** - Does it offer significant performance benefits?
3. **Ecosystem** - Is there a rich ecosystem of tools/libraries?
4. **Integration** - Does it integrate well with xwaction/xwsystem?
5. **Use Case Fit** - Does it solve a specific problem well?
6. **Maintenance Burden** - How much effort to maintain?

## Notes

- Engines should follow the same pattern as FastAPI/Flask
- Each engine should declare its `protocol_type`
- Engines should integrate with xwaction's action execution system
- Admin endpoints are optional (HTTP engines support them)
- Schema generation is protocol-specific (OpenAPI for HTTP, Protobuf for gRPC, etc.)

