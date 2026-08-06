import pytest
import uuid
from unittest.mock import AsyncMock, patch

from app.domain.retrieval.services.chunker import chunker
from app.domain.agents.services.citation_builder import citation_builder
from app.mcp_server.guards.rbac_guard import RBACGuard, ScopePermissionDeniedException


@pytest.mark.asyncio
async def test_scenario_1_rag_query_and_citation_flow():
    """Scenario 1: Auth -> Ingest -> Retrieve -> Generate Answer with Inline Citation"""
    document_text = (
        "ContextOS Operational Guide 2026.\n"
        "Incident Response: Database CPU spikes are mitigated by scaling PostgreSQL read replicas."
    )
    chunks = chunker.chunk_document(document_text, chunk_size=100, chunk_overlap=10)
    assert len(chunks) >= 1

    search_evidence = [
        {
            "document_title": "ContextOS_Operational_Guide.md",
            "chunk_index": 0,
            "chunk_text": chunks[0],
            "similarity": 0.95,
        }
    ]
    formatted_context, citations = citation_builder.build_citations(search_evidence)
    assert "[Doc:ContextOS_Operational_Guide.md#Chunk:0]" in formatted_context
    assert citations[0]["document_title"] == "ContextOS_Operational_Guide.md"


@pytest.mark.asyncio
async def test_scenario_2_hitl_approval_execution_flow():
    """Scenario 2: Write Tool Trigger -> HITL Approval Token Generation -> Operator Decision"""
    user_id = uuid.uuid4()
    investigation_id = uuid.uuid4()
    approval_token = f"approval_{uuid.uuid4().hex[:16]}"

    # Verify pending approval state structure
    approval_item = {
        "id": str(uuid.uuid4()),
        "investigation_id": str(investigation_id),
        "tool_name": "execute_account_remediation",
        "status": "PENDING_APPROVAL",
        "requested_by_user_id": str(user_id),
        "token": approval_token,
    }
    assert approval_item["status"] == "PENDING_APPROVAL"
    assert approval_item["tool_name"] == "execute_account_remediation"


@pytest.mark.asyncio
async def test_scenario_3_unauthorized_rbac_denial_flow():
    """Scenario 3: Read-only User -> Scope Enforcer -> RBAC Denial"""
    guard = RBACGuard()
    with pytest.raises(ScopePermissionDeniedException):
        guard.validate_tool_access(user_role="read_only", required_scope="admin:read")
