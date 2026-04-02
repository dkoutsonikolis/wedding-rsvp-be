"""Deterministic in-place mutations for **site surface** tools (block order, theme)."""

import copy
from typing import Any

from domains.agent.theme_registry import CURATED_THEME


def _blocks_list(config: dict[str, Any]) -> list[Any]:
    blocks = config.get("blocks")
    if not isinstance(blocks, list):
        return []
    return blocks


def mutate_reorder_blocks(config: dict[str, Any], ordered_block_ids: list[str]) -> str:
    blocks = _blocks_list(config)
    current_ids: list[str] = []
    for b in blocks:
        if isinstance(b, dict) and isinstance(b.get("id"), str):
            current_ids.append(b["id"])
    if not current_ids:
        return "No blocks with ids to reorder."
    if len(ordered_block_ids) != len(current_ids) or set(ordered_block_ids) != set(current_ids):
        return (
            "ordered_block_ids must list every block id exactly once. "
            f"Current ids: {current_ids!r}"
        )
    id_to_block: dict[str, dict[str, Any]] = {}
    for b in blocks:
        if isinstance(b, dict) and isinstance(b.get("id"), str):
            id_to_block[b["id"]] = b
    reordered = [id_to_block[i] for i in ordered_block_ids]
    for i, block in enumerate(reordered):
        block["order"] = i
    config["blocks"] = reordered
    return "Updated block order."


def mutate_apply_theme(config: dict[str, Any], theme_id: str) -> str:
    theme = CURATED_THEME.get(theme_id)
    if theme is None:
        valid = ", ".join(sorted(CURATED_THEME))
        raise ValueError(f"Unknown theme_id {theme_id!r}. Valid ids: {valid}")
    config["theme"] = copy.deepcopy(theme)
    return f"Applied theme {theme_id!r}."
