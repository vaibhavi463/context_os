import pytest
import httpx
from unittest.mock import AsyncMock, patch

from app.infrastructure.security.security import decode_token
from app.infrastructure.external.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException
from app.infrastructure.security.rate_limiter import RedisSlidingWindowRateLimiter
from app.mcp_server.guards.rbac_guard import RBACGuard, ScopePermissionDeniedException


@pytest.mark.asyncio
async def test_invalid_jwt_decoding_failure():
    assert decode_token("invalid.jwt.token.string") is None
    assert decode_token("malformed_bearer_token") is None


@pytest.mark.asyncio
async def test_unauthorized_tool_execution_rejection():
    guard = RBACGuard()
    # Read-only user trying to invoke write tool
    with pytest.raises(ScopePermissionDeniedException):
        guard.validate_tool_access(user_role="read_only", required_scope="ops:write")


@pytest.mark.asyncio
async def test_external_api_failure_and_circuit_breaker_open():
    cb = CircuitBreaker("failure_test", failure_threshold=1, recovery_timeout=60.0)

    async def _failing_http_call():
        raise httpx.HTTPStatusError("500 Server Error", request=AsyncMock(), response=AsyncMock(status_code=500))

    # First call triggers failure threshold
    with pytest.raises(httpx.HTTPStatusError):
        await cb.call(_failing_http_call)

    assert cb.state == "OPEN"

    # Subsequent call rejected immediately by CircuitBreaker
    with pytest.raises(CircuitBreakerOpenException):
        await cb.call(_failing_http_call)


@pytest.mark.asyncio
async def test_redis_unavailability_graceful_failopen():
    # Test rate limiter fails open if Redis throws connection error
    mock_failing_redis = AsyncMock()
    mock_failing_redis.pipeline.side_effect = Exception("Redis Connection Refused")

    limiter = RedisSlidingWindowRateLimiter(redis_client=mock_failing_redis)
    # Should not raise exception (fails open for high availability)
    await limiter.check_rate_limit("test_prefix", "user_101")
