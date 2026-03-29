import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__patch_wedding_site__updates_fields(
    client: AsyncClient, auth_headers: dict[str, str]
):
    # Arrange
    created = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json={"slug": "patch-me"},
    )
    site_id = created.json()["id"]
    # Act
    response = await client.patch(
        f"/api/v1/wedding-sites/{site_id}",
        headers=auth_headers,
        json={"title": "New title", "status": "published", "config": {"x": 1}},
    )
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["status"] == "published"
    assert data["config"] == {"x": 1}


@pytest.mark.asyncio
async def test__patch_wedding_site__slug_conflict(
    client: AsyncClient, auth_headers: dict[str, str]
):
    # Arrange
    await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json={"slug": "taken-slug"},
    )
    second = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json={"slug": "other-site"},
    )
    site_id = second.json()["id"]
    # Act
    response = await client.patch(
        f"/api/v1/wedding-sites/{site_id}",
        headers=auth_headers,
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
async def test__patch_wedding_site__invalid_slug(client: AsyncClient, auth_headers: dict[str, str]):
    # Arrange
    created = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json={"slug": "ok-slug"},
    )
    site_id = created.json()["id"]
    # Act
    response = await client.patch(
        f"/api/v1/wedding-sites/{site_id}",
        headers=auth_headers,
        json={"slug": "Bad_Slug"},
    )
    # Assert
    assert response.status_code == 422
