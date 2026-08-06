from typing import Any

from app.models.domain_models import AuditLog, User
from sqlalchemy.ext.asyncio import AsyncSession


class AuditLogger:
    @staticmethod
    async def log_action(
        db: AsyncSession,
        user: User,
        action: str,
        resource_type: str,
        resource_id: str,
        correlation_id: str,
        payload: dict[str, Any] | None = None,
        ip_address: str | None = None
    ) -> AuditLog:
        audit = AuditLog(
            tenant_id=user.tenant_id,
            actor_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            correlation_id=correlation_id,
            payload=payload or {},
            ip_address=ip_address
        )
        db.add(audit)
        await db.commit()
        await db.refresh(audit)
        return audit


audit_logger = AuditLogger()
