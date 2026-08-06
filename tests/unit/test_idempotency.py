import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock

from app.infrastructure.security.idempotency import RedisIdempotencyEngine


@pytest.mark.asyncio
async def test_idempotency_lock_acquisition():
    mock_redis = AsyncMock()
    # Mock lock successfully acquired
    mock_redis.set.return_value = True

    engine = RedisIdempotencyEngine(redis_client=mock_redis)
    lock_key = await engine.acquire_idempotency_lock("ik_unique_101", "tenant_a")
    assert lock_key == "idempotency:tenant_a:ik_unique_101"


@pytest.mark.asyncio
async def test_idempotency_lock_duplicate_rejection():
    mock_redis = AsyncMock()
    # Mock lock failure (key already exists)
    mock_redis.set.return_value = False

    engine = RedisIdempotencyEngine(redis_client=mock_redis)
    with pytest.raises(HTTPException) as exc_info:
        await engine.acquire_idempotency_lock("ik_duplicate_202", "tenant_a")

    assert exc_info.value.status_code == 409
    assert "Duplicate request detected" in exc_info.value.detail
