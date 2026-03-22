import pytest_asyncio

from domains.users.repository import UsersRepository
from domains.users.service import UsersService


@pytest_asyncio.fixture
async def users_repository(test_session):
    return UsersRepository(test_session)


@pytest_asyncio.fixture
async def users_service(users_repository):
    return UsersService(users_repository)
