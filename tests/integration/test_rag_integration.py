import pytest
from app.domain.retrieval.services.chunker import chunker
from app.domain.agents.services.citation_builder import citation_builder


def test_chunking_and_citation_generation():
    text = (
        "ContextOS Knowledge Base - Operational Incident Runbook.\n"
        "Section 1: Database Connection Pool Exhaustion.\n"
        "When connection pool gets exhausted, check max_connections in postgresql.conf and active pgbouncer client sessions.\n"
        "Section 2: Rate Limit Overflow Remediation.\n"
        "Trigger account rate limit bucket reset via execute_account_remediation write tool after obtaining operator approval."
    )
    chunks = chunker.chunk_document(text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) >= 1
    assert "Database Connection Pool" in chunks[0] or "ContextOS" in chunks[0]

    # Test citation building
    mock_results = [
        {
            "document_title": "Incident_Runbook.md",
            "chunk_index": 0,
            "chunk_text": chunks[0],
            "similarity": 0.94,
        }
    ]
    context_str, citations = citation_builder.build_citations(mock_results)
    assert "[Doc:Incident_Runbook.md#Chunk:0]" in context_str
    assert len(citations) == 1
    assert citations[0]["document_title"] == "Incident_Runbook.md"
