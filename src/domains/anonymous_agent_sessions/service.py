import secrets
from datetime import timedelta
from typing import Any

from config import settings
from domains.anonymous_agent_sessions.exceptions import (
    AnonymousSessionExpiredError,
    AnonymousSessionNotFoundError,
    AnonymousTrialLimitExceededError,
)
from domains.anonymous_agent_sessions.models import AnonymousAgentSession
from domains.anonymous_agent_sessions.repository import AnonymousAgentSessionsRepository
from domains.anonymous_agent_sessions.token_hash import hash_session_token
from utils import utc_now

TRIAL_INTERACTION_LIMIT = 3


class AnonymousAgentSessionsService:
    def __init__(self, repository: AnonymousAgentSessionsRepository):
        self.repository = repository

    def _new_plaintext_token(self) -> str:
        return secrets.token_urlsafe(32)

    async def create_session(self) -> tuple[str, AnonymousAgentSession]:
        plaintext = self._new_plaintext_token()
        now = utc_now()
        ttl_days = max(1, settings.ANONYMOUS_AGENT_SESSION_TTL_DAYS)
        row = AnonymousAgentSession(
            token_hash=hash_session_token(plaintext),
            interaction_count=0,
            config={},
            agent_chat_history=[],
            created_at=now,
            updated_at=now,
            expires_at=now + timedelta(days=ttl_days),
        )
        saved = await self.repository.create(row)
        return plaintext, saved

    async def get_active_by_plaintext_token(self, plaintext: str) -> AnonymousAgentSession:
        row = await self.repository.get_by_token_hash(hash_session_token(plaintext))
        if row is None:
            raise AnonymousSessionNotFoundError(
                "This chat session was not found. Start a new trial session and try again."
            )
        if row.expires_at < utc_now():
            raise AnonymousSessionExpiredError(
                "This trial chat has expired. Start a new session to continue."
            )
        return row

    async def get_active_by_plaintext_token_for_update(
        self, plaintext: str
    ) -> AnonymousAgentSession:
        """Load session row with a row lock (caller's transaction) to serialize quota updates."""
        row = await self.repository.get_by_token_hash_for_update(hash_session_token(plaintext))
        if row is None:
            raise AnonymousSessionNotFoundError(
                "This chat session was not found. Start a new trial session and try again."
            )
        if row.expires_at < utc_now():
            raise AnonymousSessionExpiredError(
                "This trial chat has expired. Start a new session to continue."
            )
        return row

    def ensure_can_take_turn(self, row: AnonymousAgentSession) -> None:
        if row.interaction_count >= TRIAL_INTERACTION_LIMIT:
            raise AnonymousTrialLimitExceededError("Trial limit reached; register to continue")

    async def finalize_turn(
        self,
        row: AnonymousAgentSession,
        new_config: dict[str, Any],
    ) -> AnonymousAgentSession:
        self.ensure_can_take_turn(row)
        row.config = new_config
        row.interaction_count = row.interaction_count + 1
        row.updated_at = utc_now()
        return await self.repository.save(row)

    async def expire_session(self, row: AnonymousAgentSession) -> AnonymousAgentSession:
        row.expires_at = utc_now()
        row.updated_at = utc_now()
        return await self.repository.save(row)
