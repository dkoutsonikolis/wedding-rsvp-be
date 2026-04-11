from uuid import UUID

from fastapi import Depends, HTTPException, status

from api.agent.schemas import AgentTurnRequest, AgentTurnResponse, ChatHistoryItem
from api.common.dependencies import get_current_user
from domains.agent.dependencies import get_agent_service
from domains.agent.service import AgentService
from domains.users.models import User
from domains.wedding_sites.exceptions import WeddingSiteNotFoundError


async def agent_turn_for_site(
    site_id: UUID,
    body: AgentTurnRequest,
    user: User = Depends(get_current_user),
    agent: AgentService = Depends(get_agent_service),
) -> AgentTurnResponse:
    try:
        reply, new_config, chat_history = await agent.turn(
            owner_user_id=user.id,
            site_id=site_id,
            message=body.message,
            config=body.config,
        )
    except WeddingSiteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return AgentTurnResponse(
        message=reply,
        config=new_config,
        chat_history=[ChatHistoryItem.model_validate(m) for m in chat_history],
        interactions_remaining=None,
    )
