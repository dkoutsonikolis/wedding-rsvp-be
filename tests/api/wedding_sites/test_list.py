import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__list_wedding_sites__empty(client: AsyncClient, auth_headers: dict[str, str]):
    # Arrange
    url = "/api/v1/wedding-sites"
    # Act
    response = await client.get(url, headers=auth_headers)
    # Assert
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test__list_wedding_sites__returns_owned(
    client: AsyncClient, auth_headers: dict[str, str]
):
    # Arrange
    created = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json={"slug": "summer-2026", "title": "Our wedding"},
    )
    assert created.status_code == 201
    site_id = created.json()["id"]
    # Act
    response = await client.get("/api/v1/wedding-sites", headers=auth_headers)
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == site_id
    assert data[0]["slug"] == "summer-2026"
    assert data[0]["title"] == "Our wedding"
    assert data[0]["config"] == {}
    assert "owner_user_id" not in data[0]


@pytest.mark.asyncio
async def test__list_wedding_sites__no_bearer(client: AsyncClient):
    # Arrange
    url = "/api/v1/wedding-sites"
    # Act
    response = await client.get(url)
    # Assert
    assert response.status_code == 403
