"""Build the agent backend from settings (call once at application startup)."""

from typing import Literal, Protocol

from domains.agent.ports import AgentBackend
from domains.agent.providers import (
    GeminiBackendConfig,
    GroqBackendConfig,
    structured_agent_backend_from_gemini,
    structured_agent_backend_from_groq,
)
from domains.agent.stub_backend import StubAgentBackend

AgentBackendKind = Literal["auto", "stub", "gemini", "groq"]


class AgentBackendConfig(Protocol):
    """Minimal config surface for building an `AgentBackend` (``Settings`` satisfies this)."""

    AGENT_BACKEND: AgentBackendKind
    GOOGLE_API_KEY: str | None
    GEMINI_MODEL: str
    GROQ_API_KEY: str | None
    GROQ_MODEL: str


def build_agent_backend(settings: AgentBackendConfig) -> AgentBackend:
    """
    Return the backend selected by ``AGENT_BACKEND``.

    - ``stub``: always the stub (no outbound LLM).
    - ``gemini``: Gemini; requires ``GOOGLE_API_KEY``.
    - ``groq``: Groq; requires ``GROQ_API_KEY``.
    - ``auto``: Gemini if ``GOOGLE_API_KEY`` is set, else Groq if ``GROQ_API_KEY``, else stub.
    """
    kind = settings.AGENT_BACKEND.strip().lower()
    if kind == "stub":
        return StubAgentBackend()
    if kind == "gemini":
        key = (settings.GOOGLE_API_KEY or "").strip()
        if not key:
            raise RuntimeError("AGENT_BACKEND=gemini requires GOOGLE_API_KEY (see .env.example).")
        return structured_agent_backend_from_gemini(
            GeminiBackendConfig(
                api_key=key,
                model_name=(settings.GEMINI_MODEL or "gemini-2.5-flash").strip(),
            )
        )
    if kind == "groq":
        key = (settings.GROQ_API_KEY or "").strip()
        if not key:
            raise RuntimeError("AGENT_BACKEND=groq requires GROQ_API_KEY (see .env.example).")
        return structured_agent_backend_from_groq(
            GroqBackendConfig(
                api_key=key,
                model_name=(settings.GROQ_MODEL or "llama-3.3-70b-versatile").strip(),
            )
        )
    if kind == "auto":
        google = (settings.GOOGLE_API_KEY or "").strip()
        if google:
            return structured_agent_backend_from_gemini(
                GeminiBackendConfig(
                    api_key=google,
                    model_name=(settings.GEMINI_MODEL or "gemini-2.5-flash").strip(),
                )
            )
        groq_key = (settings.GROQ_API_KEY or "").strip()
        if groq_key:
            return structured_agent_backend_from_groq(
                GroqBackendConfig(
                    api_key=groq_key,
                    model_name=(settings.GROQ_MODEL or "llama-3.3-70b-versatile").strip(),
                )
            )
        return StubAgentBackend()
    raise ValueError(
        f"AGENT_BACKEND must be one of auto, stub, gemini, groq; got {settings.AGENT_BACKEND!r}"
    )
