from dataclasses import dataclass

from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from domains.agent.providers.config import ProviderLlmConfig
from domains.agent.structured_agent_backend import StructuredAgentBackend


@dataclass(frozen=True)
class GeminiBackendConfig(ProviderLlmConfig):
    """Google Generative Language API (Gemini); same fields as ``ProviderLlmConfig``."""


def structured_agent_backend_from_gemini(config: GeminiBackendConfig) -> StructuredAgentBackend:
    """Build ``StructuredAgentBackend`` wired to Gemini for ``config``."""
    provider = GoogleProvider(api_key=config.api_key)
    model = GoogleModel(config.model_name, provider=provider)
    return StructuredAgentBackend(
        model=model,
        run_failed_log_message="Gemini agent run failed",
    )
