import uuid
from dataclasses import dataclass
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from app.infrastructure.llm.embeddings import embedding_service
from app.models.domain_models import DocumentChunk, Document


@dataclass
class SearchResult:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_title: str
    chunk_index: int
    content: str
    rrf_score: float
    vector_rank: int | None
    fts_rank: int | None


class HybridSearchService:
    def __init__(self, rrf_k: int = 60) -> None:
        self.rrf_k = rrf_k

    async def search(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        query: str,
        top_k: int = 5
    ) -> list[SearchResult]:
        if not query or not query.strip():
            return []

        query_vector = await embedding_service.get_embedding(query)
        query_vector_str = f"[{','.join(str(x) for x in query_vector)}]"

        # 1. pgvector Cosine Similarity Search
        vector_sql = text("""
            SELECT c.id, c.document_id, d.title, c.chunk_index, c.content,
                   (c.embedding <=> :vec::vector) AS distance
            FROM document_chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE c.tenant_id = :tenant_id
            ORDER BY distance ASC
            LIMIT 20;
        """)
        vector_res = await db.execute(vector_sql, {"vec": query_vector_str, "tenant_id": tenant_id})
        vector_rows = vector_res.fetchall()

        # Map chunk_id to vector rank (1-indexed)
        vector_ranks: dict[uuid.UUID, int] = {}
        chunk_data: dict[uuid.UUID, dict] = {}
        for rank, row in enumerate(vector_rows, start=1):
            cid = row[0]
            vector_ranks[cid] = rank
            chunk_data[cid] = {
                "chunk_id": cid,
                "document_id": row[1],
                "document_title": row[2],
                "chunk_index": row[3],
                "content": row[4]
            }

        # 2. Full-Text Search (tsvector / ts_rank_cd)
        fts_sql = text("""
            SELECT c.id, c.document_id, d.title, c.chunk_index, c.content,
                   ts_rank_cd(c.tsv_content, plainto_tsquery('english', :query)) AS rank_score
            FROM document_chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE c.tenant_id = :tenant_id 
              AND c.tsv_content @@ plainto_tsquery('english', :query)
            ORDER BY rank_score DESC
            LIMIT 20;
        """)
        fts_res = await db.execute(fts_sql, {"query": query, "tenant_id": tenant_id})
        fts_rows = fts_res.fetchall()

        fts_ranks: dict[uuid.UUID, int] = {}
        for rank, row in enumerate(fts_rows, start=1):
            cid = row[0]
            fts_ranks[cid] = rank
            if cid not in chunk_data:
                chunk_data[cid] = {
                    "chunk_id": cid,
                    "document_id": row[1],
                    "document_title": row[2],
                    "chunk_index": row[3],
                    "content": row[4]
                }

        # 3. Reciprocal Rank Fusion (RRF) Calculation
        rrf_scores: dict[uuid.UUID, float] = {}
        all_chunk_ids = set(vector_ranks.keys()).union(set(fts_ranks.keys()))

        for cid in all_chunk_ids:
            score = 0.0
            if cid in vector_ranks:
                score += 1.0 / (self.rrf_k + vector_ranks[cid])
            if cid in fts_ranks:
                score += 1.0 / (self.rrf_k + fts_ranks[cid])
            rrf_scores[cid] = score

        # Sort by RRF score descending
        sorted_ids = sorted(all_chunk_ids, key=lambda x: rrf_scores[x], reverse=True)[:top_k]

        results: list[SearchResult] = []
        for cid in sorted_ids:
            meta = chunk_data[cid]
            results.append(
                SearchResult(
                    chunk_id=cid,
                    document_id=meta["document_id"],
                    document_title=meta["document_title"],
                    chunk_index=meta["chunk_index"],
                    content=meta["content"],
                    rrf_score=rrf_scores[cid],
                    vector_rank=vector_ranks.get(cid),
                    fts_rank=fts_ranks.get(cid)
                )
            )

        return results


hybrid_search_service = HybridSearchService()
