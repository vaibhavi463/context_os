# Changelog

All notable changes to **ContextOS** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-08-06

### Added
- **RAG & Hybrid Search Engine**: Reciprocal Rank Fusion (RRF $k=60$) combining pgvector HNSW cosine search with PostgreSQL Full-Text Search.
- **Model Context Protocol (MCP) FastMCP Server**: Bounded operational tool catalog (4 Read, 2 Write) with RBAC scope enforcer.
- **Human-in-the-Loop (HITL) Security Gate**: Cryptographic HMAC-signed approval token generation for write actions.
- **Resilient External HTTP Client**: `ResilientHTTPClient` featuring `CircuitBreaker` states (`CLOSED`, `OPEN`, `HALF_OPEN`) and `tenacity` retries.
- **Multi-Turn Persistent Investigation**: Database persistence in `investigations` table with sliding context window token pruning.
- **Redis Sliding Window Rate Limiter**: Per-user and per-tenant request quota protection returning HTTP 429 status.
- **Redis Idempotency Engine**: `Idempotency-Key` write request protection backed by Redis distributed locks (`SETNX`).
- **Telemetry & Monitoring**: OpenTelemetry distributed tracing, Prometheus exporter metrics, and Grafana dashboard JSON specs.
- **AI Evaluation Suite**: Automated Recall@K, Tool Choice Precision, and Citation Precision benchmark script.
- **Locust Load Harness**: Performance benchmark harness measuring throughput RPS, p50, and p95 latency.
- **Production Hardening**: Security audit tests, OWASP API Top 10 compliance, CycloneDX SBOM, and Disaster Recovery procedures.
