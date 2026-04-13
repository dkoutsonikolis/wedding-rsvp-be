"""Helpers for model prompt history shaping."""

from collections.abc import Sequence


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
