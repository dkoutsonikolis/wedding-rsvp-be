from typing import Any


class StubAgentBackend:
    """Offline backend for tests and runs without a live LLM (see ``factory.build_agent_backend``)."""

    async def run(self, *, message: str, config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        clipped = message.strip()[:500]
        reply = f'(stub agent) Received: "{clipped}"'
        new_config = {**config, "_stub_last_user_message": clipped}
        return reply, new_config
