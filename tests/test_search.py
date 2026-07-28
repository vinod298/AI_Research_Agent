import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_endpoint(async_client: AsyncClient):
    payload = {
        "query": "artificial intelligence neural networks",
        "top_k": 3,
        "search_type": "hybrid"
    }
    res = await async_client.post("/api/v1/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert "latency_ms" in data
    assert data["search_type"] == "hybrid"
