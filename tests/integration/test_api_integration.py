import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_and_liveness_probes():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "service": "context-os-api"}

        ready_resp = await ac.get("/ready")
        assert ready_resp.status_code == 200

        live_resp = await ac.get("/live")
        assert live_resp.status_code == 200
