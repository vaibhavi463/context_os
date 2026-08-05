# ContextOS Deployment Guide

## Docker Compose (Development)
```bash
docker compose up -d
alembic upgrade head
python scripts/seed_demo_data.py
```

## Production Deployment (AWS ECS Fargate)
- **API Gateway**: Multi-AZ ECS Fargate task running `backend/Dockerfile`.
- **Database**: AWS Aurora PostgreSQL 16 (Serverless v2 or Provisioned) with `pgvector`.
- **Cache**: AWS ElastiCache Redis 7 cluster.
- **Secrets**: AWS Secrets Manager storing `JWT_SECRET` and `GEMINI_API_KEY`.
