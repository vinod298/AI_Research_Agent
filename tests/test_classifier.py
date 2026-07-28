import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_tensorflow_classifier_endpoint(async_client: AsyncClient):
    payload = {
        "text": "Deep learning convolutional neural networks for computer vision image segmentation and object detection."
    }
    res = await async_client.post("/api/v1/classify", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "predicted_category" in data
    assert "confidence" in data
    assert len(data["all_scores"]) == 10
