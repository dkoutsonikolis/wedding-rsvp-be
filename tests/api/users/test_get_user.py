import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__get_user__bearer_token_from_login(client: AsyncClient):
    # Arrange
    await client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": "password123"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # Act
    response = await client.get("/api/v1/user", headers=headers)
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test__get_user__no_authorization_header(client: AsyncClient):
    # Arrange
    url = "/api/v1/user"
    # Act
    response = await client.get(url)
    # Assert
    assert response.status_code == 403


@pytest.mark.asyncio
async def test__get_user__malformed_jwt(client: AsyncClient):
    # Arrange
    headers = {"Authorization": "Bearer not-a-real-jwt"}
    # Act
    response = await client.get("/api/v1/user", headers=headers)
    # Assert
    assert response.status_code == 401
