from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from domains.messages.models import Message


class MessagesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Message]:
        result = await self.session.exec(select(Message).order_by(Message.id))  # type: ignore[arg-type]
        return list(result.all())

    async def create(self, content: str) -> Message:
        message = Message(content=content)
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)  # reload the object with DB defaults
        return message
