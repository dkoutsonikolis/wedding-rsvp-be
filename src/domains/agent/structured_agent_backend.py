"""Structured LLM turn flow: assistant reply plus full site ``config`` (implementation uses Pydantic AI)."""

import json
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models import Model

from domains.agent.ports import AgentBackend
from domains.agent.prompts import default_wedding_builder_system_prompt
from utils.logging import get_logger

logger = get_logger(__name__)

# Builder chat is usually short; cap limits cost/context vs. full `config` JSON in the same turn.
_MAX_USER_CHARS = 4000

DEFAULT_WEDDING_AGENT_SYSTEM_PROMPT = default_wedding_builder_system_prompt()


class _TurnOutput(BaseModel):
    assistant_message: str = Field(description="Reply shown in the builder chat (plain text).")
    config: dict[str, Any] = Field(description="Complete updated site configuration object.")


class StructuredAgentBackend(AgentBackend):
    """
    Base wedding-builder agent: one user turn → chat reply + updated ``config`` JSON.

    Construct via provider helpers (e.g. ``structured_agent_backend_from_gemini``) that
    supply a concrete chat ``Model``; this class handles prompt assembly, serialization
    checks, and run logging.
    """

    def __init__(
        self,
        *,
        model: Model,
        system_prompt: str = DEFAULT_WEDDING_AGENT_SYSTEM_PROMPT,
        retries: int = 2,
        run_failed_log_message: str = "Agent run failed",
    ) -> None:
        self._agent = Agent(
            model,
            output_type=_TurnOutput,
            system_prompt=system_prompt,
            retries=retries,
        )
        self._run_failed_log_message = run_failed_log_message

    def _build_user_prompt(self, *, message: str, config: dict[str, Any]) -> str:
        text = message.strip()
        if len(text) > _MAX_USER_CHARS:
            text = text[:_MAX_USER_CHARS]
        try:
            config_json = json.dumps(config, ensure_ascii=False)
        except TypeError:
            logger.exception("Site config is not JSON-serializable for agent turn")
            raise
        return f"User message:\n{text}\n\nCurrent config JSON:\n{config_json}"

    async def _invoke_agent(self, user_prompt: str) -> _TurnOutput:
        result = await self._agent.run(user_prompt)
        return result.output

    async def run(self, *, message: str, config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        user_prompt = self._build_user_prompt(message=message, config=config)
        try:
            out = await self._invoke_agent(user_prompt)
        except Exception:
            logger.exception(self._run_failed_log_message)
            raise
        return out.assistant_message, out.config
