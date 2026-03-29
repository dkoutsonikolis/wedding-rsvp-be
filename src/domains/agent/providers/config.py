"""Shared config shapes for API-key LLM backends.

Most hosted chat APIs need a secret and a model id. Subclass for a vendor when you need
extra fields (e.g. Azure resource name, Vertex project/location) while keeping the common
pair for factories and tests.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderLlmConfig:
    """API key (or equivalent secret) plus provider model identifier."""

    api_key: str
    model_name: str
