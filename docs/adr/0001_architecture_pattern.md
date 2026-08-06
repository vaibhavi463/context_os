# ADR 0001: Clean Layered Architecture Pattern

## Status
Accepted

## Context
ContextOS requires high maintainability, strict separation of concerns, testability, and enterprise-grade reliability across API endpoints, agent domain orchestrators, RAG retrieval engines, and tool execution servers.

## Decision
We adopt a strict Clean Layered Architecture (`API -> Service -> Repository -> Database`).
- **API Layer**: `backend/app/api/v1/` (FastAPI routers, request validation, HTTP responses)
- **Domain Layer**: `backend/app/domain/` (Agents, Retrieval, Audit domain logic)
- **Infrastructure Layer**: `backend/app/infrastructure/` (LLM providers, Security, External Clients, Rate Limiter)
- **Repository Layer**: `backend/app/repositories/` (SQLAlchemy async data access abstraction)

## Consequences
- Prevents circular imports and tight coupling.
- Enables seamless unit testing via repository mocks and dependency injection.
