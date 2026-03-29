"""Agent port: one turn in, assistant message + site ``config`` out."""

from typing import Any, Protocol


class AgentBackend(Protocol):
    async def run(self, *, message: str, config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Return assistant text and the persisted site config for this turn."""
        ...
