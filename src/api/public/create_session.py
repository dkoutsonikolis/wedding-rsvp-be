from fastapi import Depends, Request

from api.agent.schemas import ChatHistoryItem, PublicAgentSessionCreateResponse
from config import settings
from domains.agent.dependencies import get_agent_service
from domains.agent.service import AgentService
from middleware.limiter import limiter


@limiter.limit(settings.RATE_LIMIT_PUBLIC_AGENT_SESSION)
async def create_public_agent_session(
    request: Request,
    agent: AgentService = Depends(get_agent_service),
) -> PublicAgentSessionCreateResponse:
    token, config, remaining, chat_history = await agent.create_public_session()
    return PublicAgentSessionCreateResponse(
        session_token=token,
        interactions_remaining=remaining,
        config=config,
        chat_history=[ChatHistoryItem.model_validate(m) for m in chat_history],
    )
