from fastapi import Depends, HTTPException, Request, status

from api.rsvp_responses.schemas import RsvpResponseRead, RsvpSubmitRequest
from config import settings
from domains.rsvp_responses.dependencies import get_rsvp_responses_service
from domains.rsvp_responses.exceptions import (
    InvalidRsvpSubmissionError,
    RsvpWeddingSiteNotFoundError,
    RsvpWeddingSiteNotPublishedError,
)
from domains.rsvp_responses.service import RsvpResponsesService
from middleware.limiter import limiter


@limiter.limit(settings.RATE_LIMIT_PUBLIC_RSVP)
async def submit_rsvp(
    request: Request,
    slug: str,
    body: RsvpSubmitRequest,
    rsvp_responses_service: RsvpResponsesService = Depends(get_rsvp_responses_service),
) -> RsvpResponseRead:
    try:
        created = await rsvp_responses_service.submit_for_slug(
            slug=slug,
            name=body.name,
            email=str(body.email) if body.email is not None else None,
            phone=body.phone,
            is_attending=body.is_attending,
            party_size=body.party_size,
            notes=body.notes,
        )
    except (RsvpWeddingSiteNotFoundError, RsvpWeddingSiteNotPublishedError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidRsvpSubmissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    return RsvpResponseRead.model_validate(created)
