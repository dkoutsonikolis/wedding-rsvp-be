import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__public_agent_turn__decrements_remaining(client: AsyncClient):
    # Arrange
    session = await client.post("/api/v1/public/agent/sessions")
    token = session.json()["session_token"]
    # Act
    r1 = await client.post(
        "/api/v1/public/agent/turn",
        json={"session_token": token, "message": "Hello"},
    )
    r2 = await client.post(
        "/api/v1/public/agent/turn",
        json={"session_token": token, "message": "Again"},
    )
    # Assert
    assert r1.status_code == 200
    assert r1.json()["interactions_remaining"] == 2
    assert "_stub_last_user_message" in r1.json()["config"]
    assert r2.status_code == 200
    assert r2.json()["interactions_remaining"] == 1


@pytest.mark.asyncio
async def test__public_agent_turn__fourth_turn_is_forbidden(client: AsyncClient):
    # Arrange
    session = await client.post("/api/v1/public/agent/sessions")
    token = session.json()["session_token"]
    for i in range(3):
        r = await client.post(
            "/api/v1/public/agent/turn",
            json={"session_token": token, "message": f"m{i}"},
        )
        assert r.status_code == 200, r.text
    # Act
    fourth = await client.post(
        "/api/v1/public/agent/turn",
        json={"session_token": token, "message": "nope"},
    )
    # Assert
    assert fourth.status_code == 403
    assert "detail" in fourth.json()


@pytest.mark.asyncio
async def test__public_agent_turn__bad_token_unauthorized(client: AsyncClient):
    # Arrange
    # Act
    response = await client.post(
        "/api/v1/public/agent/turn",
        json={"session_token": "not-a-real-token", "message": "hi"},
    )
    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test__public_agent_turn__merges_config_from_body(client: AsyncClient):
    # Arrange
    session = await client.post("/api/v1/public/agent/sessions")
    token = session.json()["session_token"]
    # Act
    response = await client.post(
        "/api/v1/public/agent/turn",
        json={"session_token": token, "message": "x", "config": {"blocks": []}},
    )
    # Assert
    assert response.status_code == 200
    assert response.json()["config"]["blocks"] == []
