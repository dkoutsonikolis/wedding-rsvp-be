from typing import Any

from pydantic import BaseModel, Field


class AgentTurnRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    config: dict[str, Any] | None = None


class AgentTurnResponse(BaseModel):
    message: str = Field(..., description="Assistant reply (stub until LLM is wired)")
    config: dict[str, Any]
    interactions_remaining: int | None = Field(
        None,
        description="Remaining trial turns for anonymous sessions only",
    )


class PublicAgentSessionCreateResponse(BaseModel):
    session_token: str
    interactions_remaining: int = 3
    config: dict[str, Any] = Field(default_factory=dict)


class PublicAgentTurnRequest(BaseModel):
    session_token: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=8000)
    config: dict[str, Any] | None = None
