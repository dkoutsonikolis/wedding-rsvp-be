import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__get_wedding_site__success(client: AsyncClient, auth_headers: dict[str, str]):
    # Arrange
    created = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json={"slug": "get-me", "config": {"blocks": []}},
    )
    site_id = created.json()["id"]
    # Act
    response = await client.get(f"/api/v1/wedding-sites/{site_id}", headers=auth_headers)
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == site_id
    assert data["slug"] == "get-me"
    assert data["config"] == {"blocks": []}


@pytest.mark.asyncio
async def test__get_wedding_site__not_found(client: AsyncClient, auth_headers: dict[str, str]):
    # Arrange
    missing = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    # Act
    response = await client.get(f"/api/v1/wedding-sites/{missing}", headers=auth_headers)
    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test__get_wedding_site__other_owner(client: AsyncClient):
    # Arrange
    email_a = f"a-{uuid.uuid4().hex[:10]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email_a, "password": "password123"},
    )
    login_a = await client.post(
        "/api/v1/auth/login",
        json={"email": email_a, "password": "password123"},
    )
    headers_a = {"Authorization": f"Bearer {login_a.json()['access_token']}"}
    created = await client.post(
        "/api/v1/wedding-sites",
        headers=headers_a,
        json={"slug": "owner-a-only"},
    )
    site_id = created.json()["id"]

    email_b = f"b-{uuid.uuid4().hex[:10]}@example.com"
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
    response = await client.get(f"/api/v1/wedding-sites/{site_id}", headers=headers_b)
    # Assert
    assert response.status_code == 404
