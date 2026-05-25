from uuid import UUID

from fastapi import Depends, HTTPException, Query, status

from api.common.dependencies import get_current_user
from api.rsvp_responses.schemas import RsvpResponseRead, RsvpResponsesPageResponse
from domains.rsvp_responses.constants import (
    RSVP_RESPONSES_PAGE_DEFAULT_LIMIT,
    RSVP_RESPONSES_PAGE_MAX_LIMIT,
)
from domains.rsvp_responses.dependencies import get_rsvp_responses_service
from domains.rsvp_responses.service import RsvpResponsesService
from domains.users.models import User
from domains.wedding_sites.exceptions import WeddingSiteNotFoundError


async def list_wedding_site_rsvp_responses(
    site_id: UUID,
    limit: int = Query(
        default=RSVP_RESPONSES_PAGE_DEFAULT_LIMIT,
        ge=1,
        le=RSVP_RESPONSES_PAGE_MAX_LIMIT,
    ),
    before_response_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    rsvp_responses_service: RsvpResponsesService = Depends(get_rsvp_responses_service),
) -> RsvpResponsesPageResponse:
    try:
        rows, next_before_response_id = await rsvp_responses_service.list_page_for_owner(
            site_id=site_id,
            owner_user_id=current_user.id,
            limit=limit,
            before_response_id=before_response_id,
        )
    except WeddingSiteNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return RsvpResponsesPageResponse(
        items=[RsvpResponseRead.model_validate(row) for row in rows],
        next_before_response_id=next_before_response_id,
    )
