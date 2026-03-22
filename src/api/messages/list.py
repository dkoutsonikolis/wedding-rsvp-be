from fastapi import Depends

from domains.messages.dependencies import get_messages_service
from domains.messages.service import MessagesService

from .schemas import MessageRead


async def list_messages(
    service: MessagesService = Depends(get_messages_service),
) -> list[MessageRead]:
    """List all messages."""
    messages = await service.list_messages()
    return [MessageRead.model_validate(m) for m in messages]
