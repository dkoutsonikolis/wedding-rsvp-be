import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from config import settings
from db.db import get_session
from domains.agent.factory import build_agent_backend
from main import app


@pytest_asyncio.fixture
async def client(test_session):
    """Create a test client with overridden database session."""

    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session
    # ASGITransport does not run FastAPI lifespan; mirror startup wiring.
    app.state.agent_backend = build_agent_backend(settings)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    # Cleanup
    app.dependency_overrides.clear()
