import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analytics_and_health_endpoints(async_client: AsyncClient):
    health_res = await async_client.get("/api/v1/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"

    metrics_res = await async_client.get("/api/v1/metrics")
    assert metrics_res.status_code == 200
    assert metrics_res.json()["uptime"] == "operational"

    analytics_res = await async_client.get("/api/v1/analytics")
    assert analytics_res.status_code == 200
    data = analytics_res.json()
    assert "metrics" in data
    assert "latency" in data
