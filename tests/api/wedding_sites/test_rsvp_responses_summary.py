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
async def test__rsvp_responses_summary__returns_counts_and_preview_rows(
    client: AsyncClient,
    auth_headers: dict[str, str],
    auth_user_site_id: str,
):
    # Arrange
    site_id = auth_user_site_id
    slug = await _publish_site(client, auth_headers, site_id)
    await _submit_rsvp(client, slug, "Attending One", "one@example.com", party_size=2)
    await _submit_rsvp(
        client,
        slug,
        "Declined Guest",
        "no@example.com",
        is_attending=False,
    )
    newest = await _submit_rsvp(
        client,
        slug,
        "Attending Two",
        "two@example.com",
        party_size=4,
        notes="Gluten free",
    )
    # Act
    response = await client.get(
        f"/api/v1/wedding-sites/{site_id}/rsvp-responses/summary",
        headers=auth_headers,
    )
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total_responses"] == 3
    assert data["attending_count"] == 2
    assert data["declined_count"] == 1
    assert data["total_guests"] == 6
    assert len(data["recent_activity"]) == 3
    assert data["recent_activity"][0]["id"] == newest["id"]
    assert data["recent_activity"][0]["name"] == "Attending Two"
    assert len(data["guest_notes"]) == 1
    assert data["guest_notes"][0]["notes"] == "Gluten free"


@pytest.mark.asyncio
async def test__rsvp_responses_summary__without_token(
    client: AsyncClient,
    auth_user_site_id: str,
):
    # Arrange
    site_id = auth_user_site_id
    # Act
    response = await client.get(f"/api/v1/wedding-sites/{site_id}/rsvp-responses/summary")
    # Assert
    assert response.status_code == 403


@pytest.mark.asyncio
async def test__rsvp_responses_summary__other_owner(client: AsyncClient):
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
        f"/api/v1/wedding-sites/{site_id}/rsvp-responses/summary",
        headers=headers_b,
    )
    # Assert
    assert response.status_code == 404
