import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__login__matching_registered_credentials(client: AsyncClient):
    # Arrange
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "password123"},
    )
    payload = {"email": "login@example.com", "password": "password123"}
    # Act
    response = await client.post("/api/v1/auth/login", json=payload)
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["expires_in"] == 30 * 60
    assert data["refresh_expires_in"] == 7 * 24 * 3600
    assert data["user"]["email"] == "login@example.com"
    assert "id" in data["user"]


@pytest.mark.asyncio
async def test__login__wrong_password_for_registered_email(client: AsyncClient):
    # Arrange
    await client.post(
        "/api/v1/auth/register",
        json={"email": "user2@example.com", "password": "password123"},
    )
    payload = {"email": "user2@example.com", "password": "wrong-password"}
    # Act
    response = await client.post("/api/v1/auth/login", json=payload)
    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test__login__email_not_registered(client: AsyncClient):
    # Arrange
    payload = {"email": "nobody@example.com", "password": "password123"}
    # Act
    response = await client.post("/api/v1/auth/login", json=payload)
    # Assert
    assert response.status_code == 401
