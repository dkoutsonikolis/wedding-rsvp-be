import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__create_wedding_site__with_explicit_slug(
    client: AsyncClient, auth_headers: dict[str, str]
):
    # Arrange
    payload = {"slug": "garden-party", "title": "Garden party"}
    # Act
    response = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json=payload,
    )
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "garden-party"
    assert data["title"] == "Garden party"
    assert data["status"] == "draft"
    assert data["schema_version"] == 1
    assert data["config"] == {}


@pytest.mark.asyncio
async def test__create_wedding_site__auto_slug(client: AsyncClient, auth_headers: dict[str, str]):
    # Arrange
    payload = {"title": "Beach Wedding Day"}
    # Act
    response = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json=payload,
    )
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "beach-wedding-day"
    assert data["title"] == "Beach Wedding Day"


@pytest.mark.asyncio
async def test__create_wedding_site__duplicate_slug(
    client: AsyncClient, auth_headers: dict[str, str]
):
    # Arrange
    slug = "unique-clash"
    first = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json={"slug": slug},
    )
    assert first.status_code == 201
    # Act
    second = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json={"slug": slug},
    )
    # Assert
    assert second.status_code == 409
    assert "detail" in second.json()


@pytest.mark.asyncio
async def test__create_wedding_site__invalid_slug(
    client: AsyncClient, auth_headers: dict[str, str]
):
    # Arrange
    # Slugs are normalized to lowercase; use characters still forbidden after that (no underscores).
    payload = {"slug": "bad_slug"}
    # Act
    response = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json=payload,
    )
    # Assert
    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test__create_wedding_site__no_bearer(client: AsyncClient):
    # Arrange
    url = "/api/v1/wedding-sites"
    # Act
    response = await client.post(
        url,
        json={"slug": "no-auth-test", "title": "x"},
    )
    # Assert
    assert response.status_code == 403
