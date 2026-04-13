from typing import Any, Literal, cast

Role = Literal["user", "assistant"]


def normalize_history(raw: Any) -> list[dict[str, str]]:
    """Coerce stored JSON-like history into a list of role/content messages."""
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
