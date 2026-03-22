from fastapi import Depends

from domains.messages.dependencies import get_messages_service
from domains.messages.service import MessagesService

from .schemas import MessageCreate, MessageRead


async def create_message(
    message_in: MessageCreate, service: MessagesService = Depends(get_messages_service)
) -> MessageRead:
    """Create a new message."""
    message = await service.create_message(message_in.content)
    return MessageRead.model_validate(message)
