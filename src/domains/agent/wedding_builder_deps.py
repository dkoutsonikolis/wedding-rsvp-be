"""Runtime dependencies for the wedding builder PydanticAI agent (per-turn)."""

from dataclasses import dataclass
from typing import Any


@dataclass
class WeddingBuilderDeps:
    """Mutable working copy of site config for a single agent run (tools edit in place)."""

    config: dict[str, Any]
