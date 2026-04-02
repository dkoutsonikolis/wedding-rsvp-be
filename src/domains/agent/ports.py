"""Agent port: one turn in, assistant message + site ``config`` out."""

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class AgentTurnResult:
    """Result of one builder-agent turn."""

    assistant_message: str
    config: dict[str, Any]
    """Authoritative full site config to persist after this turn."""
    model_config_patch: dict[str, Any] | None = None
    """Structured model ``config`` field (before merge with tool-mutated state); for logging."""
    llm_usage: dict[str, int] | None = None
    """Token/request counts from the LLM run (PydanticAI ``RunUsage``), when available."""
    tools_used: tuple[str, ...] | None = None
    """Tool names invoked during this turn (model tool calls in order), when tracked."""


class AgentBackend(Protocol):
    async def run(self, *, message: str, config: dict[str, Any]) -> AgentTurnResult:
        """Return assistant text and the persisted site config for this turn."""
        ...
