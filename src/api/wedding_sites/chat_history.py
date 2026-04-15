from uuid import UUID

from fastapi import Depends, HTTPException, Query, status

from api.common.dependencies import get_current_user
from domains.users.models import User
from domains.wedding_sites.dependencies import get_wedding_sites_service
from domains.wedding_sites.exceptions import WeddingSiteNotFoundError
from domains.wedding_sites.service import WeddingSitesService

from .schemas import AgentChatHistoryItem, AgentChatHistoryPageResponse


async def get_wedding_site_chat_history(
    site_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    before_message_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    service: WeddingSitesService = Depends(get_wedding_sites_service),
) -> AgentChatHistoryPageResponse:
    try:
        rows, next_before_message_id = await service.list_agent_chat_history_page_for_site(
            site_id=site_id,
            owner_user_id=current_user.id,
            limit=limit,
            before_message_id=before_message_id,
        )
    except WeddingSiteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return AgentChatHistoryPageResponse(
        items=[
            AgentChatHistoryItem(
                id=row.id,
                role=str(row.role),
                content=row.content,
                created_at=row.created_at,
            )
            for row in rows
        ],
        next_before_message_id=next_before_message_id,
    )
