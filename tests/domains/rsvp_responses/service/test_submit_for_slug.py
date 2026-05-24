import pytest

from domains.rsvp_responses.exceptions import (
    InvalidRsvpSubmissionError,
    RsvpWeddingSiteNotFoundError,
    RsvpWeddingSiteNotPublishedError,
)
from domains.rsvp_responses.service import RsvpResponsesService
from domains.wedding_sites.enums import SiteStatus


@pytest.mark.asyncio
async def test__submit_for_slug__email_only(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
):
    # Arrange
    site = await wedding_site_factory(slug="public-rsvp", status=SiteStatus.PUBLISHED)
    # Act
    created = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Alex Guest",
        email="alex@example.com",
        phone=None,
        is_attending=True,
        party_size=2,
        notes="Vegetarian please",
    )
    # Assert
    assert created.wedding_site_id == site.id
    assert created.email == "alex@example.com"
    assert created.phone is None
    assert created.is_attending is True
    assert created.party_size == 2
    assert created.notes == "Vegetarian please"


@pytest.mark.asyncio
async def test__submit_for_slug__phone_only(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
):
    # Arrange
    site = await wedding_site_factory(slug="phone-rsvp", status=SiteStatus.PUBLISHED)
    # Act
    created = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Sam Guest",
        email=None,
        phone="+306912345678",
        is_attending=True,
        party_size=1,
        notes=None,
    )
    # Assert
    assert created.phone == "+306912345678"
    assert created.email is None


@pytest.mark.asyncio
async def test__submit_for_slug__email_and_phone(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
):
    # Arrange
    site = await wedding_site_factory(slug="both-contact", status=SiteStatus.PUBLISHED)
    # Act
    created = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Jordan Guest",
        email="jordan@example.com",
        phone="+306912345679",
        is_attending=True,
        party_size=1,
        notes=None,
    )
    # Assert
    assert created.email == "jordan@example.com"
    assert created.phone == "+306912345679"


@pytest.mark.asyncio
async def test__submit_for_slug__neither_email_nor_phone(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
):
    # Arrange
    site = await wedding_site_factory(slug="no-contact", status=SiteStatus.PUBLISHED)
    # Act
    with pytest.raises(InvalidRsvpSubmissionError):
        await rsvp_responses_service.submit_for_slug(
            slug=site.slug,
            name="No Contact",
            email=None,
            phone=None,
            is_attending=True,
            party_size=1,
            notes=None,
        )
    # Assert


@pytest.mark.asyncio
async def test__submit_for_slug__is_attending_false_nonzero_party_size(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
):
    # Arrange
    site = await wedding_site_factory(slug="decline-rsvp", status=SiteStatus.PUBLISHED)
    # Act
    with pytest.raises(InvalidRsvpSubmissionError):
        await rsvp_responses_service.submit_for_slug(
            slug=site.slug,
            name="Declining Guest",
            email="decline@example.com",
            phone=None,
            is_attending=False,
            party_size=3,
            notes=None,
        )
    # Assert


@pytest.mark.asyncio
async def test__submit_for_slug__is_attending_false_zero_party_size(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
):
    # Arrange
    site = await wedding_site_factory(slug="decline-rsvp-ok", status=SiteStatus.PUBLISHED)
    # Act
    created = await rsvp_responses_service.submit_for_slug(
        slug=site.slug,
        name="Declining Guest",
        email="decline@example.com",
        phone=None,
        is_attending=False,
        party_size=0,
        notes=None,
    )
    # Assert
    assert created.is_attending is False
    assert created.party_size == 0


@pytest.mark.asyncio
async def test__submit_for_slug__attending_with_zero_party_size(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
):
    # Arrange
    site = await wedding_site_factory(slug="attending-size", status=SiteStatus.PUBLISHED)
    # Act
    with pytest.raises(InvalidRsvpSubmissionError):
        await rsvp_responses_service.submit_for_slug(
            slug=site.slug,
            name="Bad Size",
            email="bad@example.com",
            phone=None,
            is_attending=True,
            party_size=0,
            notes=None,
        )
    # Assert


@pytest.mark.asyncio
async def test__submit_for_slug__unknown_slug(
    rsvp_responses_service: RsvpResponsesService,
):
    # Arrange
    # Act
    with pytest.raises(RsvpWeddingSiteNotFoundError):
        await rsvp_responses_service.submit_for_slug(
            slug="missing-site",
            name="Guest",
            email="guest@example.com",
            phone=None,
            is_attending=True,
            party_size=1,
            notes=None,
        )
    # Assert


@pytest.mark.asyncio
async def test__submit_for_slug__draft_site(
    rsvp_responses_service: RsvpResponsesService,
    wedding_site_factory,
):
    # Arrange
    site = await wedding_site_factory(slug="draft-only")
    # Act
    with pytest.raises(RsvpWeddingSiteNotPublishedError):
        await rsvp_responses_service.submit_for_slug(
            slug=site.slug,
            name="Guest",
            email="guest@example.com",
            phone=None,
            is_attending=True,
            party_size=1,
            notes=None,
        )
    # Assert
