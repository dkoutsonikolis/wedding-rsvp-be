"""Build the agent backend from settings (call once at application startup)."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, Protocol, cast

from domains.agent.ports import AgentBackend
from domains.agent.providers import (
    AnthropicBackendConfig,
    GeminiBackendConfig,
    GroqBackendConfig,
    structured_agent_backend_from_anthropic,
    structured_agent_backend_from_gemini,
    structured_agent_backend_from_groq,
)
from domains.agent.stub_backend import StubAgentBackend

AgentBackendKind = Literal["auto", "stub", "gemini", "groq", "anthropic"]


class AgentBackendConfig(Protocol):
    """Minimal config surface for building an `AgentBackend` (``Settings`` satisfies this)."""

    AGENT_BACKEND: AgentBackendKind
    GOOGLE_API_KEY: str | None
    GEMINI_MODEL: str
    ANTHROPIC_API_KEY: str | None
    ANTHROPIC_MODEL: str
    GROQ_API_KEY: str | None
    GROQ_MODEL: str


def _strip_key(value: str | None) -> str:
    return (value or "").strip()


def _read_api_key(settings: AgentBackendConfig, attr: str) -> str | None:
    """``attr`` is a field name on ``AgentBackendConfig`` (same name as the env var in ``Settings``)."""
    return cast(str | None, getattr(settings, attr))


def _read_model_id(settings: AgentBackendConfig, attr: str) -> str:
    """``attr`` is a field name on ``AgentBackendConfig`` (same name as the env var in ``Settings``)."""
    return cast(str, getattr(settings, attr))


@dataclass(frozen=True)
class _ProviderSpec:
    """``api_key_attr`` / ``model_attr`` match ``AgentBackendConfig`` fields (and thus ``Settings`` / .env names)."""

    api_key_attr: str
    model_attr: str
    build: Callable[[str, str], AgentBackend]


def _require_model_id(settings: AgentBackendConfig, spec: _ProviderSpec) -> str:
    model = _read_model_id(settings, spec.model_attr).strip()
    if not model:
        raise RuntimeError(
            f"{spec.model_attr} must be set to a non-empty model id (see .env.example)."
        )
    return model


def _build_from_spec(
    settings: AgentBackendConfig, spec: _ProviderSpec, api_key: str
) -> AgentBackend:
    model = _require_model_id(settings, spec)
    return spec.build(api_key, model)


_PROVIDER_SPECS: dict[str, _ProviderSpec] = {
    "gemini": _ProviderSpec(
        api_key_attr="GOOGLE_API_KEY",
        model_attr="GEMINI_MODEL",
        build=lambda api_key, model: structured_agent_backend_from_gemini(
            GeminiBackendConfig(api_key=api_key, model_name=model)
        ),
    ),
    "anthropic": _ProviderSpec(
        api_key_attr="ANTHROPIC_API_KEY",
        model_attr="ANTHROPIC_MODEL",
        build=lambda api_key, model: structured_agent_backend_from_anthropic(
            AnthropicBackendConfig(api_key=api_key, model_name=model)
        ),
    ),
    "groq": _ProviderSpec(
        api_key_attr="GROQ_API_KEY",
        model_attr="GROQ_MODEL",
        build=lambda api_key, model: structured_agent_backend_from_groq(
            GroqBackendConfig(api_key=api_key, model_name=model)
        ),
    ),
}

# Order for ``AGENT_BACKEND=auto`` (first non-empty API key wins).
_AUTO_BACKEND_ORDER: tuple[str, ...] = ("gemini", "anthropic", "groq")


def _auto_backend(settings: AgentBackendConfig) -> AgentBackend:
    """Gemini → Anthropic → Groq if each API key is set; otherwise stub."""
    for kind in _AUTO_BACKEND_ORDER:
        spec = _PROVIDER_SPECS[kind]
        key = _strip_key(_read_api_key(settings, spec.api_key_attr))
        if key:
            return _build_from_spec(settings, spec, key)
    return StubAgentBackend()


def build_agent_backend(settings: AgentBackendConfig) -> AgentBackend:
    """
    Return the backend selected by ``AGENT_BACKEND``.

    - ``stub``: always the stub (no outbound LLM).
    - ``gemini``: Gemini; requires ``GOOGLE_API_KEY``.
    - ``anthropic``: Anthropic Claude; requires ``ANTHROPIC_API_KEY``.
    - ``groq``: Groq; requires ``GROQ_API_KEY``.
    - ``auto``: Gemini if ``GOOGLE_API_KEY``, else Anthropic if ``ANTHROPIC_API_KEY``, else Groq if ``GROQ_API_KEY``, else stub.
    """
    kind = settings.AGENT_BACKEND.strip().lower()
    if kind == "stub":
        return StubAgentBackend()
    if kind == "auto":
        return _auto_backend(settings)
    spec = _PROVIDER_SPECS.get(kind)
    if spec is not None:
        key = _strip_key(_read_api_key(settings, spec.api_key_attr))
        if not key:
            raise RuntimeError(
                f"AGENT_BACKEND={kind} requires {spec.api_key_attr} (see .env.example)."
            )
        return _build_from_spec(settings, spec, key)
    raise ValueError(
        f"AGENT_BACKEND must be one of auto, stub, gemini, groq, anthropic; got {settings.AGENT_BACKEND!r}"
    )
