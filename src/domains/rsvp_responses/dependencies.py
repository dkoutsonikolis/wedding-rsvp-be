from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from db.db import get_session
from domains.rsvp_responses.repository import RsvpResponsesRepository
from domains.rsvp_responses.service import RsvpResponsesService
from domains.wedding_sites.repository import WeddingSitesRepository
from domains.wedding_sites.service import WeddingSitesService


async def get_rsvp_responses_service(
    session: AsyncSession = Depends(get_session),
) -> RsvpResponsesService:
    wedding_sites_service = WeddingSitesService(WeddingSitesRepository(session))
    return RsvpResponsesService(
        RsvpResponsesRepository(session),
        wedding_sites_service,
    )
