import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__public_client_config__returns_agent_message_limits(client: AsyncClient):
    # Arrange
    # Act
    response = await client.get("/api/v1/public/client-config")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["agent_anon_message_max_chars"] == 200
    assert data["agent_user_message_max_chars"] == 500
