import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__delete_wedding_site__no_content(client: AsyncClient, auth_headers: dict[str, str]):
    # Arrange
    created = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json={"slug": "delete-me"},
    )
    site_id = created.json()["id"]
    # Act
    response = await client.delete(f"/api/v1/wedding-sites/{site_id}", headers=auth_headers)
    # Assert
    assert response.status_code == 204
    assert response.content == b""
    get_after = await client.get(f"/api/v1/wedding-sites/{site_id}", headers=auth_headers)
    assert get_after.status_code == 404


@pytest.mark.asyncio
async def test__delete_wedding_site__not_found(client: AsyncClient, auth_headers: dict[str, str]):
    # Arrange
    missing = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    # Act
    response = await client.delete(f"/api/v1/wedding-sites/{missing}", headers=auth_headers)
    # Assert
    assert response.status_code == 404
