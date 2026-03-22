import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__get_health__root_path(client: AsyncClient):
    # Arrange
    url = "/health"
    # Act
    response = await client.get(url)
    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test__get_ready__with_test_session(client: AsyncClient):
    # Arrange
    url = "/ready"
    # Act
    response = await client.get(url)
    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
