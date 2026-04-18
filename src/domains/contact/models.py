from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, SQLModel

from utils import utc_now


class ContactSubmission(SQLModel, table=True):
    __tablename__ = "contact_submissions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID | None = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
    )
    name: str = Field(sa_column=Column(String(length=120), nullable=False))
    email: str = Field(sa_column=Column(String(length=320), nullable=False))
    subject: str = Field(sa_column=Column(String(length=200), nullable=False))
    message: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=utc_now)
