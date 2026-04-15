from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from domains.wedding_sites.enums import SiteStatus


class WeddingSiteCreate(BaseModel):
    slug: str | None = Field(
        default=None,
        description="URL slug; omit to auto-generate from title or a random prefix",
    )
    title: str | None = None
    status: SiteStatus = SiteStatus.DRAFT
    config: dict[str, Any] | None = None
    schema_version: int = 1


class WeddingSiteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str | None
    status: SiteStatus
    config: dict[str, Any]
    schema_version: int
    created_at: datetime
    updated_at: datetime


class WeddingSiteUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    slug: str | None = None
    status: SiteStatus | None = None
    config: dict[str, Any] | None = None
    schema_version: int | None = None


class AgentChatHistoryItem(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime


class AgentChatHistoryPageResponse(BaseModel):
    items: list[AgentChatHistoryItem]
    next_before_message_id: UUID | None = None
