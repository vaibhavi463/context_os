from collections.abc import Sequence
from dataclasses import dataclass

from app.domain.retrieval.services.hybrid_search import SearchResult


@dataclass
class Citation:
    chunk_id: str
    document_id: str
    document_title: str
    chunk_index: int
    snippet: str
    reference_tag: str


class CitationBuilder:
    @staticmethod
    def build_citations(search_results: Sequence[SearchResult]) -> tuple[str, list[dict]]:
        citations: list[dict] = []
        formatted_context_blocks: list[str] = []

        for idx, res in enumerate(search_results, start=1):
            ref_tag = f"[Doc:{res.document_title}#Chunk:{res.chunk_index}]"
            citation_obj = {
                "chunk_id": str(res.chunk_id),
                "document_id": str(res.document_id),
                "document_title": res.document_title,
                "chunk_index": res.chunk_index,
                "snippet": res.content[:200] + "...",
                "reference_tag": ref_tag
            }
            citations.append(citation_obj)

            block = (
                f"Source {idx}: {ref_tag}\n"
                f"Title: {res.document_title}\n"
                f"Content:\n{res.content}\n"
            )
            formatted_context_blocks.append(block)

        context_str = "\n---\n".join(formatted_context_blocks)
        return context_str, citations


citation_builder = CitationBuilder()
