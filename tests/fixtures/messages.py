from datetime import datetime

import pytest_asyncio
from faker import Faker

from domains.messages.models import Message
from domains.messages.repository import MessagesRepository
from domains.messages.service import MessagesService

fake = Faker()


@pytest_asyncio.fixture
async def messages_repository(test_session):
    """Create a MessagesRepository instance for testing."""
    return MessagesRepository(test_session)


@pytest_asyncio.fixture
async def messages_service(messages_repository):
    """Create a MessagesService instance for testing."""
    return MessagesService(messages_repository)


@pytest_asyncio.fixture
async def message_factory(test_session):
    """Factory fixture for creating messages in the test database."""

    async def _create_message(
        content: str | None = None, created_at: datetime | None = None
    ) -> Message:
        if content is None:
            content = fake.text(max_nb_chars=200)

        # Create message directly with optional created_at
        message = Message(content=content)
        if created_at is not None:
            message.created_at = created_at

        test_session.add(message)
        await test_session.commit()
        await test_session.refresh(message)

        return message

    return _create_message
