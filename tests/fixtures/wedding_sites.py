from uuid import UUID

import pytest_asyncio

from domains.users.password import hash_password
from domains.users.repository import UsersRepository
from domains.wedding_sites.enums import SiteStatus
from domains.wedding_sites.models import WeddingSite
from domains.wedding_sites.repository import WeddingSitesRepository
from domains.wedding_sites.service import WeddingSitesService


@pytest_asyncio.fixture
async def wedding_sites_repository(test_session):
    return WeddingSitesRepository(test_session)


@pytest_asyncio.fixture
async def wedding_sites_service(wedding_sites_repository):
    return WeddingSitesService(wedding_sites_repository)


@pytest_asyncio.fixture
async def site_owner_user_id(test_session) -> UUID:
    repo = UsersRepository(test_session)
    user = await repo.create(
        email="site-owner@example.com", password_hash=hash_password("secret123")
    )
    return user.id


@pytest_asyncio.fixture
async def other_user_id(test_session) -> UUID:
    repo = UsersRepository(test_session)
    user = await repo.create(
        email="other-user@example.com", password_hash=hash_password("secret123")
    )
    return user.id


@pytest_asyncio.fixture
async def wedding_site_factory(
    wedding_sites_service: WeddingSitesService, site_owner_user_id: UUID
):
    async def _create(
        *,
        slug: str = "my-wedding",
        title: str | None = "Our day",
        status: SiteStatus = SiteStatus.DRAFT,
        owner_user_id: UUID | None = None,
    ) -> WeddingSite:
        return await wedding_sites_service.create(
            owner_user_id=owner_user_id or site_owner_user_id,
            title=title,
            slug=slug,
            status=status,
        )

    return _create
