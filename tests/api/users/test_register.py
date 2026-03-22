import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__register__unused_email(client: AsyncClient):
    # Arrange
    payload = {"email": "newuser@example.com", "password": "password123"}
    # Act
    response = await client.post("/api/v1/auth/register", json=payload)
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test__register__duplicate_email(client: AsyncClient):
    # Arrange
    payload = {"email": "dup@example.com", "password": "password123"}
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    # Act
    response = await client.post("/api/v1/auth/register", json=payload)
    # Assert
    assert response.status_code == 409


@pytest.mark.asyncio
async def test__register__password_below_min_length(client: AsyncClient):
    # Arrange
    payload = {"email": "short@example.com", "password": "short"}
    # Act
    response = await client.post("/api/v1/auth/register", json=payload)
    # Assert
    assert response.status_code == 422
