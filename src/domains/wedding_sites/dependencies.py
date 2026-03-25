from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from db.db import get_session
from domains.wedding_sites.repository import WeddingSitesRepository
from domains.wedding_sites.service import WeddingSitesService


async def get_wedding_sites_service(
    session: AsyncSession = Depends(get_session),
) -> WeddingSitesService:
    return WeddingSitesService(WeddingSitesRepository(session))
