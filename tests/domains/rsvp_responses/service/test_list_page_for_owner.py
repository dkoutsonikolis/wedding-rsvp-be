import pytest

from domains.rsvp_responses.service import RsvpResponsesService
from domains.wedding_sites.enums import SiteStatus
from domains.wedding_sites.exceptions import WeddingSiteNotFoundError


@pytest.mark.asyncio
async def test__list_page_for_owner__without_before_response_id(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
    site_owner_user_id,
):
    # Arrange
    site = await wedding_site_factory(slug="owner-list", status=SiteStatus.PUBLISHED)
    first = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="First",
        email="first@example.com",
        phone=None,
        is_attending=True,
        party_size=1,
        notes=None,
    )
    second = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Second",
        email="second@example.com",
        phone=None,
        is_attending=False,
        party_size=0,
        notes=None,
    )
    # Act
    rows, next_before_response_id = await rsvp_responses_service.list_page_for_owner(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        limit=20,
    )
    # Assert
    assert [row.id for row in rows] == [second.id, first.id]
    assert next_before_response_id is None


@pytest.mark.asyncio
async def test__list_page_for_owner__with_before_response_id(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
    site_owner_user_id,
):
    # Arrange
    site = await wedding_site_factory(slug="paged-list", status=SiteStatus.PUBLISHED)
    oldest = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Oldest",
        email="oldest@example.com",
        phone=None,
        is_attending=True,
        party_size=1,
        notes=None,
    )
    middle = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Middle",
        email="middle@example.com",
        phone=None,
        is_attending=True,
        party_size=1,
        notes=None,
    )
    newest = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Newest",
        email="newest@example.com",
        phone=None,
        is_attending=True,
        party_size=1,
        notes=None,
    )
    first_page, next_before = await rsvp_responses_service.list_page_for_owner(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        limit=2,
    )
    # Act
    second_page, next_after_second = await rsvp_responses_service.list_page_for_owner(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        limit=2,
        before_response_id=next_before,
    )
    # Assert
    assert [row.id for row in first_page] == [newest.id, middle.id]
    assert next_before == middle.id
    assert [row.id for row in second_page] == [oldest.id]
    assert next_after_second is None


@pytest.mark.asyncio
async def test__list_page_for_owner__invalid_before_response_id(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
    site_owner_user_id,
):
    # Arrange
    site = await wedding_site_factory(slug="bad-cursor", status=SiteStatus.PUBLISHED)
    await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Guest",
        email="guest@example.com",
        phone=None,
        is_attending=True,
        party_size=1,
        notes=None,
    )
    # Act
    rows, next_before_response_id = await rsvp_responses_service.list_page_for_owner(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        limit=20,
        before_response_id=site.id,
    )
    # Assert
    assert rows == []
    assert next_before_response_id is None


@pytest.mark.asyncio
async def test__list_page_for_owner__site_not_owned_by_user(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
    other_user_id,
):
    # Arrange
    site = await wedding_site_factory(slug="owned-by-someone-else")
    # Act
    with pytest.raises(WeddingSiteNotFoundError):
        await rsvp_responses_service.list_page_for_owner(
            site_id=site.id,
            owner_user_id=other_user_id,
            limit=20,
        )
    # Assert
