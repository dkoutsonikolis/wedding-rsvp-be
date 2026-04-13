import uuid

import pytest_asyncio
from httpx import AsyncClient

from domains.anonymous_agent_sessions.repository import AnonymousAgentSessionsRepository
from domains.anonymous_agent_sessions.service import AnonymousAgentSessionsService
from domains.users.repository import UsersRepository
from domains.users.service import UsersService
from domains.wedding_sites.repository import WeddingSitesRepository
from domains.wedding_sites.service import WeddingSitesService


@pytest_asyncio.fixture
async def users_repository(test_session):
    return UsersRepository(test_session)


@pytest_asyncio.fixture
async def users_service(users_repository):
    return UsersService(
        users_repository,
        anonymous_sessions_service=AnonymousAgentSessionsService(
            AnonymousAgentSessionsRepository(users_repository.session)
        ),
        wedding_sites_service=WeddingSitesService(WeddingSitesRepository(users_repository.session)),
    )


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """Register a user and return Authorization headers for API tests."""
    email = f"user-{uuid.uuid4().hex[:12]}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
