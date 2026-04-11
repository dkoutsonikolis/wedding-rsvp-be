from dataclasses import dataclass

from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

from domains.agent.providers.config import ProviderLlmConfig
from domains.agent.structured_agent_backend import StructuredAgentBackend


@dataclass(frozen=True)
class AnthropicBackendConfig(ProviderLlmConfig):
    """Anthropic Messages API (Claude); same fields as ``ProviderLlmConfig``."""


def structured_agent_backend_from_anthropic(
    config: AnthropicBackendConfig,
) -> StructuredAgentBackend:
    """Build ``StructuredAgentBackend`` wired to Anthropic for ``config``."""
    provider = AnthropicProvider(api_key=config.api_key)
    model = AnthropicModel(config.model_name, provider=provider)
    return StructuredAgentBackend(
        model=model,
        run_failed_log_message="Anthropic agent run failed",
    )
