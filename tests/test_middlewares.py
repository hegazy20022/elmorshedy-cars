import pytest


@pytest.mark.asyncio
async def test_health_not_rate_limited(client):
    response = await client.get("/health")
    assert response.status_code == 200
