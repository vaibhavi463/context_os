import pytest
import httpx
from unittest.mock import AsyncMock, patch

from app.infrastructure.external.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException
from app.infrastructure.external.client import ResilientHTTPClient


@pytest.mark.asyncio
async def test_circuit_breaker_states():
    cb = CircuitBreaker("test_cb", failure_threshold=2, recovery_timeout=0.1)

    async def _failing_fn():
        raise httpx.ConnectError("Connection refused")

    # 1. Closed state initially
    assert cb.state == "CLOSED"

    # First failure
    with pytest.raises(httpx.ConnectError):
        await cb.call(_failing_fn)
    assert cb.state == "CLOSED"
    assert cb.failure_count == 1

    # Second failure -> triggers OPEN
    with pytest.raises(httpx.ConnectError):
        await cb.call(_failing_fn)
    assert cb.state == "OPEN"

    # Attempt call while OPEN -> throws CircuitBreakerOpenException immediately
    with pytest.raises(CircuitBreakerOpenException):
        await cb.call(_failing_fn)


@pytest.mark.asyncio
async def test_resilient_http_client_fallback():
    client = ResilientHTTPClient("test_service", timeout=1.0, max_retries=1, failure_threshold=1)

    def fallback_fn():
        return {"status": "fallback_triggered"}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.ConnectError("Service Unavailable")

        result = await client.get_json("https://api.example.com/data", fallback=fallback_fn)
        assert result == {"status": "fallback_triggered"}
