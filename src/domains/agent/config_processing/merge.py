"""Merge LLM ``config`` output into the authoritative snapshot (client ∪ server).

The model may return partial or oddly shaped JSON. We always persist and return a
full dict derived from the pre-turn merged base, with the model output applied as
a deep merge; ``blocks`` are merged by block ``id`` (``data`` is deep-merged).
"""

from __future__ import annotations

import copy
from typing import Any


def _deep_merge_dict(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(base)
    for key, value in patch.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = _deep_merge_dict(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def _merge_block(base_block: dict[str, Any], patch_block: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(base_block)
    for key, value in patch_block.items():
        if key == "data" and isinstance(value, dict):
            existing = out.get("data")
            if isinstance(existing, dict):
                out["data"] = _deep_merge_dict(existing, value)
            else:
                out["data"] = copy.deepcopy(value)
        elif key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = _deep_merge_dict(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def _indices_by_block_type(blocks: list[Any]) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    for i, block in enumerate(blocks):
        if isinstance(block, dict):
            typ = block.get("type")
            if isinstance(typ, str):
                out.setdefault(typ, []).append(i)
    return out


def _merge_block_lists(base_blocks: Any, patch_blocks: Any) -> list[Any]:
    if not isinstance(patch_blocks, list):
        return copy.deepcopy(base_blocks) if isinstance(base_blocks, list) else []

    if not isinstance(base_blocks, list) or len(base_blocks) == 0:
        return copy.deepcopy(patch_blocks)

    result: list[Any] = copy.deepcopy(base_blocks)
    index_by_id: dict[str, int] = {}
    for i, block in enumerate(result):
        if isinstance(block, dict) and isinstance(block.get("id"), str):
            index_by_id[block["id"]] = i

    type_to_indices = _indices_by_block_type(result)

    for pb in patch_blocks:
        if not isinstance(pb, dict):
            continue
        idx: int | None = None
        bid = pb.get("id")
        if isinstance(bid, str) and bid in index_by_id:
            idx = index_by_id[bid]
        else:
            typ = pb.get("type")
            if isinstance(typ, str):
                candidates = type_to_indices.get(typ, [])
                if len(candidates) == 1:
                    idx = candidates[0]
        if idx is None:
            continue
        current = result[idx]
        if not isinstance(current, dict):
            continue
        result[idx] = _merge_block(current, pb)

    return result


def merge_stored_config_with_request(
    *,
    stored: dict[str, Any],
    request: dict[str, Any] | None,
) -> dict[str, Any]:
    """Merge an incoming HTTP ``config`` into the persisted snapshot before an agent turn.

    The handler used ``{**stored, **request}``, which **replaces** nested objects like
    ``theme`` when the client sends a partial ``theme`` (e.g. only ``colors.background``),
    silently dropping ``theme.id``, fonts, and other keys. That yields a broken base config
    for tools and merges.

    **Blocks:** when ``request`` includes a **non-empty** ``blocks`` list, it replaces the
    stored list (full client snapshot). An **empty** ``blocks`` list is ignored—matching
    ``mergeAgentConfigIntoSite`` on the frontend—so a partial payload cannot wipe sections.
    """
    out = copy.deepcopy(stored)
    if not isinstance(request, dict) or not request:
        return out

    for key, value in request.items():
        if key == "blocks":
            if isinstance(value, list) and len(value) > 0:
                out["blocks"] = copy.deepcopy(value)
            continue
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge_dict(out[key], value)
        else:
            out[key] = copy.deepcopy(value)

    return out


def merge_model_config_into_base(
    *,
    base: Any,
    model_config: Any,
) -> dict[str, Any]:
    """Return a full snapshot: ``base`` updated with ``model_config`` (patch semantics)."""
    base_dict: dict[str, Any] = base if isinstance(base, dict) else {}
    if not isinstance(model_config, dict):
        return copy.deepcopy(base_dict)

    removed_ids: set[str] = set()
    raw_removed = model_config.get("removed_block_ids")
    if isinstance(raw_removed, list):
        removed_ids = {x for x in raw_removed if isinstance(x, str)}

    out = copy.deepcopy(base_dict)
    for key, value in model_config.items():
        if key == "removed_block_ids":
            continue
        if key == "blocks":
            out["blocks"] = _merge_block_lists(out.get("blocks"), value)
        elif isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge_dict(out[key], value)
        else:
            out[key] = copy.deepcopy(value)

    if removed_ids and isinstance(out.get("blocks"), list):
        out["blocks"] = [
            b
            for b in out["blocks"]
            if not (isinstance(b, dict) and isinstance(b.get("id"), str) and b["id"] in removed_ids)
        ]

    return out
