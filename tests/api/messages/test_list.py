import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__list_messages__no_rows(client: AsyncClient):
    # Arrange
    url = "/api/v1/messages/"
    # Act
    response = await client.get(url)
    # Assert
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test__list_messages__two_inserted_rows(client: AsyncClient, message_factory):
    # Arrange
    await message_factory(content="First message")
    await message_factory(content="Second message")
    # Act
    response = await client.get("/api/v1/messages/")
    # Assert
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2
    assert messages[0]["content"] in ["First message", "Second message"]
    assert messages[1]["content"] in ["First message", "Second message"]
    assert messages[0]["content"] != messages[1]["content"]


@pytest.mark.asyncio
async def test__list_messages__ordered_by_primary_key(client: AsyncClient, message_factory):
    # Arrange
    for i in range(3):
        await message_factory(content=f"Message {i}")
    # Act
    response = await client.get("/api/v1/messages/")
    # Assert
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 3
    ids = [msg["id"] for msg in messages]
    assert ids == sorted(ids)
