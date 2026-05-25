import pytest

from domains.rsvp_responses.service import RsvpResponsesService
from domains.wedding_sites.enums import SiteStatus
from domains.wedding_sites.exceptions import WeddingSiteNotFoundError


@pytest.mark.asyncio
async def test__summary_for_owner__aggregates_and_preview_rows(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
    site_owner_user_id,
):
    # Arrange
    site = await wedding_site_factory(slug="owner-summary", status=SiteStatus.PUBLISHED)
    await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Oldest",
        email="oldest@example.com",
        phone=None,
        is_attending=True,
        party_size=2,
        notes=None,
    )
    middle = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Middle",
        email="middle@example.com",
        phone=None,
        is_attending=False,
        party_size=0,
        notes="  ",
    )
    newest = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Newest",
        email="newest@example.com",
        phone=None,
        is_attending=True,
        party_size=3,
        notes="Vegetarian meal",
    )
    newest_note = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Older Note",
        email="older-note@example.com",
        phone=None,
        is_attending=True,
        party_size=1,
        notes="First note",
    )
    # Act
    summary = await rsvp_responses_service.summary_for_owner(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
    )
    # Assert
    assert summary.total_responses == 4
    assert summary.attending_count == 3
    assert summary.declined_count == 1
    assert summary.total_guests == 6
    assert [row.id for row in summary.recent_activity] == [
        newest_note.id,
        newest.id,
        middle.id,
    ]
    assert len(summary.recent_activity) == 3
    assert [row.name for row in summary.guest_notes] == ["Older Note", "Newest"]
    assert all(row.notes and row.notes.strip() for row in summary.guest_notes)


@pytest.mark.asyncio
async def test__summary_for_owner__site_not_owned_by_user(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
    other_user_id,
):
    # Arrange
    site = await wedding_site_factory(slug="summary-not-owned")
    # Act
    with pytest.raises(WeddingSiteNotFoundError):
        await rsvp_responses_service.summary_for_owner(
            site_id=site.id,
            owner_user_id=other_user_id,
        )
    # Assert
