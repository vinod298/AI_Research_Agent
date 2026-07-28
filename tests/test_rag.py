import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_rag_endpoint(async_client: AsyncClient):
    payload = {
        "question": "What is the proposed architecture and empirical results?",
        "top_k": 3,
        "llm_provider": "mock"
    }
    res = await async_client.post("/api/v1/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "citations" in data
    assert "session_id" in data
    assert data["llm_provider"] == "mock"
