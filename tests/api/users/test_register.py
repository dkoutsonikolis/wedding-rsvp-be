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
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["expires_in"] == 30 * 60
    assert data["refresh_expires_in"] == 7 * 24 * 3600
    assert data["user"]["email"] == "newuser@example.com"
    assert "id" in data["user"]
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


@pytest.mark.asyncio
async def test__register__with_anonymous_session_token(client: AsyncClient):
    # Arrange
    session_response = await client.post("/api/v1/public/agent/sessions")
    session_token = session_response.json()["session_token"]
    draft_turn = await client.post(
        "/api/v1/public/agent/turn",
        json={
            "session_token": session_token,
            "message": "Build my site",
            "config": {"hero": {"title": "Nina and Theo"}, "schedule": {"enabled": True}},
        },
    )
    assert draft_turn.status_code == 200
    register_payload = {
        "email": "imported-draft@example.com",
        "password": "password123",
        "anonymous_session_token": session_token,
    }
    # Act
    register_response = await client.post("/api/v1/auth/register", json=register_payload)
    access_token = register_response.json()["access_token"]
    sites_response = await client.get(
        "/api/v1/wedding-sites",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    expired_public_trial_turn = await client.post(
        "/api/v1/public/agent/turn",
        json={"session_token": session_token, "message": "Can I keep using this token?"},
    )
    # Assert
    assert register_response.status_code == 201
    assert sites_response.status_code == 200
    assert expired_public_trial_turn.status_code == 401
    sites = sites_response.json()
    assert len(sites) == 1


@pytest.mark.asyncio
async def test__register__with_invalid_anonymous_session_token(client: AsyncClient):
    # Arrange
    register_payload = {
        "email": "invalid-anon-session@example.com",
        "password": "password123",
        "anonymous_session_token": "not-a-real-token",
    }
    # Act
    register_response = await client.post("/api/v1/auth/register", json=register_payload)
    access_token = register_response.json()["access_token"]
    sites_response = await client.get(
        "/api/v1/wedding-sites",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    # Assert
    assert register_response.status_code == 201
    assert sites_response.status_code == 200
    assert sites_response.json() == []
