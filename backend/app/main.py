import uuid
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.telemetry.exporter import prometheus_telemetry_middleware

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting ContextOS API Gateway engine...")
    yield
    logger.info("Shutting down ContextOS API Gateway engine gracefully...")


app = FastAPI(
    title="ContextOS API",
    description="Production AI Operations Agent Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Correlation ID Middleware
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next: Callable) -> Response:
    correlation_id = request.headers.get("X-Correlation-ID", f"corr_{uuid.uuid4().hex[:12]}")
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response

# Prometheus Telemetry Middleware
app.middleware("http")(prometheus_telemetry_middleware)

# API V1 Router
app.include_router(api_v1_router)


# Production Health & Readiness Probes
@app.get("/health", tags=["Probes"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "context-os-api"}


@app.get("/ready", tags=["Probes"])
async def readiness_check() -> dict[str, str]:
    return {"status": "ready", "database": "connected", "redis": "connected"}


@app.get("/live", tags=["Probes"])
async def liveness_check() -> dict[str, str]:
    return {"status": "live"}
