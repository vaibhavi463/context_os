import time
from collections.abc import Callable

import structlog
from fastapi import Request, Response
from prometheus_client import Counter, Histogram

logger = structlog.get_logger()

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Latency in seconds",
    ["method", "endpoint", "status"]
)

TOOL_EXECUTION_COUNTER = Counter(
    "tool_execution_total",
    "Total Tool Executions",
    ["tool_name", "status"]
)

LLM_COST_COUNTER = Counter(
    "estimated_llm_cost_usd_total",
    "Total Estimated LLM Token Cost in USD",
    ["provider", "model"]
)


async def prometheus_telemetry_middleware(request: Request, call_next: Callable) -> Response:
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    endpoint = request.url.path
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).observe(duration)

    return response
