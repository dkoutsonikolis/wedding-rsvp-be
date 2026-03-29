"""Build the agent backend from settings (call once at application startup)."""

from typing import Literal, Protocol

from domains.agent.backend import AgentBackend, StubAgentBackend
from domains.agent.gemini_backend import GeminiAgentBackend

AgentBackendKind = Literal["auto", "stub", "gemini"]


class AgentBackendConfig(Protocol):
    """Minimal config surface for building an `AgentBackend` (``Settings`` satisfies this)."""

    AGENT_BACKEND: AgentBackendKind
    GOOGLE_API_KEY: str | None
    GEMINI_MODEL: str


def build_agent_backend(settings: AgentBackendConfig) -> AgentBackend:
    """
    Return the backend selected by ``AGENT_BACKEND``.

    - ``stub``: always the stub (no outbound LLM).
    - ``gemini``: Gemini; requires ``GOOGLE_API_KEY``.
    - ``auto``: Gemini when a non-empty ``GOOGLE_API_KEY`` is set, otherwise stub.
    """
    kind = settings.AGENT_BACKEND.strip().lower()
    if kind == "stub":
        return StubAgentBackend()
    if kind == "gemini":
        key = (settings.GOOGLE_API_KEY or "").strip()
        if not key:
            raise RuntimeError("AGENT_BACKEND=gemini requires GOOGLE_API_KEY (see .env.example).")
        return GeminiAgentBackend(
            api_key=key,
            model_name=(settings.GEMINI_MODEL or "gemini-2.5-flash").strip(),
        )
    if kind == "auto":
        key = (settings.GOOGLE_API_KEY or "").strip()
        if key:
            return GeminiAgentBackend(
                api_key=key,
                model_name=(settings.GEMINI_MODEL or "gemini-2.5-flash").strip(),
            )
        return StubAgentBackend()
    raise ValueError(
        f"AGENT_BACKEND must be one of auto, stub, gemini; got {settings.AGENT_BACKEND!r}"
    )
