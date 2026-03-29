from typing import Any
from uuid import UUID

from domains.agent.backend import StubAgentBackend
from domains.anonymous_agent_sessions.service import (
    TRIAL_INTERACTION_LIMIT,
    AnonymousAgentSessionsService,
)
from domains.wedding_sites.service import WeddingSitesService


class AgentService:
    def __init__(
        self,
        anonymous_sessions: AnonymousAgentSessionsService,
        wedding_sites: WeddingSitesService,
        backend: StubAgentBackend | None = None,
    ):
        self._anonymous_sessions = anonymous_sessions
        self._wedding_sites = wedding_sites
        self._backend = backend or StubAgentBackend()

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
        reply, new_config = await self._backend.run(message=message, config=merged)
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
        reply, new_config = await self._backend.run(message=message, config=merged)
        await self._wedding_sites.update_for_user(
            site_id=site_id,
            owner_user_id=owner_user_id,
            updates={"config": new_config},
        )
        return reply, new_config
