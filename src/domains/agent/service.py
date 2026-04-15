from typing import Any, cast
from uuid import UUID

from config import settings
from domains.agent.chat_history import (
    trim_for_model,
    trim_to_max_turn_pairs,
)
from domains.agent.config_processing import (
    apply_hero_names_from_user_message_when_unchanged,
    normalize_misplaced_hero_couple_fields,
    normalize_theme_color_field_aliases,
    strip_unknown_top_level_site_config_keys,
)
from domains.agent.ports import AgentBackend
from domains.agent.turn_logging import log_agent_turn_config
from domains.anonymous_agent_sessions.service import (
    TRIAL_INTERACTION_LIMIT,
    AnonymousAgentSessionsService,
)
from domains.wedding_sites.service import WeddingSitesService
from utils.chat_history import append_turn, normalize_history
from utils.logging import get_logger

logger = get_logger(__name__)


class AgentService:
    def __init__(
        self,
        anonymous_sessions: AnonymousAgentSessionsService,
        wedding_sites: WeddingSitesService,
        backend: AgentBackend,
    ):
        self._anonymous_sessions = anonymous_sessions
        self._wedding_sites = wedding_sites
        self._backend = backend

    async def create_public_session(
        self,
    ) -> tuple[str, dict[str, Any], int, list[dict[str, str]]]:
        token, row = await self._anonymous_sessions.create_session()
        return (
            token,
            dict(row.config),
            TRIAL_INTERACTION_LIMIT,
            normalize_history(row.agent_chat_history),
        )

    async def public_turn(
        self,
        *,
        session_token: str,
        message: str,
        config: dict[str, Any] | None,
    ) -> tuple[str, dict[str, Any], int, list[dict[str, str]]]:
        row = await self._anonymous_sessions.get_active_by_plaintext_token_for_update(session_token)
        self._anonymous_sessions.ensure_can_take_turn(row)
        merged: dict[str, Any] = {**row.config, **(config or {})}
        prior = normalize_history(row.agent_chat_history)
        history_for_model = trim_for_model(prior, settings.AGENT_MODEL_HISTORY_MAX_TURNS)
        turn = await self._backend.run(
            message=message,
            config=merged,
            conversation_history=history_for_model,
        )
        reply = turn.assistant_message
        new_config = turn.config
        new_config = strip_unknown_top_level_site_config_keys(new_config)
        new_config = normalize_misplaced_hero_couple_fields(new_config)
        new_config = normalize_theme_color_field_aliases(new_config)
        new_config = apply_hero_names_from_user_message_when_unchanged(merged, new_config, message)
        log_agent_turn_config(
            logger,
            scope="public",
            site_id=None,
            user_message=message,
            merged_base=merged,
            raw_model_config=turn.model_config_patch
            if turn.model_config_patch is not None
            else new_config,
            final_config=new_config,
            llm_usage=turn.llm_usage,
            tools_used=turn.tools_used,
        )
        row.agent_chat_history = cast(
            list[dict[str, Any]],
            trim_to_max_turn_pairs(append_turn(prior, message, reply), TRIAL_INTERACTION_LIMIT),
        )
        updated = await self._anonymous_sessions.finalize_turn(row, new_config)
        remaining = max(0, TRIAL_INTERACTION_LIMIT - updated.interaction_count)
        chat_history = normalize_history(updated.agent_chat_history)
        return reply, new_config, remaining, chat_history

    async def public_session_state(
        self,
        *,
        session_token: str,
    ) -> tuple[dict[str, Any], int, list[dict[str, str]]]:
        row = await self._anonymous_sessions.get_active_by_plaintext_token(session_token)
        remaining = max(0, TRIAL_INTERACTION_LIMIT - row.interaction_count)
        chat_history = normalize_history(row.agent_chat_history)
        return dict(row.config), remaining, chat_history

    async def turn(
        self,
        *,
        owner_user_id: UUID,
        site_id: UUID,
        message: str,
        config: dict[str, Any] | None,
    ) -> tuple[str, dict[str, Any], list[dict[str, str]]]:
        site = await self._wedding_sites.get_by_id_for_user(
            site_id=site_id,
            owner_user_id=owner_user_id,
        )
        merged = {**site.config, **(config or {})}
        prior = await self._wedding_sites.list_agent_chat_history_for_site(
            site_id=site_id,
            owner_user_id=owner_user_id,
            max_turns=settings.AGENT_MODEL_HISTORY_MAX_TURNS,
        )
        history_for_model = trim_for_model(prior, settings.AGENT_MODEL_HISTORY_MAX_TURNS)
        turn = await self._backend.run(
            message=message,
            config=merged,
            conversation_history=history_for_model,
        )
        reply = turn.assistant_message
        new_config = turn.config
        new_config = strip_unknown_top_level_site_config_keys(new_config)
        new_config = normalize_misplaced_hero_couple_fields(new_config)
        new_config = normalize_theme_color_field_aliases(new_config)
        new_config = apply_hero_names_from_user_message_when_unchanged(merged, new_config, message)
        log_agent_turn_config(
            logger,
            scope="owner",
            site_id=site_id,
            user_message=message,
            merged_base=merged,
            raw_model_config=turn.model_config_patch
            if turn.model_config_patch is not None
            else new_config,
            final_config=new_config,
            llm_usage=turn.llm_usage,
            tools_used=turn.tools_used,
        )
        await self._wedding_sites.update_for_user(
            site_id=site_id,
            owner_user_id=owner_user_id,
            updates={"config": new_config},
        )
        await self._wedding_sites.append_agent_chat_turn(
            site_id=site_id,
            owner_user_id=owner_user_id,
            user_message=message,
            assistant_message=reply,
        )
        chat_history = await self._wedding_sites.list_agent_chat_history_for_site(
            site_id=site_id,
            owner_user_id=owner_user_id,
        )
        return reply, new_config, chat_history
