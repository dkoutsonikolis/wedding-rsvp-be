from domains.messages.models import Message
from domains.messages.repository import MessagesRepository
from utils.logging import get_logger

logger = get_logger(__name__)


class MessagesService:
    def __init__(self, repository: MessagesRepository):
        self.repository = repository

    async def list_messages(self) -> list[Message]:
        return await self.repository.get_all()

    async def create_message(self, content: str) -> Message:
        try:
            return await self.repository.create(content)
        except Exception as e:
            logger.error(f"Failed to create message: {e}", exc_info=True)
            raise
