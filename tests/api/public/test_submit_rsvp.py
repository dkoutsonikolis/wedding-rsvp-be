import pytest
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from domains.rsvp_responses.models import RsvpResponse
from domains.wedding_sites.enums import SiteStatus


@pytest.mark.asyncio
async def test__submit_rsvp__email_only(
    client: AsyncClient,
    test_session: AsyncSession,
    wedding_site_factory,
):
    # Arrange
    site = await wedding_site_factory(slug="public-submit", status=SiteStatus.PUBLISHED)
    payload = {
        "name": "Alex Guest",
        "email": "alex@example.com",
        "is_attending": True,
        "party_size": 2,
        "notes": "Vegetarian please",
    }
    # Act
    response = await client.post(
        f"/api/v1/public/wedding-sites/{site.slug}/rsvp-responses",
        json=payload,
    )
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alex Guest"
    assert data["email"] == "alex@example.com"
    assert data["phone"] is None
    assert data["is_attending"] is True
    assert data["party_size"] == 2
    assert data["notes"] == "Vegetarian please"
    rows = (
        await test_session.exec(select(RsvpResponse).where(RsvpResponse.wedding_site_id == site.id))
    ).all()
    assert len(rows) == 1


@pytest.mark.asyncio
async def test__submit_rsvp__phone_only(
    client: AsyncClient,
    test_session: AsyncSession,
    wedding_site_factory,
):
    # Arrange
    site = await wedding_site_factory(slug="phone-submit", status=SiteStatus.PUBLISHED)
    payload = {
        "name": "Sam Guest",
        "phone": "+306912345678",
        "is_attending": True,
        "party_size": 1,
    }
    # Act
    response = await client.post(
        f"/api/v1/public/wedding-sites/{site.slug}/rsvp-responses",
        json=payload,
    )
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["phone"] == "+306912345678"
    assert data["email"] is None


@pytest.mark.asyncio
async def test__submit_rsvp__neither_email_nor_phone(
    client: AsyncClient,
    wedding_site_factory,
):
    # Arrange
    site = await wedding_site_factory(slug="no-contact-submit", status=SiteStatus.PUBLISHED)
    payload = {
        "name": "No Contact",
        "is_attending": True,
        "party_size": 1,
    }
    # Act
    response = await client.post(
        f"/api/v1/public/wedding-sites/{site.slug}/rsvp-responses",
        json=payload,
    )
    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test__submit_rsvp__unknown_slug(client: AsyncClient):
    # Arrange
    payload = {
        "name": "Guest",
        "email": "guest@example.com",
        "is_attending": True,
        "party_size": 1,
    }
    # Act
    response = await client.post(
        "/api/v1/public/wedding-sites/missing-site/rsvp-responses",
        json=payload,
    )
    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test__submit_rsvp__draft_site(
    client: AsyncClient,
    wedding_site_factory,
):
    # Arrange
    site = await wedding_site_factory(slug="draft-submit")
    payload = {
        "name": "Guest",
        "email": "guest@example.com",
        "is_attending": True,
        "party_size": 1,
    }
    # Act
    response = await client.post(
        f"/api/v1/public/wedding-sites/{site.slug}/rsvp-responses",
        json=payload,
    )
    # Assert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test__submit_rsvp__is_attending_false_nonzero_party_size(
    client: AsyncClient,
    wedding_site_factory,
):
    # Arrange
    site = await wedding_site_factory(slug="decline-submit", status=SiteStatus.PUBLISHED)
    payload = {
        "name": "Declining Guest",
        "email": "decline@example.com",
        "is_attending": False,
        "party_size": 3,
    }
    # Act
    response = await client.post(
        f"/api/v1/public/wedding-sites/{site.slug}/rsvp-responses",
        json=payload,
    )
    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test__submit_rsvp__without_notes(
    client: AsyncClient,
    wedding_site_factory,
):
    # Arrange
    site = await wedding_site_factory(slug="no-notes-submit", status=SiteStatus.PUBLISHED)
    payload = {
        "name": "Guest",
        "email": "guest@example.com",
        "is_attending": True,
        "party_size": 1,
    }
    # Act
    response = await client.post(
        f"/api/v1/public/wedding-sites/{site.slug}/rsvp-responses",
        json=payload,
    )
    # Assert
    assert response.status_code == 201
    assert response.json()["notes"] is None
