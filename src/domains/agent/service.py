from typing import Any
from uuid import UUID

from domains.agent.config_processing import (
    apply_hero_names_from_user_message_when_unchanged,
    normalize_misplaced_hero_couple_fields,
    strip_unknown_top_level_site_config_keys,
)
from domains.agent.ports import AgentBackend
from domains.agent.turn_logging import log_agent_turn_config
from domains.anonymous_agent_sessions.service import (
    TRIAL_INTERACTION_LIMIT,
    AnonymousAgentSessionsService,
)
from domains.wedding_sites.service import WeddingSitesService
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
    ) -> tuple[str, dict[str, Any], int]:
        token, row = await self._anonymous_sessions.create_session()
        return token, dict(row.config), TRIAL_INTERACTION_LIMIT

    async def public_turn(
        self,
        *,
        session_token: str,
        message: str,
        config: dict[str, Any] | None,
    ) -> tuple[str, dict[str, Any], int]:
        row = await self._anonymous_sessions.get_active_by_plaintext_token_for_update(session_token)
        self._anonymous_sessions.ensure_can_take_turn(row)
        merged: dict[str, Any] = {**row.config, **(config or {})}
        turn = await self._backend.run(message=message, config=merged)
        reply = turn.assistant_message
        new_config = turn.config
        new_config = strip_unknown_top_level_site_config_keys(new_config)
        new_config = normalize_misplaced_hero_couple_fields(new_config)
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
        updated = await self._anonymous_sessions.finalize_turn(row, new_config)
        remaining = max(0, TRIAL_INTERACTION_LIMIT - updated.interaction_count)
        return reply, new_config, remaining

    async def turn(
        self,
        *,
        owner_user_id: UUID,
        site_id: UUID,
        message: str,
        config: dict[str, Any] | None,
    ) -> tuple[str, dict[str, Any]]:
        site = await self._wedding_sites.get_by_id_for_user(
            site_id=site_id,
            owner_user_id=owner_user_id,
        )
        merged = {**site.config, **(config or {})}
        turn = await self._backend.run(message=message, config=merged)
        reply = turn.assistant_message
        new_config = turn.config
        new_config = strip_unknown_top_level_site_config_keys(new_config)
        new_config = normalize_misplaced_hero_couple_fields(new_config)
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
        return reply, new_config
