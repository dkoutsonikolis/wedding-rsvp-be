from typing import cast

from fastapi import Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from db.db import get_session
from domains.agent.ports import AgentBackend
from domains.agent.service import AgentService
from domains.anonymous_agent_sessions.repository import AnonymousAgentSessionsRepository
from domains.anonymous_agent_sessions.service import AnonymousAgentSessionsService
from domains.wedding_sites.repository import WeddingSitesRepository
from domains.wedding_sites.service import WeddingSitesService


def get_agent_backend(request: Request) -> AgentBackend:
    return cast(AgentBackend, request.app.state.agent_backend)


async def get_agent_service(
    session: AsyncSession = Depends(get_session),
    backend: AgentBackend = Depends(get_agent_backend),
) -> AgentService:
    return AgentService(
        AnonymousAgentSessionsService(AnonymousAgentSessionsRepository(session)),
        WeddingSitesService(WeddingSitesRepository(session)),
        backend=backend,
    )
