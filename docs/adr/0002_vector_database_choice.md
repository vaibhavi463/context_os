# ADR 0002: Choice of PostgreSQL 16 pgvector for Hybrid Search

## Status
Accepted

## Context
ContextOS requires high-speed vector embedding storage, cosine distance similarity search, and hybrid retrieval combined with Full-Text Search (FTS) while maintaining strict tenant isolation.

## Decision
We select `pgvector` extension for PostgreSQL 16 using HNSW (`m=16, ef_construction=64`) cosine distance indexing combined with PostgreSQL native `tsvector` FTS via Reciprocal Rank Fusion (RRF $k=60$).

## Consequences
- Guarantees zero data synchronization latency between relational metadata and vector embeddings.
- Enables native PostgreSQL Row-Level Security (RLS) enforcement on vector queries.
