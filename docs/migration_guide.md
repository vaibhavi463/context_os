# ContextOS v1.0.0 Migration & Operations Guide

## 1. Initial Database Provisioning
Run Alembic migrations to initialize the `vector` extension and database schema:
```bash
alembic upgrade head
```

## 2. Environment Variables Checklist
- `DATABASE_URL`: PostgreSQL connection string with `asyncpg` driver.
- `REDIS_URL`: Redis connection string for rate limiting & locks.
- `GEMINI_API_KEY`: Google Gemini API credentials.
- `JWT_SECRET_KEY`: Cryptographic signing secret for JWT access tokens and HITL approval tokens.
