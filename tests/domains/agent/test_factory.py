from types import SimpleNamespace

import pytest

from domains.agent.backend import StubAgentBackend
from domains.agent.factory import build_agent_backend
from domains.agent.gemini_backend import GeminiAgentBackend


def _ns(**kwargs: object) -> SimpleNamespace:
    base = {
        "AGENT_BACKEND": "auto",
        "GOOGLE_API_KEY": None,
        "GEMINI_MODEL": "gemini-2.5-flash",
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


def test__build_agent_backend__stub():
    # Arrange
    cfg = _ns(AGENT_BACKEND="stub", GOOGLE_API_KEY="ignored")
    # Act
    backend = build_agent_backend(cfg)
    # Assert
    assert isinstance(backend, StubAgentBackend)


def test__build_agent_backend__auto_without_key():
    # Arrange
    cfg = _ns(AGENT_BACKEND="auto", GOOGLE_API_KEY=None)
    # Act
    backend = build_agent_backend(cfg)
    # Assert
    assert isinstance(backend, StubAgentBackend)


def test__build_agent_backend__auto_with_key():
    # Arrange
    cfg = _ns(AGENT_BACKEND="auto", GOOGLE_API_KEY="test-key")
    # Act
    backend = build_agent_backend(cfg)
    # Assert
    assert isinstance(backend, GeminiAgentBackend)


def test__build_agent_backend__gemini_without_key():
    # Arrange
    cfg = _ns(AGENT_BACKEND="gemini", GOOGLE_API_KEY="")
    # Act / Assert
    with pytest.raises(RuntimeError, match="GOOGLE_API_KEY"):
        build_agent_backend(cfg)


def test__build_agent_backend__invalid_kind():
    # Arrange
    cfg = _ns(AGENT_BACKEND="wat")
    # Act / Assert
    with pytest.raises(ValueError, match="AGENT_BACKEND"):
        build_agent_backend(cfg)
