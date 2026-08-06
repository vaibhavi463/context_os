from collections.abc import Sequence
from typing import Annotated

from app.db.session import get_db
from app.domain.retrieval.services.ingestion import ingestion_service
from app.infrastructure.security.dependencies import RequireRole, get_current_user
from app.models.domain_models import Document, DocumentChunk, User
from app.schemas.documents import DocumentChunkResponse, DocumentCreate, DocumentResponse
from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    payload: DocumentCreate,
    current_user: Annotated[User, Depends(RequireRole(["ops_engineer", "admin", "support_engineer"]))],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> DocumentResponse:
    doc = await ingestion_service.ingest_document(db=db, user=current_user, payload=payload)
    
    count_stmt = select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == doc.id)
    chunk_count = (await db.execute(count_stmt)).scalar() or 0

    return DocumentResponse(
        id=doc.id,
        tenant_id=doc.tenant_id,
        title=doc.title,
        source_url=doc.source_url,
        content_hash=doc.content_hash,
        file_type=doc.file_type,
        metadata_json=doc.metadata_json,
        chunk_count=chunk_count,
        created_at=doc.created_at
    )


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> list[DocumentResponse]:
    stmt = select(Document).where(Document.tenant_id == current_user.tenant_id).order_by(Document.created_at.desc())
    docs = (await db.execute(stmt)).scalars().all()

    response: list[DocumentResponse] = []
    for doc in docs:
        count_stmt = select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == doc.id)
        chunk_count = (await db.execute(count_stmt)).scalar() or 0
        response.append(
            DocumentResponse(
                id=doc.id,
                tenant_id=doc.tenant_id,
                title=doc.title,
                source_url=doc.source_url,
                content_hash=doc.content_hash,
                file_type=doc.file_type,
                metadata_json=doc.metadata_json,
                chunk_count=chunk_count,
                created_at=doc.created_at
            )
        )
    return response


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkResponse])
async def get_document_chunks(
    document_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Sequence[DocumentChunk]:
    stmt = (
        select(DocumentChunk)
        .where(
            DocumentChunk.document_id == document_id,
            DocumentChunk.tenant_id == current_user.tenant_id
        )
        .order_by(DocumentChunk.chunk_index.asc())
    )
    chunks = (await db.execute(stmt)).scalars().all()
    return chunks
