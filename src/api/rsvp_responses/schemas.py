from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from domains.rsvp_responses.constants import PARTY_SIZE_MAX

NOTES_MAX_LENGTH = 2000


class RsvpSubmitRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    is_attending: bool
    party_size: int = Field(default=1, ge=0, le=PARTY_SIZE_MAX)
    notes: str | None = Field(default=None, max_length=NOTES_MAX_LENGTH)

    @model_validator(mode="after")
    def email_or_phone_required(self) -> Self:
        if self.email is None and self.phone is None:
            raise ValueError("At least one of email or phone is required")
        return self


class RsvpResponseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str | None
    phone: str | None
    is_attending: bool
    party_size: int
    notes: str | None
    created_at: datetime


class RsvpResponsesPageResponse(BaseModel):
    items: list[RsvpResponseRead]
    next_before_response_id: UUID | None = None
