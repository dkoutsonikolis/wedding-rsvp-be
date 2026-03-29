from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from db.db import get_session
from domains.anonymous_agent_sessions.repository import AnonymousAgentSessionsRepository
from domains.anonymous_agent_sessions.service import AnonymousAgentSessionsService


async def get_anonymous_agent_sessions_service(
    session: AsyncSession = Depends(get_session),
) -> AnonymousAgentSessionsService:
    return AnonymousAgentSessionsService(AnonymousAgentSessionsRepository(session))
