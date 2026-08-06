import redis.asyncio as redis
import structlog
from fastapi import Header, HTTPException, status

logger = structlog.get_logger(__name__)


class RedisIdempotencyEngine:
    """
    Redis Distributed Lock & Request Idempotency Engine.
    Uses SETNX with TTL to prevent duplicate processing of mutation requests.
    """

    def __init__(self, redis_client: redis.Redis | None = None) -> None:
        self.redis = redis_client

    async def acquire_idempotency_lock(
        self,
        idempotency_key: str | None,
        tenant_id: str = "default",
        lock_ttl_seconds: int = 120
    ) -> str | None:
        if not idempotency_key or not self.redis:
            return None

        key = f"idempotency:{tenant_id}:{idempotency_key}"
        acquired = await self.redis.set(key, "PROCESSING", nx=True, ex=lock_ttl_seconds)
        if not acquired:
            logger.warning("Duplicate request blocked by Idempotency Engine", key=idempotency_key)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Duplicate request detected for Idempotency-Key '{idempotency_key}'. Request is already processing or completed."
            )
        return key


idempotency_engine = RedisIdempotencyEngine()


async def verify_idempotency_header(
    idempotency_key: str | None = Header(None, alias="Idempotency-Key")
) -> str | None:
    return idempotency_key
