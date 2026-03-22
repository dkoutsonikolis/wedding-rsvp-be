import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__create_message__non_empty_body(client: AsyncClient):
    # Arrange
    payload = {"content": "Test message"}
    # Act
    response = await client.post("/api/v1/messages/", json=payload)
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Test message"
    assert "id" in data
    assert data["id"] is not None
    assert "created_at" in data


@pytest.mark.asyncio
async def test__create_message__empty_json_body(client: AsyncClient):
    # Arrange
    payload = {}
    # Act
    response = await client.post("/api/v1/messages/", json=payload)
    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test__create_message__content_not_string(client: AsyncClient):
    # Arrange
    payload = {"content": 123}
    # Act
    response = await client.post("/api/v1/messages/", json=payload)
    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test__create_message__empty_string_content(client: AsyncClient):
    # Arrange
    payload = {"content": ""}
    # Act
    response = await client.post("/api/v1/messages/", json=payload)
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == ""
