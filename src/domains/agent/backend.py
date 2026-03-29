from typing import Any


class StubAgentBackend:
    """Placeholder until a real LLM/tool-calling agent is integrated."""

    async def run(self, *, message: str, config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        clipped = message.strip()[:500]
        reply = f'(stub agent) Received: "{clipped}"'
        new_config = {**config, "_stub_last_user_message": clipped}
        return reply, new_config
