from collections.abc import Sequence
from typing import Any

from domains.agent.ports import AgentTurnResult


class StubAgentBackend:
    """Offline backend for tests and runs without a live LLM (see ``factory.build_agent_backend``)."""

    async def run(
        self,
        *,
        message: str,
        config: dict[str, Any],
        conversation_history: Sequence[dict[str, str]] | None = None,
    ) -> AgentTurnResult:
        clipped = message.strip()[:500]
        reply = f'(stub agent) Received: "{clipped}"'
        new_config = {**config, "_stub_last_user_message": clipped}
        return AgentTurnResult(
            assistant_message=reply,
            config=new_config,
            model_config_patch={"_stub_last_user_message": clipped},
        )
