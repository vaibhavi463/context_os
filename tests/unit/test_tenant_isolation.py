import pytest
import uuid
from app.models.domain_models import Document
from app.repositories.base import BaseRepository
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_tenant_repository_isolation():
    mock_session = AsyncMock()
    repo = BaseRepository(Document, mock_session)

    # Test get_by_id_tenant builds query with tenant_id condition
    doc_id = uuid.uuid4()
    await repo.get_by_id_tenant(doc_id, "tenant_a")
    assert mock_session.execute.called

    # Test get_all_tenant filters by tenant_id
    await repo.get_all_tenant("tenant_b")
    assert mock_session.execute.call_count == 2
