from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, SQLModel

from domains.rsvp_responses.constants import PARTY_SIZE_MAX
from utils import utc_now


class RsvpResponse(SQLModel, table=True):
    __tablename__ = "rsvp_responses"
    __table_args__ = (
        CheckConstraint(
            f"(is_attending IS TRUE AND party_size >= 1 AND party_size <= {PARTY_SIZE_MAX}) "
            f"OR (is_attending IS FALSE AND party_size = 0)",
            name="ck_rsvp_responses_attending_party_size",
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
    name: str = Field(sa_column=Column(String(length=100), nullable=False))
    email: str | None = Field(
        default=None,
        sa_column=Column(String(length=254), nullable=True),
    )
    phone: str | None = Field(
        default=None,
        sa_column=Column(String(length=20), nullable=True),
    )
    is_attending: bool = Field(sa_column=Column(Boolean(), nullable=False))
    party_size: int = Field(
        le=PARTY_SIZE_MAX,
        sa_column=Column(Integer(), nullable=False),
    )
    notes: str | None = Field(
        default=None,
        sa_column=Column(Text(), nullable=True),
    )
    created_at: datetime = Field(default_factory=utc_now)
