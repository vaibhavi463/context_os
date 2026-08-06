from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.approvals import router as approvals_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.investigations import router as investigations_router
from fastapi import APIRouter

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(approvals_router)
api_v1_router.include_router(investigations_router)
api_v1_router.include_router(admin_router)
