from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any


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
    def build_citations(search_results: Sequence[Any]) -> tuple[str, list[dict]]:
        citations: list[dict] = []
        formatted_context_blocks: list[str] = []

        for idx, res in enumerate(search_results, start=1):
            if isinstance(res, dict):
                doc_title = res.get("document_title", "Untitled")
                chunk_idx = res.get("chunk_index", 0)
                chunk_id = str(res.get("chunk_id", ""))
                doc_id = str(res.get("document_id", ""))
                content = res.get("content") or res.get("chunk_text", "")
            else:
                doc_title = res.document_title
                chunk_idx = res.chunk_index
                chunk_id = str(res.chunk_id)
                doc_id = str(res.document_id)
                content = res.content

            ref_tag = f"[Doc:{doc_title}#Chunk:{chunk_idx}]"
            citation_obj = {
                "chunk_id": chunk_id,
                "document_id": doc_id,
                "document_title": doc_title,
                "chunk_index": chunk_idx,
                "snippet": content[:200] + "..." if len(content) > 200 else content,
                "reference_tag": ref_tag,
            }
            citations.append(citation_obj)

            block = (
                f"Source {idx}: {ref_tag}\n"
                f"Title: {doc_title}\n"
                f"Content:\n{content}\n"
            )
            formatted_context_blocks.append(block)

        context_str = "\n---\n".join(formatted_context_blocks)
        return context_str, citations


citation_builder = CitationBuilder()
