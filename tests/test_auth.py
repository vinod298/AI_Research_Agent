import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_user(async_client: AsyncClient):
    # Register user
    reg_payload = {
        "email": "researcher_test@enterprise.ai",
        "username": "test_researcher",
        "password": "SecurePassword123!",
        "full_name": "Test Researcher",
        "role": "researcher"
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert data["email"] == "researcher_test@enterprise.ai"
    assert data["username"] == "test_researcher"

    # Login user
    login_payload = {
        "username_or_email": "test_researcher",
        "password": "SecurePassword123!"
    }
    login_res = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
