"""Wedding site ``config`` processing for the builder agent (merge + normalize)."""

from domains.agent.config_processing.merge import (
    merge_model_config_into_base,
    merge_stored_config_with_request,
)
from domains.agent.config_processing.normalize import (
    apply_hero_names_from_user_message_when_unchanged,
    normalize_misplaced_hero_couple_fields,
    normalize_theme_color_field_aliases,
    strip_unknown_top_level_site_config_keys,
)

__all__ = [
    "apply_hero_names_from_user_message_when_unchanged",
    "merge_model_config_into_base",
    "merge_stored_config_with_request",
    "normalize_misplaced_hero_couple_fields",
    "normalize_theme_color_field_aliases",
    "strip_unknown_top_level_site_config_keys",
]
