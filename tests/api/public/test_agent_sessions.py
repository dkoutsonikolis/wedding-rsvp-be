import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__create_public_agent_session__returns_token_and_quota(client: AsyncClient):
    # Arrange
    url = "/api/v1/public/agent/sessions"
    # Act
    response = await client.post(url)
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "session_token" in data
    assert len(data["session_token"]) >= 32
    assert data["interactions_remaining"] == 3
    assert data["config"] == {}
