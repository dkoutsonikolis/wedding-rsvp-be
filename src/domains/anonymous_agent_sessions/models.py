from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from utils import utc_now


class AnonymousAgentSession(SQLModel, table=True):
    __tablename__ = "anonymous_agent_sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    token_hash: str = Field(unique=True, index=True, max_length=64)
    interaction_count: int = Field(default=0, ge=0)
    config: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    expires_at: datetime
