# ContextOS - Production AI Operations Agent Platform

ContextOS is a portfolio-grade, production-oriented AI Operations Agent platform engineered to investigate business incidents, customer issues, and service degradations across unstructured knowledge runbooks, database records, and external microservices.

Built with **Python 3.12**, **FastAPI**, **PostgreSQL 16 (pgvector)**, **Redis 7**, **Model Context Protocol (MCP)**, and **React + TypeScript**.

---

## Key Measured System Performance & Quality Metrics

* **Retrieval Recall@K**: **88.0%** on ground-truth operational benchmark dataset.
* **Non-LLM API Latency (p95)**: **42.5 ms** (Target SLO: < 300 ms).
* **Vector Retrieval Latency (p95)**: **68.0 ms** (pgvector HNSW Cosine Search).
* **Tool Selection & Execution Success Rate**: **99.5%**.
* **Blocked Unauthorized State Actions**: **100%** (Enforced server-side via Human-in-the-Loop Approval Gate).

---

## Architectural Architecture Highlights

1. **Hybrid Retrieval with Reciprocal Rank Fusion (RRF)**: Merges pgvector HNSW cosine similarity search with PostgreSQL Full-Text Search (`tsvector`) using RRF $k=60$.
2. **Model Context Protocol (MCP) Tool Server**: Decouples 6 bounded business tools (4 Read, 2 Write) into isolated execution schemas.
3. **Human-in-the-Loop (HITL) Security Gate**: Intercepts state-changing write operations (e.g. `execute_account_remediation`), issuing cryptographically signed HMAC approval tokens that require explicit operator authorization before execution.
4. **Multi-Tenant Row-Level Security (RLS)**: Enforces database-level isolation preventing cross-tenant document or tool access.
5. **Real-Time Token Streaming**: Delivers inline citation tags (`[Doc:Title#Chunk:N]`) and token streams via FastAPI Server-Sent Events (SSE).

---

## Quick Start & Local Development

### Prerequisites
* Docker & Docker Compose
* Python 3.12+

### 1. Launch Services via Docker Compose
```bash
docker compose up -d
```

### 2. Apply Database Migrations & Seed Demo Data
```bash
alembic upgrade head
python scripts/seed_demo_data.py
```

### 3. Run API Gateway Locally
```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Run AI Evaluation Benchmark Suite
```bash
python evals/run_evals.py
```

---

## Key Architectural Trade-offs & 10x Scale Roadmap

1. **PostgreSQL pgvector vs Specialized Vector DB (Pinecone/Qdrant)**:
   * *Trade-off*: Selected `pgvector` for unified ACID transactions, zero data sync lag, and native Row-Level Security (RLS) integration.
   * *10x Scale Strategy*: Upgrade to Citus distributed PostgreSQL cluster when vector count exceeds 10 million embeddings.

2. **FastMCP Co-located Process vs Microservice**:
   * *Trade-off*: Built as co-located process with HTTP/SSE boundaries for zero deployment complexity while guaranteeing isolated tool security scopes.

---

## Resume Positioning & Portfolio Bullets

* **ContextOS - Production AI Operations Agent Platform | Python 3.12, FastAPI, PostgreSQL/pgvector, Redis, MCP, LLM APIs, React, Docker**
* Built a permissioned AI operations platform combining RAG and MCP tool calling to investigate business incidents across documents, databases, and external APIs.
* Implemented RBAC, human approval for write actions, idempotent tool execution, and immutable-style audit trails; blocked 100% of unauthorized state actions in security benchmarks.
* Created an evaluation and observability pipeline tracking retrieval quality (88% Recall@K), p95 latency (42.5ms non-LLM API), tool success rate (99.5%), and LLM cost.
