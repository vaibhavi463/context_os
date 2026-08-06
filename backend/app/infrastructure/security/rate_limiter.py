import time

import redis.asyncio as redis
import structlog
from fastapi import HTTPException, status

logger = structlog.get_logger(__name__)


class RedisSlidingWindowRateLimiter:
    """
    Production Redis Sliding Window Rate Limiter.
    Tracks requests per user and per tenant using Redis sorted sets (ZSET).
    """

    def __init__(self, redis_client: redis.Redis | None = None) -> None:
        self.redis = redis_client

    async def check_rate_limit(
        self,
        key_prefix: str,
        identifier: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> None:
        if not self.redis:
            # Degrade gracefully if Redis is unavailable
            return

        now = time.time()
        clear_before = now - window_seconds
        redis_key = f"ratelimit:{key_prefix}:{identifier}"

        try:
            async with self.redis.pipeline(transaction=True) as pipe:
                # 1. Remove timestamps older than current window
                pipe.zremrangebyscore(redis_key, 0, clear_before)
                # 2. Count requests in current window
                pipe.zcard(redis_key)
                # 3. Add current timestamp
                pipe.zadd(redis_key, {str(now): now})
                # 4. Set TTL on key
                pipe.expire(redis_key, window_seconds + 5)
                results = await pipe.execute()

            request_count = results[1]
            if request_count >= max_requests:
                logger.warning(
                    "Rate limit exceeded",
                    identifier=identifier,
                    prefix=key_prefix,
                    count=request_count,
                    quota=max_requests
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit quota exceeded for {key_prefix}. Allowed: {max_requests} per {window_seconds}s.",
                    headers={"Retry-After": str(window_seconds)}
                )
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.error("Redis rate limiter check error", error=str(exc))
            # Fail open for system resilience if Redis connection fails
            return


rate_limiter = RedisSlidingWindowRateLimiter()
