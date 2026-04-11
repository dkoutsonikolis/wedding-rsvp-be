"""Helpers for persisted agent chat (JSONB trial or DB rows for sites)."""

from collections.abc import Sequence
from typing import Any, Literal, cast

from domains.wedding_sites.models import AgentConversationMessage

Role = Literal["user", "assistant"]


def normalize_history(raw: Any) -> list[dict[str, str]]:
    """Coerce stored JSONB (or similar) into a list of user/assistant messages."""
    if raw is None:
        return []
    if not isinstance(raw, list):
        return []
    out: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role not in ("user", "assistant") or not isinstance(content, str):
            continue
        out.append({"role": cast(Role, role), "content": content})
    return out


def append_turn(
    history: list[dict[str, str]], user_message: str, assistant_message: str
) -> list[dict[str, str]]:
    return [
        *history,
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": assistant_message},
    ]


def trim_to_max_turn_pairs(history: list[dict[str, str]], max_turns: int) -> list[dict[str, str]]:
    """Keep at most ``max_turns`` completed user+assistant pairs (``2 * max_turns`` entries)."""
    if max_turns <= 0:
        return []
    max_items = max_turns * 2
    if len(history) <= max_items:
        return history
    return history[-max_items:]


def trim_for_model(history: list[dict[str, str]], max_turns: int) -> list[dict[str, str]]:
    """Last ``max_turns`` pairs to send to the LLM (storage may be longer for owner sites)."""
    return trim_to_max_turn_pairs(history, max_turns)


def format_history_for_prompt(history: Sequence[dict[str, str]]) -> str:
    if not history:
        return ""
    lines: list[str] = []
    for msg in history:
        role = msg["role"]
        label = "User" if role == "user" else "Assistant"
        lines.append(f"{label}: {msg['content']}")
    return "\n".join(lines)


def agent_conversation_rows_to_history(
    rows: list[AgentConversationMessage],
) -> list[dict[str, str]]:
    """Ordered rows from DB → chat message dicts."""
    return [{"role": str(row.role), "content": row.content} for row in rows]
