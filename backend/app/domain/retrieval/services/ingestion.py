import hashlib
import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.retrieval.services.chunker import RecursiveTextChunker
from app.infrastructure.llm.embeddings import embedding_service
from app.models.domain_models import Document, DocumentChunk, User
from app.schemas.documents import DocumentCreate


class IngestionService:
    def __init__(self) -> None:
        self.chunker = RecursiveTextChunker(chunk_size=512, chunk_overlap=64)

    async def ingest_document(
        self,
        db: AsyncSession,
        user: User,
        payload: DocumentCreate
    ) -> Document:
        content_bytes = payload.content.encode("utf-8")
        content_hash = hashlib.sha256(content_bytes).hexdigest()

        # Check existing document with same hash for tenant
        stmt = select(Document).where(
            Document.tenant_id == user.tenant_id,
            Document.content_hash == content_hash
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            return existing

        doc = Document(
            tenant_id=user.tenant_id,
            title=payload.title,
            source_url=payload.source_url,
            content_hash=content_hash,
            file_type=payload.file_type,
            metadata_json=payload.metadata
        )
        db.add(doc)
        await db.flush()

        text_chunks = self.chunker.split_text(payload.content)
        embeddings = await embedding_service.get_embeddings_batch(text_chunks)

        for idx, (chunk_text, emb) in enumerate(zip(text_chunks, embeddings)):
            chunk = DocumentChunk(
                document_id=doc.id,
                tenant_id=user.tenant_id,
                chunk_index=idx,
                content=chunk_text,
                embedding=emb,
                metadata_json={"title": payload.title, "chunk_index": idx}
            )
            db.add(chunk)

        await db.commit()
        await db.refresh(doc)
        return doc


ingestion_service = IngestionService()
