import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__patch_wedding_site__updates_fields(
    client: AsyncClient, auth_headers: dict[str, str], auth_user_site_id: str
):
    # Act
    response = await client.patch(
        f"/api/v1/wedding-sites/{auth_user_site_id}",
        headers=auth_headers,
        json={
            "slug": "patch-me",
            "title": "New title",
            "status": "published",
            "config": {"x": 1},
        },
    )
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "patch-me"
    assert data["title"] == "New title"
    assert data["status"] == "published"
    assert data["config"] == {"x": 1}


@pytest.mark.asyncio
async def test__patch_wedding_site__slug_conflict(client: AsyncClient):
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
    sites_a = await client.get("/api/v1/wedding-sites", headers=headers_a)
    await client.patch(
        f"/api/v1/wedding-sites/{sites_a.json()[0]['id']}",
        headers=headers_a,
        json={"slug": "taken-slug"},
    )

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
    sites_b = await client.get("/api/v1/wedding-sites", headers=headers_b)
    site_id_b = sites_b.json()[0]["id"]
    await client.patch(
        f"/api/v1/wedding-sites/{site_id_b}",
        headers=headers_b,
        json={"slug": "other-site"},
    )
    # Act
    response = await client.patch(
        f"/api/v1/wedding-sites/{site_id_b}",
        headers=headers_b,
        json={"slug": "taken-slug"},
    )
    # Assert
    assert response.status_code == 409


@pytest.mark.asyncio
async def test__patch_wedding_site__not_found(client: AsyncClient, auth_headers: dict[str, str]):
    # Arrange
    missing = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    # Act
    response = await client.patch(
        f"/api/v1/wedding-sites/{missing}",
        headers=auth_headers,
        json={"title": "Nope"},
    )
    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test__patch_wedding_site__invalid_slug(
    client: AsyncClient, auth_headers: dict[str, str], auth_user_site_id: str
):
    # Act
    response = await client.patch(
        f"/api/v1/wedding-sites/{auth_user_site_id}",
        headers=auth_headers,
        json={"slug": "Bad_Slug"},
    )
    # Assert
    assert response.status_code == 422
