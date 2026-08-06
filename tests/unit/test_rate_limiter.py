import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock

from app.infrastructure.security.rate_limiter import RedisSlidingWindowRateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_exceeded():
    mock_redis = AsyncMock()
    # Mock pipeline return where count exceeds quota
    mock_pipeline = AsyncMock()
    mock_pipeline.execute.return_value = [None, 105, None, None]
    mock_redis.pipeline.return_value.__aenter__.return_value = mock_pipeline

    limiter = RedisSlidingWindowRateLimiter(redis_client=mock_redis)

    with pytest.raises(HTTPException) as exc_info:
        await limiter.check_rate_limit("test_user", "usr_123", max_requests=100, window_seconds=60)

    assert exc_info.value.status_code == 429
    assert "Rate limit quota exceeded" in exc_info.value.detail
