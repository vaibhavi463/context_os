# ContextOS Architecture Guide

## Overview
ContextOS is built using a domain-driven micro-layer architecture:

```
[React SPA] --> [FastAPI Gateway] --> [Agent Orchestrator] --> [Retrieval Engine] --> [PostgreSQL + pgvector]
                                   └-> [MCP Tool Server]  --> [HITL Gate]
```

## Bounded Contexts
1. **Identity & Tenant Context**: User roles (`admin`, `ops_engineer`, `support_engineer`), JWT auth, Postgres Row Level Security (RLS).
2. **Ingestion & Retrieval Context**: Recursive 512-token chunking, Gemini `text-embedding-004`, pgvector HNSW cosine search + FTS `ts_rank_cd` + Reciprocal Rank Fusion (RRF $k=60$).
3. **Agent Orchestration Context**: Prompt assembly, citation parser (`[Doc:Title#Chunk:N]`), SSE response streaming.
4. **Tool Execution & Approvals Context**: FastMCP server, RBAC scope guard, HMAC-signed JWT approval tokens.
5. **Telemetry & Audit Context**: Prometheus middleware, OpenTelemetry spans, append-only `audit_logs`.
