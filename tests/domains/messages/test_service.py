import pytest

from domains.messages.models import Message
from domains.messages.service import MessagesService


@pytest.mark.asyncio
async def test__list_messages__repository_empty(messages_service: MessagesService):
    # Arrange
    # (empty DB via fixtures)
    # Act
    messages = await messages_service.list_messages()
    # Assert
    assert messages == []
    assert isinstance(messages, list)


@pytest.mark.asyncio
async def test__list_messages__two_committed_rows(
    messages_service: MessagesService, message_factory
):
    # Arrange
    await message_factory(content="First message")
    await message_factory(content="Second message")
    # Act
    messages = await messages_service.list_messages()
    # Assert
    assert len(messages) == 2
    assert isinstance(messages[0], Message)
    assert isinstance(messages[1], Message)
    contents = [msg.content for msg in messages]
    assert "First message" in contents
    assert "Second message" in contents


@pytest.mark.asyncio
async def test__create_message__arbitrary_text(messages_service: MessagesService):
    # Arrange
    text = "Test message content"
    # Act
    message = await messages_service.create_message(text)
    # Assert
    assert isinstance(message, Message)
    assert message.content == text
    assert message.id is not None
    assert message.created_at is not None


@pytest.mark.asyncio
async def test__create_message__visible_in_subsequent_list(messages_service: MessagesService):
    # Arrange
    created_message = await messages_service.create_message("Persisted message")
    assert created_message.id is not None
    # Act
    messages = await messages_service.list_messages()
    # Assert
    assert len(messages) == 1
    assert messages[0].id == created_message.id
    assert messages[0].content == "Persisted message"
