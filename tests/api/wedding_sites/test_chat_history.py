import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test__get_wedding_site_chat_history__returns_recent_messages_and_cursor(
    client: AsyncClient, auth_headers: dict[str, str]
):
    # Arrange
    created = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json={"slug": "owner-chat-history"},
    )
    assert created.status_code == 201
    site_id = created.json()["id"]
    first_turn = await client.post(
        f"/api/v1/wedding-sites/{site_id}/agent/turn",
        headers=auth_headers,
        json={"message": "first message"},
    )
    assert first_turn.status_code == 200
    second_turn = await client.post(
        f"/api/v1/wedding-sites/{site_id}/agent/turn",
        headers=auth_headers,
        json={"message": "second message"},
    )
    assert second_turn.status_code == 200
    # Act
    response = await client.get(
        f"/api/v1/wedding-sites/{site_id}/chat-history",
        headers=auth_headers,
        params={"limit": 2},
    )
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["role"] == "user"
    assert data["items"][0]["content"] == "second message"
    assert data["items"][1]["role"] == "assistant"
    assert data["items"][1]["content"] == second_turn.json()["message"]
    assert data["next_before_message_id"] is not None


@pytest.mark.asyncio
async def test__get_wedding_site_chat_history__before_message_id_returns_previous_page(
    client: AsyncClient, auth_headers: dict[str, str]
):
    # Arrange
    created = await client.post(
        "/api/v1/wedding-sites",
        headers=auth_headers,
        json={"slug": "owner-chat-history-before-id"},
    )
    assert created.status_code == 201
    site_id = created.json()["id"]
    first_turn = await client.post(
        f"/api/v1/wedding-sites/{site_id}/agent/turn",
        headers=auth_headers,
        json={"message": "first message"},
    )
    assert first_turn.status_code == 200
    second_turn = await client.post(
        f"/api/v1/wedding-sites/{site_id}/agent/turn",
        headers=auth_headers,
        json={"message": "second message"},
    )
    assert second_turn.status_code == 200
    newest_page = await client.get(
        f"/api/v1/wedding-sites/{site_id}/chat-history",
        headers=auth_headers,
        params={"limit": 2},
    )
    before_id = newest_page.json()["next_before_message_id"]
    # Act
    older_page = await client.get(
        f"/api/v1/wedding-sites/{site_id}/chat-history",
        headers=auth_headers,
        params={"limit": 2, "before_message_id": before_id},
    )
    # Assert
    assert older_page.status_code == 200
    data = older_page.json()
    assert data["items"] == [
        {
            "id": data["items"][0]["id"],
            "role": "user",
            "content": "first message",
            "created_at": data["items"][0]["created_at"],
        },
        {
            "id": data["items"][1]["id"],
            "role": "assistant",
            "content": first_turn.json()["message"],
            "created_at": data["items"][1]["created_at"],
        },
    ]
    assert data["next_before_message_id"] is None
