from dataclasses import dataclass
from uuid import UUID

from domains.rsvp_responses.constants import (
    PARTY_SIZE_MAX,
    RSVP_RESPONSES_PAGE_MAX_LIMIT,
    RSVP_SUMMARY_GUEST_NOTES_LIMIT,
    RSVP_SUMMARY_RECENT_LIMIT,
)
from domains.rsvp_responses.exceptions import (
    InvalidRsvpSubmissionError,
    RsvpWeddingSiteNotFoundError,
    RsvpWeddingSiteNotPublishedError,
)
from domains.rsvp_responses.models import RsvpResponse
from domains.rsvp_responses.repository import RsvpResponsesRepository
from domains.wedding_sites.enums import SiteStatus
from domains.wedding_sites.service import WeddingSitesService
from utils.logging import get_logger

logger = get_logger(__name__)

NOTES_MAX_LENGTH = 2000


@dataclass(frozen=True)
class RsvpOwnerSummary:
    attending_count: int
    declined_count: int
    total_guests: int
    total_responses: int
    recent_activity: list[RsvpResponse]
    guest_notes: list[RsvpResponse]


class RsvpResponsesService:
    def __init__(
        self,
        repository: RsvpResponsesRepository,
        wedding_sites_service: WeddingSitesService,
    ):
        self.repository = repository
        self.wedding_sites_service = wedding_sites_service

    @staticmethod
    def _normalize_optional_text(value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    def _normalize_submission(
        self,
        email: str | None,
        phone: str | None,
        is_attending: bool,
        party_size: int,
        notes: str | None,
    ) -> tuple[str | None, str | None, int, str | None]:
        normalized_email = self._normalize_optional_text(email)
        normalized_phone = self._normalize_optional_text(phone)
        if normalized_email is None and normalized_phone is None:
            raise InvalidRsvpSubmissionError("At least one of email or phone is required")

        normalized_notes = self._normalize_optional_text(notes)
        if normalized_notes is not None and len(normalized_notes) > NOTES_MAX_LENGTH:
            raise InvalidRsvpSubmissionError(f"notes must be at most {NOTES_MAX_LENGTH} characters")

        if is_attending:
            if party_size < 1:
                raise InvalidRsvpSubmissionError("party_size must be at least 1 when attending")
            if party_size > PARTY_SIZE_MAX:
                raise InvalidRsvpSubmissionError(f"party_size must be at most {PARTY_SIZE_MAX}")
            stored_party_size = party_size
        elif party_size != 0:
            raise InvalidRsvpSubmissionError("party_size must be 0 when not attending")
        else:
            stored_party_size = 0

        return normalized_email, normalized_phone, stored_party_size, normalized_notes

    async def submit_for_slug(
        self,
        slug: str,
        name: str,
        email: str | None,
        phone: str | None,
        is_attending: bool,
        party_size: int,
        notes: str | None,
    ) -> RsvpResponse:
        normalized_slug = slug.strip().lower()
        site = await self.wedding_sites_service.get_by_slug(normalized_slug)
        if site is None:
            raise RsvpWeddingSiteNotFoundError("Wedding site not found")
        if site.status != SiteStatus.PUBLISHED:
            raise RsvpWeddingSiteNotPublishedError("Wedding site is not published")

        normalized_name = self._normalize_optional_text(name)
        if normalized_name is None:
            raise InvalidRsvpSubmissionError("name is required")

        (
            normalized_email,
            normalized_phone,
            stored_party_size,
            normalized_notes,
        ) = self._normalize_submission(
            email=email,
            phone=phone,
            is_attending=is_attending,
            party_size=party_size,
            notes=notes,
        )

        response = RsvpResponse(
            wedding_site_id=site.id,
            name=normalized_name,
            email=normalized_email,
            phone=normalized_phone,
            is_attending=is_attending,
            party_size=stored_party_size,
            notes=normalized_notes,
        )
        created = await self.repository.create(response)
        logger.info(
            "RSVP response stored (id=%s, wedding_site_id=%s, is_attending=%s, party_size=%s)",
            created.id,
            created.wedding_site_id,
            created.is_attending,
            created.party_size,
        )
        return created

    async def list_page_for_owner(
        self,
        site_id: UUID,
        owner_user_id: UUID,
        limit: int,
        before_response_id: UUID | None = None,
        q: str | None = None,
        is_attending: bool | None = None,
    ) -> tuple[list[RsvpResponse], UUID | None]:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        if limit > RSVP_RESPONSES_PAGE_MAX_LIMIT:
            raise ValueError(f"limit must be at most {RSVP_RESPONSES_PAGE_MAX_LIMIT}")

        await self.wedding_sites_service.get_by_id_for_user(
            site_id=site_id,
            owner_user_id=owner_user_id,
        )
        search_query = self._normalize_optional_text(q)
        rows = await self.repository.list_by_wedding_site_id(
            wedding_site_id=site_id,
            limit=limit + 1,
            before_response_id=before_response_id,
            q=search_query,
            is_attending=is_attending,
        )
        if len(rows) <= limit:
            return rows, None
        page_rows = rows[:limit]
        next_before_response_id = page_rows[-1].id
        return page_rows, next_before_response_id

    async def summary_for_owner(
        self,
        site_id: UUID,
        owner_user_id: UUID,
    ) -> RsvpOwnerSummary:
        await self.wedding_sites_service.get_by_id_for_user(
            site_id=site_id,
            owner_user_id=owner_user_id,
        )
        (
            total_responses,
            attending_count,
            declined_count,
            total_guests,
        ) = await self.repository.get_summary_counts_for_wedding_site_id(site_id)
        recent_activity = await self.repository.list_recent_by_wedding_site_id(
            wedding_site_id=site_id,
            limit=RSVP_SUMMARY_RECENT_LIMIT,
        )
        guest_notes = await self.repository.list_with_notes_by_wedding_site_id(
            wedding_site_id=site_id,
            limit=RSVP_SUMMARY_GUEST_NOTES_LIMIT,
        )
        return RsvpOwnerSummary(
            attending_count=attending_count,
            declined_count=declined_count,
            total_guests=total_guests,
            total_responses=total_responses,
            recent_activity=recent_activity,
            guest_notes=guest_notes,
        )
