from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status

from api.agent.schemas import AgentSessionStateResponse, ChatHistoryItem
from config import settings
from domains.agent.dependencies import get_agent_service
from domains.agent.service import AgentService
from domains.anonymous_agent_sessions.exceptions import (
    AnonymousSessionExpiredError,
    AnonymousSessionNotFoundError,
)
from middleware.limiter import limiter


@limiter.limit(settings.RATE_LIMIT_PUBLIC_AGENT_TURN)
async def get_public_agent_session_state(
    request: Request,
    session_token: Annotated[str, Header(alias="X-Session-Token", min_length=1)],
    agent: AgentService = Depends(get_agent_service),
) -> AgentSessionStateResponse:
    try:
        config, remaining, chat_history = await agent.public_session_state(
            session_token=session_token
        )
    except AnonymousSessionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    except AnonymousSessionExpiredError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    return AgentSessionStateResponse(
        config=config,
        chat_history=[ChatHistoryItem.model_validate(message) for message in chat_history],
        interactions_remaining=remaining,
    )
