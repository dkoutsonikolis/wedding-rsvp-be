from typing import Any, Protocol


class AgentBackend(Protocol):
    async def run(self, *, message: str, config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Return assistant text and the persisted site config for this turn."""
        ...


class StubAgentBackend:
    """Offline backend for tests and local runs without GOOGLE_API_KEY."""

    async def run(self, *, message: str, config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        clipped = message.strip()[:500]
        reply = f'(stub agent) Received: "{clipped}"'
        new_config = {**config, "_stub_last_user_message": clipped}
        return reply, new_config
