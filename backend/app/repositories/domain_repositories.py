import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain_models import (
    AuditLog,
    Document,
    DocumentChunk,
    Investigation,
    InvestigationMessage,
    PendingApproval,
    Tenant,
    User,
)
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email, User.is_active == True)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_or_create_tenant(self, name: str, slug: str) -> Tenant:
        stmt = select(Tenant).where(Tenant.slug == slug)
        res = await self.session.execute(stmt)
        tenant = res.scalar_one_or_none()
        if not tenant:
            tenant = Tenant(name=name, slug=slug)
            self.session.add(tenant)
            await self.session.flush()
        return tenant


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Document, session)

    async def get_by_hash(self, tenant_id: uuid.UUID, content_hash: str) -> Document | None:
        stmt = select(Document).where(
            Document.tenant_id == tenant_id,
            Document.content_hash == content_hash
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_tenant(self, tenant_id: uuid.UUID) -> Sequence[Document]:
        stmt = (
            select(Document)
            .where(Document.tenant_id == tenant_id)
            .order_by(Document.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def count_chunks(self, document_id: uuid.UUID) -> int:
        stmt = select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == document_id)
        res = await self.session.execute(stmt)
        return res.scalar() or 0


class InvestigationRepository(BaseRepository[Investigation]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Investigation, session)

    async def list_by_tenant(self, tenant_id: uuid.UUID) -> Sequence[Investigation]:
        stmt = (
            select(Investigation)
            .where(Investigation.tenant_id == tenant_id)
            .order_by(Investigation.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_messages(self, investigation_id: uuid.UUID) -> Sequence[InvestigationMessage]:
        stmt = (
            select(InvestigationMessage)
            .where(InvestigationMessage.investigation_id == investigation_id)
            .order_by(InvestigationMessage.created_at.asc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()


class ApprovalRepository(BaseRepository[PendingApproval]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(PendingApproval, session)

    async def get_pending_by_tenant(self, tenant_id: uuid.UUID) -> Sequence[PendingApproval]:
        stmt = (
            select(PendingApproval)
            .where(
                PendingApproval.tenant_id == tenant_id,
                PendingApproval.status == "PENDING"
            )
            .order_by(PendingApproval.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AuditLog, session)

    async def list_by_tenant(self, tenant_id: uuid.UUID, limit: int = 50) -> Sequence[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
