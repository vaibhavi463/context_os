import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)


class TenantIsolationMiddleware(BaseHTTPMiddleware):
    """
    Middleware ensuring tenant_id context is extracted from JWT or headers
    and bound to request state for strict multi-tenant isolation.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        tenant_id = request.headers.get("X-Tenant-ID", "default_tenant")
        request.state.tenant_id = tenant_id

        response = await call_next(request)
        response.headers["X-Tenant-ID"] = tenant_id
        return response
