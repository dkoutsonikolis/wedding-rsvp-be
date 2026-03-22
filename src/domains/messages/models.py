from datetime import datetime

from sqlmodel import Field, SQLModel

from utils import utc_now


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=utc_now)
