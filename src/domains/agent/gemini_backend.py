import json
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from utils.logging import get_logger

logger = get_logger(__name__)

_MAX_USER_CHARS = 16_000

_SYSTEM_PROMPT = """You help couples edit a wedding website in a visual builder.

You receive the user's message and the current site configuration as JSON (`config`).
Apply the user's intent to `config` and return:
- `assistant_message`: a short, friendly plain-text reply for the chat UI.
- `config`: the full updated JSON object to save (not a patch).

Preserve existing keys and structure unless the user clearly wants changes or removals.
Do not invent private guest data, passwords, or payment details."""


class _TurnOutput(BaseModel):
    assistant_message: str = Field(description="Reply shown in the builder chat (plain text).")
    config: dict[str, Any] = Field(description="Complete updated site configuration object.")


class GeminiAgentBackend:
    """Pydantic AI agent backed by Google Gemini (Generative Language API)."""

    def __init__(self, *, api_key: str, model_name: str) -> None:
        provider = GoogleProvider(api_key=api_key)
        model = GoogleModel(model_name, provider=provider)
        self._agent = Agent(
            model,
            output_type=_TurnOutput,
            system_prompt=_SYSTEM_PROMPT,
            retries=2,
        )

    async def run(self, *, message: str, config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        text = message.strip()
        if len(text) > _MAX_USER_CHARS:
            text = text[:_MAX_USER_CHARS]
        try:
            config_json = json.dumps(config, ensure_ascii=False)
        except TypeError:
            logger.exception("Site config is not JSON-serializable for Gemini turn")
            raise
        user_prompt = f"User message:\n{text}\n\nCurrent config JSON:\n{config_json}"
        try:
            result = await self._agent.run(user_prompt)
        except Exception:
            logger.exception("Gemini agent run failed")
            raise
        out = result.output
        return out.assistant_message, out.config
