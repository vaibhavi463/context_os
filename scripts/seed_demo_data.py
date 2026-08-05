import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.models.domain_models import Tenant, User, Document, DocumentChunk
from app.infrastructure.security.security import get_password_hash
from app.infrastructure.llm.embeddings import embedding_service

sample_runbook = """# Database Primary Pool Troubleshooting Runbook

## Symptoms & High CPU Utilization
High CPU utilization on the PostgreSQL Primary DB Pool occurs primarily when unindexed vector similarity queries (cosine distance) or un-tuned full-text search queries spike concurrently.

## Emergency Remediation Steps
1. Verify active connection pool saturation.
2. If rate limits are exceeded for Enterprise Tenant `ACC-9941`, invoke tool `execute_account_remediation` with `action_type: RESET_RATE_LIMIT`.
3. Check HNSW index parameters (m=16, ef_construction=64).
"""

async def seed_data() -> None:
    print("Seeding ContextOS demo database...")
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create Tenant
        tenant = Tenant(id=uuid.uuid4(), name="Acme Operations Corp", slug="acme-corp")
        session.add(tenant)
        await session.flush()

        # Create Admin & Ops Users
        admin_user = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="admin@contextos.io",
            hashed_password=get_password_hash("AdminPass123!"),
            full_name="System Administrator",
            role="admin"
        )
        ops_user = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="ops@contextos.io",
            hashed_password=get_password_hash("OpsPass123!"),
            full_name="Operations Lead",
            role="ops_engineer"
        )
        session.add_all([admin_user, ops_user])
        await session.flush()

        # Create Document & Chunk
        doc = Document(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            title="Database Runbook.md",
            source_url="https://wiki.contextos.io/runbooks/db",
            content_hash="seed_hash_001",
            file_type="text/markdown",
            metadata_json={"author": "DevOps Team"}
        )
        session.add(doc)
        await session.flush()

        emb = await embedding_service.get_embedding(sample_runbook)
        chunk = DocumentChunk(
            id=uuid.uuid4(),
            document_id=doc.id,
            tenant_id=tenant.id,
            chunk_index=0,
            content=sample_runbook,
            embedding=emb,
            metadata_json={"title": doc.title}
        )
        session.add(chunk)

        await session.commit()
        print("Seeding completed successfully!")
        print(f"Created Tenant: {tenant.name} ({tenant.id})")
        print(f"Created Admin: {admin_user.email} / AdminPass123!")
        print(f"Created Ops Engineer: {ops_user.email} / OpsPass123!")
        print("Indexed 1 Document Chunk into pgvector.")

if __name__ == "__main__":
    asyncio.run(seed_data())
