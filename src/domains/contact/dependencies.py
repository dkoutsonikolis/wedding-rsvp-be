from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from db.db import get_session
from domains.contact.repository import ContactRepository
from domains.contact.service import ContactService


async def get_contact_service(session: AsyncSession = Depends(get_session)) -> ContactService:
    return ContactService(ContactRepository(session))
