"""Structured LLM turn flow: assistant reply plus full site ``config`` (implementation uses Pydantic AI)."""

import copy
import json
from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.messages import BuiltinToolCallPart, ModelResponse, ToolCallPart
from pydantic_ai.models import Model, ModelSettings
from pydantic_ai.run import AgentRunResult
from pydantic_ai.usage import RunUsage

from domains.agent.agent_config_summary import summarize_wedding_site_config_for_agent
from domains.agent.chat_history import format_history_for_prompt
from domains.agent.config_processing import merge_model_config_into_base
from domains.agent.ports import AgentBackend, AgentTurnResult
from domains.agent.prompts import default_wedding_builder_system_prompt
from domains.agent.tools import register_site_surface_tools
from domains.agent.wedding_builder_deps import WeddingBuilderDeps
from utils.logging import get_logger

logger = get_logger(__name__)

# Builder chat is usually short; cap limits cost/context vs. full `config` JSON in the same turn.
_MAX_USER_CHARS = 4000

DEFAULT_WEDDING_AGENT_SYSTEM_PROMPT = default_wedding_builder_system_prompt()


def _tool_names_from_run(result: AgentRunResult[Any]) -> tuple[str, ...]:
    """Model-invoked tool names in conversation order (includes output-structured tool if used as a call)."""
    names: list[str] = []
    for message in result.all_messages():
        if not isinstance(message, ModelResponse):
            continue
        for part in message.parts:
            if isinstance(part, ToolCallPart | BuiltinToolCallPart):
                names.append(part.tool_name)
    return tuple(names)


def _run_usage_for_log(run_usage: RunUsage) -> dict[str, int]:
    """Stable, log-friendly snapshot (totals for this agent run, including tool loops)."""
    snapshot: dict[str, int] = {
        "input_tokens": run_usage.input_tokens,
        "output_tokens": run_usage.output_tokens,
        "requests": run_usage.requests,
        "tool_calls": run_usage.tool_calls,
    }
    if run_usage.cache_read_tokens:
        snapshot["cache_read_tokens"] = run_usage.cache_read_tokens
    if run_usage.cache_write_tokens:
        snapshot["cache_write_tokens"] = run_usage.cache_write_tokens
    return snapshot


class _TurnOutput(BaseModel):
    assistant_message: str = Field(
        description=(
            "Short, friendly message for the couple in the chat UI only. Plain sentences—no JSON, "
            "no site summary, no config dump, no block ids, no markdown code fences. Do not say "
            "'hero section/block', 'gallery-1', or other builder jargon; use natural wording "
            "(e.g. names at the top, photo area). Technical details belong only in `config`, not here."
        ),
    )
    config: dict[str, Any] = Field(
        description=(
            "Partial site config patch (deep-merged after tool calls). Prefer {} when reorder_blocks "
            "or apply_theme already applied the user's request. get_full_site_config is read-only—if the "
            "user asked for a content/data change and you called it to read nested fields, you must still "
            "include that edit here (not {}). For custom page background or palette tweaks, include "
            "theme.colors (e.g. theme.colors.background)—{} leaves colors unchanged."
        ),
    )


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
        model_settings: ModelSettings | None = None,
    ) -> None:
        self._agent = Agent(
            model,
            output_type=_TurnOutput,
            system_prompt=system_prompt,
            model_settings=model_settings,
            retries=retries,
            deps_type=WeddingBuilderDeps,
            # Default "early" runs the output tool first and skips other tool calls in the same model
            # response—function tools would be stubbed and never mutate deps. "exhaustive" runs them.
            end_strategy="exhaustive",
        )
        register_site_surface_tools(self._agent)
        self._run_failed_log_message = run_failed_log_message

    def _build_user_prompt(
        self,
        *,
        message: str,
        config: dict[str, Any],
        conversation_history: Sequence[dict[str, str]] | None = None,
    ) -> str:
        text = message.strip()
        if len(text) > _MAX_USER_CHARS:
            text = text[:_MAX_USER_CHARS]
        summary = summarize_wedding_site_config_for_agent(config)
        try:
            summary_json = json.dumps(summary, ensure_ascii=False)
        except TypeError:
            logger.exception("Site config summary is not JSON-serializable for agent turn")
            raise
        prev_block = format_history_for_prompt(conversation_history or ())
        prefix = f"Previous conversation:\n{prev_block}\n\n" if prev_block else ""
        return (
            f"{prefix}"
            f"User message:\n{text}\n\n"
            f"Site summary (compact — nested section data omitted; call get_full_site_config if you need it):\n"
            f"{summary_json}"
        )

    async def _invoke_agent(
        self, user_prompt: str, deps: WeddingBuilderDeps
    ) -> tuple[_TurnOutput, RunUsage, tuple[str, ...]]:
        result = await self._agent.run(user_prompt, deps=deps)
        return result.output, result.usage(), _tool_names_from_run(result)

    async def run(
        self,
        *,
        message: str,
        config: dict[str, Any],
        conversation_history: Sequence[dict[str, str]] | None = None,
    ) -> AgentTurnResult:
        user_prompt = self._build_user_prompt(
            message=message,
            config=config,
            conversation_history=conversation_history,
        )
        deps = WeddingBuilderDeps(config=copy.deepcopy(config))
        try:
            out, run_usage, tool_names = await self._invoke_agent(user_prompt, deps=deps)
        except Exception:
            logger.exception(self._run_failed_log_message)
            raise
        merged_config = merge_model_config_into_base(base=deps.config, model_config=out.config)
        return AgentTurnResult(
            assistant_message=out.assistant_message,
            config=merged_config,
            model_config_patch=out.config if isinstance(out.config, dict) else None,
            llm_usage=_run_usage_for_log(run_usage),
            tools_used=tool_names,
        )
