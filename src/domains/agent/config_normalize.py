"""Repair common LLM mistakes in wedding `config` before persist/response.

Models sometimes put couple names at the root of ``config`` instead of under the
hero block's ``data``. They may also emit a bogus string ``data`` field at the
root, or random top-level keys (e.g. inverted key/value pairs). The builder UI
only reads names from ``blocks[].data`` for the hero block.
"""

from __future__ import annotations

import copy
import re
from typing import Any

# Site JSON the FE sends under `config` (allow unknown `_` prefix for stubs/tests).
_ALLOWED_TOP_LEVEL_KEYS = frozenset(
    {"id", "slug", "theme", "blocks", "metadata", "customCss", "version"},
)

_NAME_INTENT = re.compile(
    r"\b(names?|couple|partner|bride|groom|rename|call us|call them)\b",
    re.IGNORECASE,
)

_TWO_NAMES = re.compile(
    r"\b([A-Za-z][A-Za-z']*)\s+and\s+([A-Za-z][A-Za-z']*)\b",
)


def strip_unknown_top_level_site_config_keys(config: dict[str, Any]) -> dict[str, Any]:
    """Drop top-level keys that are not part of the wedding site config shape."""
    out = copy.deepcopy(config)
    for key in list(out.keys()):
        if key in _ALLOWED_TOP_LEVEL_KEYS or key.startswith("_"):
            continue
        out.pop(key, None)
    return out


def _hero_data(cfg: dict[str, Any]) -> dict[str, Any] | None:
    blocks = cfg.get("blocks")
    if not isinstance(blocks, list):
        return None
    for block in blocks:
        if isinstance(block, dict) and block.get("type") == "hero":
            data = block.get("data")
            return data if isinstance(data, dict) else {}
    return None


def apply_hero_names_from_user_message_when_unchanged(
    base: dict[str, Any],
    final: dict[str, Any],
    user_message: str,
) -> dict[str, Any]:
    """
    If the user asked to change names and the hero ``partnerOne``/``partnerTwo``
    are unchanged from ``base`` after the model run, try ``Name and Name`` from the
    user message. Guards with a simple name-intent keyword to limit false positives.
    """
    out = copy.deepcopy(final)
    if not _NAME_INTENT.search(user_message):
        return out
    m = _TWO_NAMES.search(user_message)
    if not m:
        return out
    one, two = m.group(1).strip(), m.group(2).strip()

    base_hero = _hero_data(base)
    final_hero = _hero_data(out)
    if final_hero is None:
        return out
    if base_hero is not None:
        same = final_hero.get("partnerOne") == base_hero.get("partnerOne") and (
            final_hero.get("partnerTwo") == base_hero.get("partnerTwo")
        )
        if not same:
            return out

    blocks = out.get("blocks")
    if not isinstance(blocks, list):
        return out
    for block in blocks:
        if not isinstance(block, dict) or block.get("type") != "hero":
            continue
        data = block.get("data")
        if not isinstance(data, dict):
            data = {}
            block["data"] = data
        data["partnerOne"] = one
        data["partnerTwo"] = two
        break
    return out


def normalize_misplaced_hero_couple_fields(config: dict[str, Any]) -> dict[str, Any]:
    """
    - Remove root ``data`` when it is not an object (invalid for site config).
    - If root ``partnerOne`` / ``partnerTwo`` are non-empty strings, move them into
      the first ``hero`` block's ``data``. If no hero block exists, restore those
      keys at the root so values are not dropped silently.
    """
    out = copy.deepcopy(config)

    root_data = out.get("data")
    if "data" in out and not isinstance(root_data, dict):
        out.pop("data", None)

    moved: dict[str, str] = {}
    for key in ("partnerOne", "partnerTwo"):
        val = out.get(key)
        if isinstance(val, str) and val.strip():
            moved[key] = val.strip()
            out.pop(key, None)

    if not moved:
        return out

    blocks = out.get("blocks")
    if not isinstance(blocks, list):
        out.update(moved)
        return out

    for block in blocks:
        if not isinstance(block, dict) or block.get("type") != "hero":
            continue
        inner = block.get("data")
        if not isinstance(inner, dict):
            inner = {}
            block["data"] = inner
        for k, v in moved.items():
            inner[k] = v
        return out

    out.update(moved)
    return out
