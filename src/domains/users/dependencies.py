from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from db.db import get_session
from domains.anonymous_agent_sessions.repository import AnonymousAgentSessionsRepository
from domains.anonymous_agent_sessions.service import AnonymousAgentSessionsService
from domains.users.repository import UsersRepository
from domains.users.service import UsersService
from domains.wedding_sites.repository import WeddingSitesRepository
from domains.wedding_sites.service import WeddingSitesService


async def get_users_service(session: AsyncSession = Depends(get_session)) -> UsersService:
    return UsersService(
        UsersRepository(session),
        anonymous_sessions_service=AnonymousAgentSessionsService(
            AnonymousAgentSessionsRepository(session)
        ),
        wedding_sites_service=WeddingSitesService(WeddingSitesRepository(session)),
    )
