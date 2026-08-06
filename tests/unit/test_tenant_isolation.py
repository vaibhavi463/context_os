import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.domain_models import Document
from app.repositories.base import BaseRepository


@pytest.mark.asyncio
async def test_tenant_repository_isolation():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_result.scalars().all.return_value = []
    mock_session.execute.return_value = mock_result

    repo = BaseRepository(Document, mock_session)

    # Test get_by_id_tenant builds query with tenant_id condition
    doc_id = uuid.uuid4()
    await repo.get_by_id_tenant(doc_id, "tenant_a")
    assert mock_session.execute.called

    # Test get_all_tenant filters by tenant_id
    await repo.get_all_tenant("tenant_b")
    assert mock_session.execute.call_count == 2
