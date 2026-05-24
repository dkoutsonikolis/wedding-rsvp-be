import re

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__list_wedding_sites__empty(
    client: AsyncClient, auth_headers_without_site: dict[str, str]
):
    # Arrange
    url = "/api/v1/wedding-sites"
    # Act
    response = await client.get(url, headers=auth_headers_without_site)
    # Assert
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test__list_wedding_sites__returns_owned(
    client: AsyncClient, auth_headers: dict[str, str], auth_user_site_id: str
):
    # Act
    response = await client.get("/api/v1/wedding-sites", headers=auth_headers)
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == auth_user_site_id
    assert data[0]["status"] == "draft"
    assert data[0]["config"] == {}
    assert re.fullmatch(r"site-[0-9a-f]{12}", data[0]["slug"])
    assert "owner_user_id" not in data[0]


@pytest.mark.asyncio
async def test__list_wedding_sites__no_bearer(client: AsyncClient):
    # Arrange
    url = "/api/v1/wedding-sites"
    # Act
    response = await client.get(url)
    # Assert
    assert response.status_code == 403
