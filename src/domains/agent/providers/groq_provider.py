from dataclasses import dataclass

from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

from domains.agent.providers.config import ProviderLlmConfig
from domains.agent.structured_agent_backend import StructuredAgentBackend


@dataclass(frozen=True)
class GroqBackendConfig(ProviderLlmConfig):
    """Groq Cloud API (OpenAI-compatible chat); same fields as ``ProviderLlmConfig``."""


def structured_agent_backend_from_groq(config: GroqBackendConfig) -> StructuredAgentBackend:
    """Build ``StructuredAgentBackend`` wired to Groq for ``config``."""
    provider = GroqProvider(api_key=config.api_key)
    model = GroqModel(config.model_name, provider=provider)
    return StructuredAgentBackend(
        model=model,
        run_failed_log_message="Groq agent run failed",
    )
