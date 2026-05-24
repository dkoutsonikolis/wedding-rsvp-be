import pytest_asyncio

from domains.rsvp_responses.repository import RsvpResponsesRepository
from domains.rsvp_responses.service import RsvpResponsesService
from domains.wedding_sites.service import WeddingSitesService


@pytest_asyncio.fixture
async def rsvp_responses_repository(test_session):
    return RsvpResponsesRepository(test_session)


@pytest_asyncio.fixture
async def rsvp_responses_service(
    rsvp_responses_repository: RsvpResponsesRepository,
    wedding_sites_service: WeddingSitesService,
) -> RsvpResponsesService:
    return RsvpResponsesService(rsvp_responses_repository, wedding_sites_service)
