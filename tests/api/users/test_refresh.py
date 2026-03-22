import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__refresh__returns_new_pair_with_valid_refresh_token(client: AsyncClient):
    # Arrange
    await client.post(
        "/api/v1/auth/register",
        json={"email": "refresh@example.com", "password": "password123"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "refresh@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    refresh_token = login.json()["refresh_token"]
    # Act
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] != login.json()["access_token"]
    assert data["refresh_token"] != refresh_token
    assert data["user"]["email"] == "refresh@example.com"


@pytest.mark.asyncio
async def test__refresh__invalid_token(client: AsyncClient):
    # Arrange
    # Act
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "not-a-valid-jwt"},
    )
    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test__get_user__rejects_refresh_token_used_as_bearer(client: AsyncClient):
    # Arrange
    await client.post(
        "/api/v1/auth/register",
        json={"email": "bear@example.com", "password": "password123"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "bear@example.com", "password": "password123"},
    )
    refresh_token = login.json()["refresh_token"]
    # Act
    response = await client.get(
        "/api/v1/user",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    # Assert
    assert response.status_code == 401
