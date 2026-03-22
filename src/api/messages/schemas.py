from datetime import datetime

from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class MessageRead(BaseModel):
    """HTTP representation of a message (decoupled from the ORM table)."""

    model_config = {"from_attributes": True}

    id: int
    content: str
    created_at: datetime
