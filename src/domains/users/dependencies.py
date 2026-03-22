from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from db.db import get_session
from domains.users.repository import UsersRepository
from domains.users.service import UsersService


async def get_users_service(session: AsyncSession = Depends(get_session)) -> UsersService:
    return UsersService(UsersRepository(session))
