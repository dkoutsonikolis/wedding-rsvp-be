import uuid

import pytest
from httpx import AsyncClient


async def _publish_site(client: AsyncClient, auth_headers: dict[str, str], site_id: str) -> str:
    response = await client.patch(
        f"/api/v1/wedding-sites/{site_id}",
        headers=auth_headers,
        json={"status": "published"},
    )
    assert response.status_code == 200
    return response.json()["slug"]


async def _submit_rsvp(
    client: AsyncClient,
    slug: str,
    name: str,
    email: str,
    *,
    is_attending: bool = True,
    party_size: int | None = None,
    notes: str | None = None,
) -> dict:
    payload: dict = {
        "name": name,
        "email": email,
        "is_attending": is_attending,
    }
    if is_attending:
        payload["party_size"] = 1 if party_size is None else party_size
    else:
        payload["party_size"] = 0 if party_size is None else party_size
    if notes is not None:
        payload["notes"] = notes
    response = await client.post(
        f"/api/v1/public/wedding-sites/{slug}/rsvp-responses",
        json=payload,
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test__list_rsvp_responses__returns_newest_first_and_cursor(
    client: AsyncClient,
    auth_headers: dict[str, str],
    auth_user_site_id: str,
):
    # Arrange
    site_id = auth_user_site_id
    slug = await _publish_site(client, auth_headers, site_id)
    await _submit_rsvp(client, slug, "First Guest", "first@example.com")
    second_submitted = await _submit_rsvp(client, slug, "Second Guest", "second@example.com")
    third_submitted = await _submit_rsvp(client, slug, "Third Guest", "third@example.com")
    # Act
    response = await client.get(
        f"/api/v1/wedding-sites/{site_id}/rsvp-responses",
        headers=auth_headers,
        params={"limit": 2},
    )
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert [item["id"] for item in data["items"]] == [
        third_submitted["id"],
        second_submitted["id"],
    ]
    assert data["items"][0]["name"] == "Third Guest"
    assert data["next_before_response_id"] == second_submitted["id"]


@pytest.mark.asyncio
async def test__list_rsvp_responses__before_response_id_returns_older_page(
    client: AsyncClient,
    auth_headers: dict[str, str],
    auth_user_site_id: str,
):
    # Arrange
    site_id = auth_user_site_id
    slug = await _publish_site(client, auth_headers, site_id)
    oldest_submitted = await _submit_rsvp(client, slug, "Oldest Guest", "oldest@example.com")
    await _submit_rsvp(client, slug, "Middle Guest", "middle@example.com")
    await _submit_rsvp(client, slug, "Newest Guest", "newest@example.com")
    first_page = await client.get(
        f"/api/v1/wedding-sites/{site_id}/rsvp-responses",
        headers=auth_headers,
        params={"limit": 2},
    )
    before_id = first_page.json()["next_before_response_id"]
    # Act
    second_page = await client.get(
        f"/api/v1/wedding-sites/{site_id}/rsvp-responses",
        headers=auth_headers,
        params={"limit": 2, "before_response_id": before_id},
    )
    # Assert
    assert second_page.status_code == 200
    data = second_page.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == oldest_submitted["id"]
    assert data["next_before_response_id"] is None


@pytest.mark.asyncio
async def test__list_rsvp_responses__without_token(
    client: AsyncClient,
    auth_user_site_id: str,
):
    # Arrange
    site_id = auth_user_site_id
    # Act
    response = await client.get(f"/api/v1/wedding-sites/{site_id}/rsvp-responses")
    # Assert
    assert response.status_code == 403


@pytest.mark.asyncio
async def test__list_rsvp_responses__other_owner(client: AsyncClient):
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
    site_id = sites_a.json()[0]["id"]

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
    response = await client.get(
        f"/api/v1/wedding-sites/{site_id}/rsvp-responses",
        headers=headers_b,
    )
    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test__list_rsvp_responses__is_attending_filter(
    client: AsyncClient,
    auth_headers: dict[str, str],
    auth_user_site_id: str,
):
    # Arrange
    site_id = auth_user_site_id
    slug = await _publish_site(client, auth_headers, site_id)
    await _submit_rsvp(client, slug, "Attending Guest", "yes@example.com", is_attending=True)
    declined = await _submit_rsvp(
        client,
        slug,
        "Declined Guest",
        "no@example.com",
        is_attending=False,
    )
    # Act
    response = await client.get(
        f"/api/v1/wedding-sites/{site_id}/rsvp-responses",
        headers=auth_headers,
        params={"is_attending": False},
    )
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == declined["id"]
    assert data["next_before_response_id"] is None


@pytest.mark.asyncio
async def test__list_rsvp_responses__q_filter(
    client: AsyncClient,
    auth_headers: dict[str, str],
    auth_user_site_id: str,
):
    # Arrange
    site_id = auth_user_site_id
    slug = await _publish_site(client, auth_headers, site_id)
    await _submit_rsvp(client, slug, "Other Guest", "other@example.com")
    match = await _submit_rsvp(
        client,
        slug,
        "Searchable Guest",
        "findme@example.com",
        notes="Bring a plus-one",
    )
    # Act
    response = await client.get(
        f"/api/v1/wedding-sites/{site_id}/rsvp-responses",
        headers=auth_headers,
        params={"q": "plus-one"},
    )
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == match["id"]


@pytest.mark.asyncio
async def test__list_rsvp_responses__q_above_max_length(
    client: AsyncClient,
    auth_headers: dict[str, str],
    auth_user_site_id: str,
):
    # Arrange
    site_id = auth_user_site_id
    # Act
    response = await client.get(
        f"/api/v1/wedding-sites/{site_id}/rsvp-responses",
        headers=auth_headers,
        params={"q": "x" * 101},
    )
    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test__list_rsvp_responses__limit_above_max(
    client: AsyncClient,
    auth_headers: dict[str, str],
    auth_user_site_id: str,
):
    # Arrange
    site_id = auth_user_site_id
    # Act
    response = await client.get(
        f"/api/v1/wedding-sites/{site_id}/rsvp-responses",
        headers=auth_headers,
        params={"limit": 51},
    )
    # Assert
    assert response.status_code == 422
