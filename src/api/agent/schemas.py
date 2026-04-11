from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentTurnRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    config: dict[str, Any] | None = None


class ChatHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AgentTurnResponse(BaseModel):
    message: str = Field(..., description="Assistant reply for this turn")
    config: dict[str, Any]
    chat_history: list[ChatHistoryItem] = Field(
        default_factory=list,
        description="Full persisted chat for this session or site (same order as stored)",
    )
    interactions_remaining: int | None = Field(
        None,
        description="Remaining trial turns for anonymous sessions only",
    )


class PublicAgentSessionCreateResponse(BaseModel):
    session_token: str
    interactions_remaining: int = 3
    config: dict[str, Any] = Field(default_factory=dict)
    chat_history: list[ChatHistoryItem] = Field(
        default_factory=list,
        description="Persisted trial chat (empty on create)",
    )


class PublicAgentTurnRequest(BaseModel):
    session_token: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=8000)
    config: dict[str, Any] | None = None
