# ContextOS Security Guide

## Security Model
1. **OAuth2 / RS256 JWT Authentication**: Short-lived access tokens (15m expiry).
2. **Server-Side RBAC**: Role enforcement via `RequireRole` dependencies (`admin`, `ops_engineer`, `support_engineer`, `read_only`).
3. **Prompt Injection Guard**: Retrieved chunks are wrapped within `<untrusted_evidence>` tags. Model outputs cannot directly bypass tool scope authorization.
4. **Human-in-the-Loop (HITL) Gate**: Write operations issue HMAC-SHA256 signed JWT approval tokens incorporating argument hashes. Single-use execution enforced via Redis `SETNX` distributed locks.
5. **Multi-Tenancy Isolation**: Enforced at DB level using PostgreSQL Row-Level Security (RLS).
