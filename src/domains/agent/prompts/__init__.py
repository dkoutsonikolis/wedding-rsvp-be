"""Versioned prompt assets for the wedding builder agent (plain text / markdown).

Use ``importlib.resources`` so prompt files resolve correctly from wheels, Docker, and
editable installs. Add Jinja (or another templating layer) only when prompts need
runtime variables; static text stays as ``.txt`` / ``.md`` files.
"""

from functools import lru_cache
from importlib.resources import files


@lru_cache(maxsize=16)
def load_prompt_text(name: str) -> str:
    """Load a UTF-8 prompt file shipped with this package."""
    return files(__package__).joinpath(name).read_text(encoding="utf-8").strip()


@lru_cache(maxsize=1)
def default_wedding_builder_system_prompt() -> str:
    """System prompt for ``StructuredAgentBackend`` (wedding builder)."""
    return load_prompt_text("wedding_builder_system.txt")
