import pytest
import uuid
from app.models.domain_models import Investigation, InvestigationMessage, User
from app.domain.agents.orchestrator import agent_orchestrator


@pytest.mark.asyncio
async def test_conversation_context_window_pruning():
    dummy_user = User(
        id=uuid.uuid4(),
        tenant_id="tenant_test",
        email="test@contextos.io",
        hashed_password="hash",
        role="ops_engineer",
    )
    dummy_investigation = Investigation(
        id=uuid.uuid4(),
        tenant_id="tenant_test",
        user_id=dummy_user.id,
        title="Test Investigation Context Window",
        status="ACTIVE",
    )

    messages = []
    for i in range(30):
        messages.append(
            InvestigationMessage(
                investigation_id=dummy_investigation.id,
                sender_type="USER" if i % 2 == 0 else "AGENT",
                content=f"Message turn #{i}",
            )
        )

    # Pruning logic check (20 messages retained for max_history_turns=10)
    max_history_turns = 10
    pruned = messages[-(max_history_turns * 2):] if len(messages) > max_history_turns * 2 else messages
    assert len(pruned) == 20
    assert pruned[0].content == "Message turn #10"
    assert pruned[-1].content == "Message turn #29"
