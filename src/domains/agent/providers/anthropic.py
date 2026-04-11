from dataclasses import dataclass
from typing import Literal

from pydantic_ai.models import ModelSettings
from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelSettings
from pydantic_ai.providers.anthropic import AnthropicProvider

from domains.agent.providers.config import ProviderLlmConfig
from domains.agent.structured_agent_backend import StructuredAgentBackend


@dataclass(frozen=True)
class AnthropicBackendConfig(ProviderLlmConfig):
    """Anthropic Messages API (Claude); extends base with optional prompt-cache flags."""

    prompt_cache: bool = True
    prompt_cache_ttl: Literal["5m", "1h"] = "1h"


def _anthropic_model_settings(config: AnthropicBackendConfig) -> ModelSettings | None:
    if not config.prompt_cache:
        return None
    ttl = config.prompt_cache_ttl
    return AnthropicModelSettings(
        anthropic_cache_instructions=ttl,
        anthropic_cache_tool_definitions=ttl,
    )


def structured_agent_backend_from_anthropic(
    config: AnthropicBackendConfig,
) -> StructuredAgentBackend:
    """Build ``StructuredAgentBackend`` wired to Anthropic for ``config``."""
    provider = AnthropicProvider(api_key=config.api_key)
    model = AnthropicModel(config.model_name, provider=provider)
    return StructuredAgentBackend(
        model=model,
        run_failed_log_message="Anthropic agent run failed",
        model_settings=_anthropic_model_settings(config),
    )
