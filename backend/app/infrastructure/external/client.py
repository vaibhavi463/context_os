from typing import Any, TypeVar
from collections.abc import Callable, Awaitable
import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.infrastructure.external.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class ResilientHTTPClient:
    """
    Enterprise Resilient HTTP Client wrapping HTTPX with Circuit Breaker,
    exponential backoff retries, timeouts, and fallback callbacks.
    """

    def __init__(
        self,
        service_name: str,
        timeout: float = 5.0,
        max_retries: int = 3,
        failure_threshold: int = 3,
        recovery_timeout: float = 15.0,
    ) -> None:
        self.service_name = service_name
        self.timeout = timeout
        self.max_retries = max_retries
        self.circuit_breaker = CircuitBreaker(
            name=service_name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=httpx.HTTPError,
        )

    async def get_json(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        fallback: Callable[[], dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        async def _execute_http_request() -> dict[str, Any]:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()  # type: ignore[no-any-return]

        @retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=0.5, min=0.5, max=2.0),
            retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError)),
            reraise=True,
        )
        async def _retrying_call() -> dict[str, Any]:
            return await self.circuit_breaker.call(_execute_http_request)

        try:
            return await _retrying_call()
        except (httpx.HTTPError, CircuitBreakerOpenException) as exc:
            logger.error(
                f"ResilientHTTPClient '{self.service_name}' request failed",
                url=url,
                error=str(exc),
                fallback_used=fallback is not None,
            )
            if fallback:
                return fallback()
            raise


class ServiceClientRegistry:
    """Registry holding resilient HTTP clients per downstream service."""

    def __init__(self) -> None:
        self._clients: dict[str, ResilientHTTPClient] = {}

    def get_client(self, service_name: str, timeout: float = 5.0) -> ResilientHTTPClient:
        if service_name not in self._clients:
            self._clients[service_name] = ResilientHTTPClient(service_name=service_name, timeout=timeout)
        return self._clients[service_name]


client_registry = ServiceClientRegistry()
