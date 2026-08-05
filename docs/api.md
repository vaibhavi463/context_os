# ContextOS API Reference

## Base URL
`/api/v1`

## Endpoints

### Auth
- `POST /api/v1/auth/register`: Register user and tenant.
- `POST /api/v1/auth/login`: Authenticate and receive RS256 JWT access token.
- `GET /api/v1/auth/me`: Fetch profile of authenticated caller.

### Documents
- `POST /api/v1/documents`: Upload knowledge runbook; chunk & index into pgvector.
- `GET /api/v1/documents`: List ingested tenant documents.
- `GET /api/v1/documents/{id}/chunks`: Retrieve document chunks.

### Investigations
- `POST /api/v1/investigations`: Initialize new investigation session.
- `GET /api/v1/investigations`: List tenant investigations.
- `POST /api/v1/investigations/{id}/stream`: Real-time SSE streaming agent completion.

### Approvals (HITL)
- `GET /api/v1/approvals/pending`: List pending write operations requiring operator decision.
- `POST /api/v1/approvals/{id}/decide`: Approve or reject write operation.

### Admin & Telemetry
- `GET /api/v1/admin/audit-logs`: Inspect append-only audit log.
- `GET /api/v1/admin/telemetry`: View p95 latency, recall metrics, and model costs.
