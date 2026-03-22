# dependencies.py
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from db.db import get_session
from domains.messages.repository import MessagesRepository
from domains.messages.service import MessagesService


async def get_messages_service(session: AsyncSession = Depends(get_session)) -> MessagesService:
    repo = MessagesRepository(session)  # session is already AsyncSession
    return MessagesService(repo)
