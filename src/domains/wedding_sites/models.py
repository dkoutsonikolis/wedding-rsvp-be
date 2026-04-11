from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, SQLModel

from domains.wedding_sites.enums import AgentMessageRole, SiteStatus
from utils import utc_now


class WeddingSite(SQLModel, table=True):
    __tablename__ = "wedding_sites"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    owner_user_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    slug: str = Field(unique=True, index=True)
    title: str | None = Field(default=None)
    status: SiteStatus = Field(default=SiteStatus.DRAFT)
    config: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    schema_version: int = Field(default=1)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class AgentConversationMessage(SQLModel, table=True):
    """A single user or assistant line in the builder chat (authenticated site only)."""

    __tablename__ = "agent_conversation_messages"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant')",
            name="ck_agent_conversation_messages_role",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    wedding_site_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("wedding_sites.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
    )
    role: AgentMessageRole = Field(sa_column=Column(String(length=16), nullable=False))
    content: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=utc_now)
