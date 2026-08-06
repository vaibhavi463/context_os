import time
import structlog
from typing import Any, TypeVar
from collections.abc import Callable, Awaitable

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class CircuitBreakerOpenException(Exception):
    """Raised when an external call is attempted while the circuit is OPEN."""


class CircuitBreaker:
    """
    Production-grade Circuit Breaker implementing State Machine:
    CLOSED -> OPEN (after failure_threshold reached) -> HALF_OPEN (after recovery_timeout) -> CLOSED / OPEN
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,
        recovery_timeout: float = 30.0,
        expected_exception: type[Exception] = Exception,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_count: int = 0
        self.last_state_change: float = time.time()
        self.last_failure_time: float = 0.0

    async def call(self, func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any) -> T:
        now = time.time()

        if self.state == "OPEN":
            if now - self.last_state_change >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                self.last_state_change = now
                logger.info(f"CircuitBreaker '{self.name}' transitioned from OPEN to HALF_OPEN")
            else:
                logger.warning(
                    f"CircuitBreaker '{self.name}' is OPEN. Rejecting call.",
                    remaining_cooldown=round(self.recovery_timeout - (now - self.last_state_change), 2),
                )
                raise CircuitBreakerOpenException(f"Circuit breaker '{self.name}' is OPEN")

        try:
            result = await func(*args, **kwargs)
            if self.state in ("HALF_OPEN", "OPEN"):
                self.state = "CLOSED"
                self.failure_count = 0
                self.last_state_change = now
                logger.info(f"CircuitBreaker '{self.name}' call succeeded. Transitioned to CLOSED.")
            return result
        except self.expected_exception as exc:
            self.failure_count += 1
            self.last_failure_time = now
            logger.error(
                f"CircuitBreaker '{self.name}' caught failure",
                failure_count=self.failure_count,
                threshold=self.failure_threshold,
                error=str(exc),
            )
            if self.failure_count >= self.failure_threshold or self.state == "HALF_OPEN":
                self.state = "OPEN"
                self.last_state_change = now
                logger.error(f"CircuitBreaker '{self.name}' threshold reached. Transitioned to OPEN.")
            raise
