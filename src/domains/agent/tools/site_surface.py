"""
**Site surface** PydanticAI tools — high-level operations on the whole site shape:

- **Layout** — block order
- **Theme** — curated global theme
- **Context** — read-only full JSON (nested ``data``), so the model can patch content afterward

Deeper, block-specific tools (hero copy, gallery CRUD, …) stay separate when added.
Mutations live in ``tools.mutations.site_surface``.
"""

import json
from typing import Annotated

from pydantic import Field
from pydantic_ai import RunContext

from domains.agent.theme_registry import CuratedThemeId
from domains.agent.tools.mutations.site_surface import mutate_apply_theme, mutate_reorder_blocks
from domains.agent.wedding_builder_deps import WeddingBuilderDeps
from utils.logging import get_logger

logger = get_logger(__name__)


def reorder_blocks(ctx: RunContext[WeddingBuilderDeps], ordered_block_ids: list[str]) -> str:
    """Set section order. Pass every block id once, in top-to-bottom order; ``order`` fields are updated."""
    logger.info(
        "Builder tool reorder_blocks n=%s ids=%r",
        len(ordered_block_ids),
        ordered_block_ids,
    )
    return mutate_reorder_blocks(ctx.deps.config, ordered_block_ids)


def apply_theme(ctx: RunContext[WeddingBuilderDeps], theme_id: CuratedThemeId) -> str:
    """Apply a curated theme by id (classic-elegant or garden-romance — full theme object is set server-side)."""
    logger.info("Builder tool apply_theme theme_id=%r", theme_id)
    return mutate_apply_theme(ctx.deps.config, theme_id)


def get_full_site_config(
    ctx: RunContext[WeddingBuilderDeps],
    confirm: Annotated[
        bool,
        Field(
            default=True,
            description='Always true. Include this so the tool call uses a JSON object (e.g. {} or {"confirm":true}), never null.',
        ),
    ] = True,
) -> str:
    """
    Read-only: return the complete site configuration as JSON (same shape the builder persists). Does not save.

    Call when nested ``data`` is missing from the compact summary (photos/captions, party members, venue fields, RSVP flags, copy).
    After you read the result, you must still return a ``config`` patch (or call a mutating tool) for any edit the user asked for—
    returning ``{}`` alone leaves the site unchanged.
    """
    payload = json.dumps(ctx.deps.config, ensure_ascii=False, default=str)
    blocks = ctx.deps.config.get("blocks")
    block_count = len(blocks) if isinstance(blocks, list) else 0
    logger.info(
        "Builder tool get_full_site_config json_chars=%s block_count=%s",
        len(payload),
        block_count,
    )
    return payload


def register_site_surface_tools(agent: object) -> None:
    """Register all **site surface** tools on a PydanticAI ``Agent`` with ``WeddingBuilderDeps``."""
    for fn in (
        reorder_blocks,
        apply_theme,
        get_full_site_config,
    ):
        agent.tool(fn)  # type: ignore[attr-defined]
