import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__agent_turn__persists_config_for_owner(
    client: AsyncClient, auth_headers: dict[str, str]
):
    # Arrange
    created = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json={"slug": "agent-site", "config": {"version": 1}},
    )
    assert created.status_code == 201
    site_id = created.json()["id"]
    # Act
    turn = await client.post(
        f"/api/v1/wedding-sites/{site_id}/agent/turn",
        headers=auth_headers,
        json={"message": "Add hero", "config": {"version": 2}},
    )
    # Assert
    assert turn.status_code == 200
    data = turn.json()
    assert data["interactions_remaining"] is None
    assert data["message"].startswith("(stub agent)")
    assert data["config"]["version"] == 2
    assert data["config"]["_stub_last_user_message"] == "Add hero"
    loaded = await client.get(f"/api/v1/wedding-sites/{site_id}", headers=auth_headers)
    assert loaded.json()["config"] == data["config"]


@pytest.mark.asyncio
async def test__agent_turn__not_found_for_other_user(client: AsyncClient):
    # Arrange
    email_a = f"a-{uuid.uuid4().hex[:12]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email_a, "password": "password123"},
    )
    login_a = await client.post(
        "/api/v1/auth/login",
        json={"email": email_a, "password": "password123"},
    )
    headers_a = {"Authorization": f"Bearer {login_a.json()['access_token']}"}
    site = await client.post(
        "/api/v1/wedding-sites",
        headers=headers_a,
        json={"slug": f"only-a-{uuid.uuid4().hex[:8]}"},
    )
    site_id = site.json()["id"]

    email_b = f"b-{uuid.uuid4().hex[:12]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email_b, "password": "password123"},
    )
    login_b = await client.post(
        "/api/v1/auth/login",
        json={"email": email_b, "password": "password123"},
    )
    headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}
    # Act
    response = await client.post(
        f"/api/v1/wedding-sites/{site_id}/agent/turn",
        headers=headers_b,
        json={"message": "hack"},
    )
    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test__agent_turn__requires_bearer(client: AsyncClient, auth_headers: dict[str, str]):
    # Arrange
    created = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json={"slug": f"auth-only-{uuid.uuid4().hex[:8]}"},
    )
    site_id = created.json()["id"]
    # Act
    response = await client.post(
        f"/api/v1/wedding-sites/{site_id}/agent/turn",
        json={"message": "x"},
    )
    # Assert
    assert response.status_code == 403


@pytest.mark.asyncio
async def test__agent_turn__rejects_overlong_message(
    client: AsyncClient, auth_headers: dict[str, str]
):
    # Arrange
    created = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json={"slug": "long-message-site"},
    )
    assert created.status_code == 201
    site_id = created.json()["id"]
    too_long = "a" * 501
    # Act
    response = await client.post(
        f"/api/v1/wedding-sites/{site_id}/agent/turn",
        headers=auth_headers,
        json={"message": too_long},
    )
    # Assert
    assert response.status_code == 422
    assert "detail" in response.json()
