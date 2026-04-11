from fastapi import Depends, HTTPException, Request, status

from api.agent.schemas import AgentTurnResponse, ChatHistoryItem, PublicAgentTurnRequest
from config import settings
from domains.agent.dependencies import get_agent_service
from domains.agent.service import AgentService
from domains.anonymous_agent_sessions.exceptions import (
    AnonymousSessionExpiredError,
    AnonymousSessionNotFoundError,
    AnonymousTrialLimitExceededError,
)
from middleware.limiter import limiter


@limiter.limit(settings.RATE_LIMIT_PUBLIC_AGENT_TURN)
async def public_agent_turn(
    request: Request,
    body: PublicAgentTurnRequest,
    agent: AgentService = Depends(get_agent_service),
) -> AgentTurnResponse:
    try:
        reply, new_config, remaining, chat_history = await agent.public_turn(
            session_token=body.session_token,
            message=body.message,
            config=body.config,
        )
    except AnonymousSessionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    except AnonymousSessionExpiredError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    except AnonymousTrialLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
    return AgentTurnResponse(
        message=reply,
        config=new_config,
        chat_history=[ChatHistoryItem.model_validate(m) for m in chat_history],
        interactions_remaining=remaining,
    )
