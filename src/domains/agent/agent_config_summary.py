"""Compact site config for the builder agent user prompt (fewer input tokens)."""

from typing import Any

_MAX_SUMMARY_LEN = 120


def _truncate(text: str, max_len: int = _MAX_SUMMARY_LEN) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def _block_row(block: dict[str, Any]) -> dict[str, Any]:
    block_id = block.get("id")
    typ = block.get("type")
    if not isinstance(block_id, str) or not isinstance(typ, str):
        return {
            "id": str(block_id) if block_id is not None else None,
            "type": str(typ) if typ is not None else "unknown",
            "visible": bool(block.get("visible", True)),
            "order": block.get("order"),
            "summary": "",
        }
    raw_order = block.get("order")
    order: int | None = int(raw_order) if isinstance(raw_order, int | float) else None
    data = block.get("data")
    inner = data if isinstance(data, dict) else {}
    summary = ""
    extras: dict[str, Any] = {}

    if typ == "hero":
        one = inner.get("partnerOne")
        two = inner.get("partnerTwo")
        if isinstance(one, str) and one.strip() and isinstance(two, str) and two.strip():
            summary = f"{one.strip()} & {two.strip()}"
        elif isinstance(one, str) and one.strip():
            summary = one.strip()
        else:
            tag = inner.get("tagline")
            summary = _truncate(str(tag)) if isinstance(tag, str) and tag.strip() else "Hero"
    elif typ == "wedding-party":
        title = inner.get("title")
        summary = _truncate(str(title)) if isinstance(title, str) else "Wedding party"
        members = inner.get("members")
        if isinstance(members, list):
            extras["member_count"] = len(members)
    elif typ == "gallery":
        title = inner.get("title")
        summary = _truncate(str(title)) if isinstance(title, str) else "Gallery"
        photos = inner.get("photos")
        if isinstance(photos, list):
            extras["photo_count"] = len(photos)
    elif typ == "venue":
        ceremony = inner.get("ceremony")
        if isinstance(ceremony, dict):
            name = ceremony.get("name")
            if isinstance(name, str) and name.strip():
                summary = _truncate(name.strip())
            else:
                summary = "Venue"
        else:
            summary = "Venue"
    elif typ == "rsvp":
        title = inner.get("title")
        summary = _truncate(str(title)) if isinstance(title, str) else "RSVP"
    else:
        summary = typ

    row: dict[str, Any] = {
        "id": block_id,
        "type": typ,
        "visible": bool(block.get("visible", True)),
        "order": order,
        "summary": summary,
    }
    row.update(extras)
    return row


def summarize_wedding_site_config_for_agent(config: dict[str, Any]) -> dict[str, Any]:
    """
    Small JSON snapshot for the first user message: ids, types, visibility, order, one-line labels.

    Full nested ``data`` is omitted; the model should call ``get_full_site_config`` when it needs it.
    """
    theme = config.get("theme")
    theme_out: dict[str, Any] = {}
    if isinstance(theme, dict) and isinstance(theme.get("id"), str):
        theme_out["id"] = theme["id"]
    # Include palette so the model can adjust theme.colors without guessing current hex values.
    if isinstance(theme, dict):
        raw_colors = theme.get("colors")
        if isinstance(raw_colors, dict) and raw_colors:
            theme_out["colors"] = {str(k): v for k, v in raw_colors.items() if isinstance(v, str)}

    meta = config.get("metadata")
    meta_out: dict[str, Any] = {}
    if isinstance(meta, dict) and "published" in meta:
        meta_out["published"] = bool(meta.get("published"))

    blocks_in = config.get("blocks")
    block_rows: list[dict[str, Any]] = []
    if isinstance(blocks_in, list):
        for block in blocks_in:
            if isinstance(block, dict):
                block_rows.append(_block_row(block))

    block_rows.sort(key=lambda row: (row.get("order") is None, row.get("order") or 0))

    out: dict[str, Any] = {
        "id": config.get("id"),
        "slug": config.get("slug"),
        "theme": theme_out,
        "blocks": block_rows,
    }
    if meta_out:
        out["metadata"] = meta_out
    return out
