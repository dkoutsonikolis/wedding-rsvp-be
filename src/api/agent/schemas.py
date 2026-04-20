from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from config import settings


class AgentTurnRequest(BaseModel):
    message: str = Field(..., min_length=1)
    config: dict[str, Any] | None = None

    @field_validator("message")
    @classmethod
    def validate_message_length(cls, value: str) -> str:
        trimmed = value.strip()
        if len(trimmed) > settings.AGENT_USER_MESSAGE_MAX_CHARS:
            raise ValueError(
                f"message must be at most {settings.AGENT_USER_MESSAGE_MAX_CHARS} characters"
            )
        return trimmed


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


class AgentSessionStateResponse(BaseModel):
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
    message: str = Field(..., min_length=1)
    config: dict[str, Any] | None = None

    @field_validator("message")
    @classmethod
    def validate_message_length(cls, value: str) -> str:
        trimmed = value.strip()
        if len(trimmed) > settings.AGENT_ANON_MESSAGE_MAX_CHARS:
            raise ValueError(
                f"message must be at most {settings.AGENT_ANON_MESSAGE_MAX_CHARS} characters"
            )
        return trimmed
