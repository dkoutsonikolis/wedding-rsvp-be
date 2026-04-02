"""Structured logging for agent turns (short feedback loop when debugging config merge)."""

from __future__ import annotations

import json
import logging
from collections.abc import Sequence
from typing import Any
from uuid import UUID

# Full JSON in DEBUG can be large; cap per field for terminal / log collectors.
_DEBUG_JSON_MAX_CHARS = 14_000


def _hero_name_snapshot(config: Any) -> str | None:
    if not isinstance(config, dict):
        return None
    blocks = config.get("blocks")
    if not isinstance(blocks, list):
        return None
    for block in blocks:
        if not isinstance(block, dict) or block.get("type") != "hero":
            continue
        data = block.get("data")
        if not isinstance(data, dict):
            return "hero(data=non-dict)"
        one = data.get("partnerOne")
        two = data.get("partnerTwo")
        return f"{one!r}/{two!r}"
    return None


def summarize_agent_config(name: str, config: Any) -> str:
    """One-line summary: top-level keys, block count, block id:type preview, hero names."""
    if not isinstance(config, dict):
        return f"{name}=<{type(config).__name__}>"
    keys = ",".join(sorted(config.keys()))
    blocks = config.get("blocks")
    if not isinstance(blocks, list):
        return f"{name} keys=[{keys}] blocks=? hero={_hero_name_snapshot(config)}"
    preview: list[str] = []
    for block in blocks[:10]:
        if isinstance(block, dict):
            preview.append(f"{block.get('id')}:{block.get('type')}")
        else:
            preview.append(type(block).__name__)
    more = "+" if len(blocks) > 10 else ""
    blk = f"[{';'.join(preview)}{more}] n={len(blocks)}"
    hero = _hero_name_snapshot(config)
    hero_part = f" hero={hero}" if hero else ""
    return f"{name} keys=[{keys}] blocks={blk}{hero_part}"


def summarize_llm_usage(usage: dict[str, int] | None) -> str:
    """One-line usage for INFO logs (compare runs / cost debugging)."""
    if not usage:
        return "llm_usage=n/a"
    parts = [f"{k}={v}" for k, v in sorted(usage.items())]
    return "llm_usage[" + ";".join(parts) + "]"


def summarize_tools_used(names: Sequence[str] | None) -> str:
    """One-line tool call sequence for INFO logs (observe model behavior per turn)."""
    if names is None:
        return "tools=n/a"
    if not names:
        return "tools=[]"
    return "tools[" + ";".join(names) + "]"


def debug_config_json(config: Any) -> str:
    try:
        text = json.dumps(config, ensure_ascii=False, default=str)
    except TypeError:
        return f"<not JSON-serializable {type(config).__name__}>"
    if len(text) > _DEBUG_JSON_MAX_CHARS:
        return text[:_DEBUG_JSON_MAX_CHARS] + f"... <truncated len={len(text)}>"
    return text


def log_agent_turn_config(
    logger: logging.Logger,
    *,
    scope: str,
    site_id: UUID | None,
    user_message: str,
    merged_base: dict[str, Any],
    raw_model_config: Any,
    final_config: dict[str, Any],
    llm_usage: dict[str, int] | None = None,
    tools_used: Sequence[str] | None = None,
) -> None:
    msg_preview = user_message.strip().replace("\n", " ")[:200]
    site = f" site_id={site_id}" if site_id else ""
    logger.info(
        "Agent turn scope=%s%s msg=%r | %s | %s | %s | %s | %s",
        scope,
        site,
        msg_preview,
        summarize_agent_config("base", merged_base),
        summarize_agent_config("raw", raw_model_config),
        summarize_agent_config("final", final_config),
        summarize_llm_usage(llm_usage),
        summarize_tools_used(tools_used),
    )
    logger.debug(
        "Agent turn scope=%s%s raw_config JSON: %s",
        scope,
        site,
        debug_config_json(raw_model_config),
    )
    logger.debug(
        "Agent turn scope=%s%s final_config JSON: %s", scope, site, debug_config_json(final_config)
    )
