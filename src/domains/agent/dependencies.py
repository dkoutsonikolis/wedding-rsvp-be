from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from db.db import get_session
from domains.agent.service import AgentService
from domains.anonymous_agent_sessions.repository import AnonymousAgentSessionsRepository
from domains.anonymous_agent_sessions.service import AnonymousAgentSessionsService
from domains.wedding_sites.repository import WeddingSitesRepository
from domains.wedding_sites.service import WeddingSitesService


async def get_agent_service(session: AsyncSession = Depends(get_session)) -> AgentService:
    return AgentService(
        AnonymousAgentSessionsService(AnonymousAgentSessionsRepository(session)),
        WeddingSitesService(WeddingSitesRepository(session)),
    )
