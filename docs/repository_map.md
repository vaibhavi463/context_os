# ContextOS Repository Map & Folder Architecture

```
context_os/
├── .github/
│   └── workflows/ci.yml         # GitHub Actions CI/CD Pipeline
├── backend/
│   ├── Dockerfile              # Multi-stage non-root container build
│   └── app/
│       ├── api/v1/             # REST API routers & endpoints (Auth, Documents, Investigations, Approvals, Admin)
│       ├── core/               # Configuration & settings management (Pydantic BaseSettings)
│       ├── db/                 # Database engine & Alembic migrations
│       ├── domain/             # Domain logic (Agents, Hybrid Retrieval, Audit Logger)
│       ├── infrastructure/     # Infrastructure (Gemini Provider, Embeddings, Security, External Clients, Rate Limiter)
│       ├── mcp_server/         # FastMCP Tool Server, Registry, Read/Write Tools, HITL Approval Gate
│       ├── models/             # SQLAlchemy domain models (User, Document, Chunk, Investigation, Approval, Audit)
│       ├── repositories/       # Generic BaseRepository & specialized domain repositories
│       ├── schemas/            # Pydantic request/response schemas
│       └── telemetry/          # OpenTelemetry & Prometheus metrics exporter
├── docs/                       # Architectural docs, ADRs, Security, Deployment, & DR guides
├── evals/                      # AI Benchmark evaluation suite & ground-truth dataset
├── frontend/                   # React 18, TypeScript 5, Tailwind CSS, & Vite application
├── load_tests/                 # Locust load testing harness & benchmark report generator
├── monitoring/                 # Prometheus scrape configs & Grafana dashboard JSON specs
├── scripts/                    # Demo seeding, incident drills, & backup/restore verification
├── tests/                      # Unit, Integration, Failure, & End-to-End test suites
├── docker-compose.yml          # Multi-container orchestration (Postgres pgvector, Redis, API)
└── pyproject.toml              # Python dependencies & build-system configuration
```
