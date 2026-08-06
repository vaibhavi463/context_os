# ADR 0005: Redis Sliding Window Rate Limiting & Idempotency

## Status
Accepted

## Context
API endpoints must be protected against denial-of-service, abusive user traffic, and duplicate mutation execution.

## Decision
We implement a Redis-backed Sliding Window Rate Limiter using atomic ZSET pipelines and a Redis Distributed Lock (`SETNX`) Idempotency Engine for write operations.

## Consequences
- Returns HTTP 429 status with `Retry-After` headers on quota overflow.
- Fails open gracefully if Redis connection is unavailable to preserve core system availability.
