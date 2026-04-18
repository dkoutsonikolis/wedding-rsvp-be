from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from domains.contact.models import ContactSubmission


@pytest.mark.asyncio
async def test__submit_contact_message__anonymous_submission_accepted(
    client: AsyncClient, test_session: AsyncSession
):
    # Arrange
    payload = {
        "name": "Guest User",
        "email": "guest@example.com",
        "subject": "Question about pricing",
        "message": "Can you share your pricing tiers?",
    }
    # Act
    response = await client.post("/api/v1/public/contact", json=payload)
    # Assert
    assert response.status_code == 204
    rows = (
        await test_session.exec(
            select(ContactSubmission).where(ContactSubmission.email == "guest@example.com")
        )
    ).all()
    assert len(rows) == 1
    assert rows[0].user_id is None
    assert rows[0].subject == "Question about pricing"


@pytest.mark.asyncio
async def test__submit_contact_message__authenticated_submission_uses_account_email(
    client: AsyncClient,
    test_session: AsyncSession,
):
    # Arrange
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": "member@example.com", "password": "password123"},
    )
    token = register.json()["access_token"]
    payload = {
        "name": "Member User",
        "email": "different@example.com",
        "subject": "Account support",
        "message": "I need help with my site.",
    }
    # Act
    response = await client.post(
        "/api/v1/public/contact",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    # Assert
    assert response.status_code == 204
    rows = (
        await test_session.exec(
            select(ContactSubmission).where(ContactSubmission.email == "member@example.com")
        )
    ).all()
    assert len(rows) == 1
    assert rows[0].user_id == UUID(register.json()["user"]["id"])
    assert rows[0].subject == "Account support"


@pytest.mark.asyncio
async def test__submit_contact_message__invalid_bearer_token(client: AsyncClient):
    # Arrange
    payload = {
        "name": "Bad Token",
        "email": "guest@example.com",
        "subject": "Token test",
        "message": "This should fail due to auth header.",
    }
    # Act
    response = await client.post(
        "/api/v1/public/contact",
        json=payload,
        headers={"Authorization": "Bearer invalid-token"},
    )
    # Assert
    assert response.status_code == 401
