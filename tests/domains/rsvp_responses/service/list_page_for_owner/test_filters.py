import pytest

from domains.rsvp_responses.service import RsvpResponsesService
from domains.wedding_sites.enums import SiteStatus


@pytest.mark.asyncio
async def test__list_page_for_owner__is_attending_true(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
    site_owner_user_id,
):
    # Arrange
    site = await wedding_site_factory(slug="filter-attending", status=SiteStatus.PUBLISHED)
    attending = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Yes Guest",
        email="yes@example.com",
        phone=None,
        is_attending=True,
        party_size=2,
        notes=None,
    )
    await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="No Guest",
        email="no@example.com",
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
        is_attending=True,
    )
    # Assert
    assert [row.id for row in rows] == [attending.id]
    assert next_before_response_id is None


@pytest.mark.asyncio
async def test__list_page_for_owner__is_attending_false(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
    site_owner_user_id,
):
    # Arrange
    site = await wedding_site_factory(slug="filter-declined", status=SiteStatus.PUBLISHED)
    await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Yes Guest",
        email="yes@example.com",
        phone=None,
        is_attending=True,
        party_size=1,
        notes=None,
    )
    declined = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="No Guest",
        email="no@example.com",
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
        is_attending=False,
    )
    # Assert
    assert [row.id for row in rows] == [declined.id]
    assert next_before_response_id is None


@pytest.mark.asyncio
async def test__list_page_for_owner__q_matches_name_case_insensitive(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
    site_owner_user_id,
):
    # Arrange
    site = await wedding_site_factory(slug="filter-search-name", status=SiteStatus.PUBLISHED)
    await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Other Person",
        email="other@example.com",
        phone=None,
        is_attending=True,
        party_size=1,
        notes=None,
    )
    match = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Alice Smith",
        email="alice@example.com",
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
        q="  ALICE  ",
    )
    # Assert
    assert [row.id for row in rows] == [match.id]
    assert next_before_response_id is None


@pytest.mark.asyncio
async def test__list_page_for_owner__q_matches_email_phone_and_notes(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
    site_owner_user_id,
):
    # Arrange
    site = await wedding_site_factory(slug="filter-search-fields", status=SiteStatus.PUBLISHED)
    by_email = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Email Guest",
        email="unique.email@example.com",
        phone=None,
        is_attending=True,
        party_size=1,
        notes=None,
    )
    by_phone = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Phone Guest",
        email=None,
        phone="+15551234567",
        is_attending=True,
        party_size=1,
        notes=None,
    )
    by_notes = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Notes Guest",
        email="notes@example.com",
        phone=None,
        is_attending=True,
        party_size=1,
        notes="Vegetarian meal please",
    )
    # Act
    email_rows, _ = await rsvp_responses_service.list_page_for_owner(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        limit=20,
        q="unique.email",
    )
    phone_rows, _ = await rsvp_responses_service.list_page_for_owner(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        limit=20,
        q="555123",
    )
    notes_rows, _ = await rsvp_responses_service.list_page_for_owner(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        limit=20,
        q="vegetarian",
    )
    # Assert
    assert [row.id for row in email_rows] == [by_email.id]
    assert [row.id for row in phone_rows] == [by_phone.id]
    assert [row.id for row in notes_rows] == [by_notes.id]


@pytest.mark.asyncio
async def test__list_page_for_owner__q_and_is_attending_combined(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
    site_owner_user_id,
):
    # Arrange
    site = await wedding_site_factory(slug="filter-combined", status=SiteStatus.PUBLISHED)
    await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Bob Attending",
        email="bob-attend@example.com",
        phone=None,
        is_attending=True,
        party_size=1,
        notes=None,
    )
    await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Bob Declined",
        email="bob-decline@example.com",
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
        q="bob",
        is_attending=False,
    )
    # Assert
    assert len(rows) == 1
    assert rows[0].name == "Bob Declined"
    assert next_before_response_id is None


@pytest.mark.asyncio
async def test__list_page_for_owner__whitespace_only_q_ignored(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
    site_owner_user_id,
):
    # Arrange
    site = await wedding_site_factory(slug="filter-empty-q", status=SiteStatus.PUBLISHED)
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
        is_attending=True,
        party_size=1,
        notes=None,
    )
    # Act
    rows, next_before_response_id = await rsvp_responses_service.list_page_for_owner(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        limit=20,
        q="   ",
    )
    # Assert
    assert [row.id for row in rows] == [second.id, first.id]
    assert next_before_response_id is None


@pytest.mark.asyncio
async def test__list_page_for_owner__filtered_cursor_pagination(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
    site_owner_user_id,
):
    # Arrange
    site = await wedding_site_factory(slug="filter-paged", status=SiteStatus.PUBLISHED)
    oldest = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Team Alpha One",
        email="alpha1@example.com",
        phone=None,
        is_attending=True,
        party_size=1,
        notes=None,
    )
    middle = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Team Alpha Two",
        email="alpha2@example.com",
        phone=None,
        is_attending=True,
        party_size=1,
        notes=None,
    )
    newest = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Team Alpha Three",
        email="alpha3@example.com",
        phone=None,
        is_attending=True,
        party_size=1,
        notes=None,
    )
    await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Unrelated Guest",
        email="other@example.com",
        phone=None,
        is_attending=True,
        party_size=1,
        notes=None,
    )
    first_page, next_before = await rsvp_responses_service.list_page_for_owner(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        limit=2,
        q="alpha",
    )
    # Act
    second_page, next_after_second = await rsvp_responses_service.list_page_for_owner(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        limit=2,
        before_response_id=next_before,
        q="alpha",
    )
    # Assert
    assert [row.id for row in first_page] == [newest.id, middle.id]
    assert next_before == middle.id
    assert [row.id for row in second_page] == [oldest.id]
    assert next_after_second is None
