import re
from typing import Any, TypedDict
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError

from domains.wedding_sites.enums import AgentMessageRole, SiteStatus
from domains.wedding_sites.exceptions import (
    InvalidSlugError,
    SlugConflictError,
    WeddingSiteNotFoundError,
)
from domains.wedding_sites.models import AgentConversationMessage, WeddingSite
from domains.wedding_sites.repository import WeddingSitesRepository
from utils import utc_now
from utils.logging import get_logger

logger = get_logger(__name__)


class WeddingSitePartialUpdate(TypedDict, total=False):
    """Fields to change; a key must be present to apply that field (including ``title: None`` to clear)."""

    title: str | None
    slug: str
    status: SiteStatus
    config: dict[str, Any]
    schema_version: int


class WeddingSitesService:
    _slug_pattern = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    def __init__(self, repository: WeddingSitesRepository):
        self.repository = repository

    def _normalize_slug(self, raw: str) -> str:
        s = raw.strip().lower()
        if not s:
            raise InvalidSlugError("Slug cannot be empty")
        if not self._slug_pattern.fullmatch(s):
            raise InvalidSlugError(
                "Slug must be lowercase letters, digits, and hyphens only (hyphens not at ends)"
            )
        return s

    def _slugify_title(self, title: str) -> str:
        s = title.strip().lower()
        s = re.sub(r"[^a-z0-9]+", "-", s)
        s = re.sub(r"-+", "-", s).strip("-")
        if not s or not self._slug_pattern.fullmatch(s):
            return ""
        return s

    def _random_slug_base(self) -> str:
        return f"site-{uuid4().hex[:12]}"

    async def _allocate_unique_slug(self, base: str) -> str:
        if not base or not self._slug_pattern.fullmatch(base):
            base = self._random_slug_base()
        candidate = base
        suffix = 2
        while await self.repository.get_by_slug(candidate) is not None:
            candidate = f"{base}-{suffix}"
            suffix += 1
        return candidate

    def _agent_conversation_rows_to_history(
        self, rows: list[AgentConversationMessage]
    ) -> list[dict[str, str]]:
        return [{"role": str(row.role), "content": row.content} for row in rows]

    async def list_for_user(self, owner_user_id: UUID) -> list[WeddingSite]:
        return await self.repository.list_for_user(owner_user_id)

    async def get_by_id_for_user(self, *, site_id: UUID, owner_user_id: UUID) -> WeddingSite:
        site = await self.repository.get_by_id_for_user(
            site_id=site_id, owner_user_id=owner_user_id
        )
        if site is None:
            raise WeddingSiteNotFoundError("Wedding site not found")
        return site

    async def create(
        self,
        *,
        owner_user_id: UUID,
        title: str | None = None,
        slug: str | None = None,
        status: SiteStatus = SiteStatus.DRAFT,
        config: dict[str, Any] | None = None,
        schema_version: int = 1,
    ) -> WeddingSite:
        if slug is not None and slug.strip():
            normalized = self._normalize_slug(slug)
            existing = await self.repository.get_by_slug(normalized)
            if existing is not None:
                raise SlugConflictError(f"Slug '{normalized}' is already in use")
        else:
            base: str
            if title and title.strip():
                base = self._slugify_title(title) or self._random_slug_base()
            else:
                base = self._random_slug_base()
            normalized = await self._allocate_unique_slug(base)
        site = WeddingSite(
            owner_user_id=owner_user_id,
            slug=normalized,
            title=title,
            status=status,
            config=dict(config) if config is not None else {},
            schema_version=schema_version,
        )
        try:
            return await self.repository.create(site)
        except IntegrityError as e:
            logger.warning("create wedding site failed integrity check: %s", e)
            raise SlugConflictError(f"Slug '{normalized}' is already in use") from e

    async def update_for_user(
        self,
        *,
        site_id: UUID,
        owner_user_id: UUID,
        updates: WeddingSitePartialUpdate,
    ) -> WeddingSite:
        site = await self.repository.get_by_id_for_user(
            site_id=site_id, owner_user_id=owner_user_id
        )
        if site is None:
            raise WeddingSiteNotFoundError("Wedding site not found")

        if "title" in updates:
            site.title = updates["title"]

        if "slug" in updates:
            normalized = self._normalize_slug(updates["slug"])
            other = await self.repository.get_by_slug(normalized)
            if other is not None and other.id != site.id:
                raise SlugConflictError(f"Slug '{normalized}' is already in use")
            site.slug = normalized

        if "status" in updates:
            site.status = updates["status"]

        if "config" in updates:
            site.config = dict(updates["config"])

        if "schema_version" in updates:
            site.schema_version = updates["schema_version"]

        site.updated_at = utc_now()
        try:
            return await self.repository.save(site)
        except IntegrityError as e:
            logger.warning("update wedding site failed integrity check: %s", e)
            raise SlugConflictError("Slug is already in use") from e

    async def list_agent_conversation_messages_for_site(
        self,
        *,
        site_id: UUID,
        owner_user_id: UUID,
        limit: int | None = None,
    ) -> list[AgentConversationMessage]:
        await self.get_by_id_for_user(site_id=site_id, owner_user_id=owner_user_id)
        return await self.repository.list_agent_conversation_messages(
            wedding_site_id=site_id,
            limit=limit,
        )

    async def list_agent_chat_history_for_site(
        self,
        *,
        site_id: UUID,
        owner_user_id: UUID,
        max_turns: int | None = None,
    ) -> list[dict[str, str]]:
        if max_turns is not None and max_turns < 0:
            raise ValueError("max_turns cannot be negative")
        message_limit = None if max_turns is None else max_turns * 2
        rows = await self.list_agent_conversation_messages_for_site(
            site_id=site_id,
            owner_user_id=owner_user_id,
            limit=message_limit,
        )
        return self._agent_conversation_rows_to_history(rows)

    async def append_agent_chat_turn(
        self,
        *,
        site_id: UUID,
        owner_user_id: UUID,
        user_message: str,
        assistant_message: str,
    ) -> None:
        await self.get_by_id_for_user(site_id=site_id, owner_user_id=owner_user_id)
        user_row = AgentConversationMessage(
            wedding_site_id=site_id,
            role=AgentMessageRole.USER,
            content=user_message,
        )
        assistant_row = AgentConversationMessage(
            wedding_site_id=site_id,
            role=AgentMessageRole.ASSISTANT,
            content=assistant_message,
        )
        await self.repository.add_agent_conversation_messages([user_row, assistant_row])

    async def delete_for_user(self, *, site_id: UUID, owner_user_id: UUID) -> None:
        site = await self.repository.get_by_id_for_user(
            site_id=site_id, owner_user_id=owner_user_id
        )
        if site is None:
            raise WeddingSiteNotFoundError("Wedding site not found")
        await self.repository.delete(site)
