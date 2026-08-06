from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.infrastructure.security.rate_limiter import RedisSlidingWindowRateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_exceeded():
    mock_redis = MagicMock()
    mock_pipeline = AsyncMock()
    mock_pipeline.execute.return_value = [None, 105, None, None]
    mock_pipeline_ctx = MagicMock()
    mock_pipeline_ctx.__aenter__.return_value = mock_pipeline
    mock_pipeline_ctx.__aexit__.return_value = None
    mock_redis.pipeline.return_value = mock_pipeline_ctx

    limiter = RedisSlidingWindowRateLimiter(redis_client=mock_redis)

    with pytest.raises(HTTPException) as exc_info:
        await limiter.check_rate_limit("test_user", "usr_123", max_requests=100, window_seconds=60)

    assert exc_info.value.status_code == 429
    assert "Rate limit quota exceeded" in exc_info.value.detail
