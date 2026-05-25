from uuid import UUID

from fastapi import Depends, HTTPException, status

from api.common.dependencies import get_current_user
from api.rsvp_responses.schemas import RsvpResponseRead, RsvpResponsesSummaryResponse
from domains.rsvp_responses.dependencies import get_rsvp_responses_service
from domains.rsvp_responses.service import RsvpResponsesService
from domains.users.models import User
from domains.wedding_sites.exceptions import WeddingSiteNotFoundError


async def get_wedding_site_rsvp_responses_summary(
    site_id: UUID,
    current_user: User = Depends(get_current_user),
    rsvp_responses_service: RsvpResponsesService = Depends(get_rsvp_responses_service),
) -> RsvpResponsesSummaryResponse:
    try:
        summary = await rsvp_responses_service.summary_for_owner(
            site_id=site_id,
            owner_user_id=current_user.id,
        )
    except WeddingSiteNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return RsvpResponsesSummaryResponse(
        attending_count=summary.attending_count,
        declined_count=summary.declined_count,
        total_guests=summary.total_guests,
        total_responses=summary.total_responses,
        recent_activity=[RsvpResponseRead.model_validate(row) for row in summary.recent_activity],
        guest_notes=[RsvpResponseRead.model_validate(row) for row in summary.guest_notes],
    )
