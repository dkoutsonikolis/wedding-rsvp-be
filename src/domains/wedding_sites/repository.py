from uuid import UUID

from sqlalchemy import and_, delete, desc, or_
from sqlalchemy.exc import IntegrityError
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from domains.wedding_sites.models import AgentConversationMessage, WeddingSite


class WeddingSitesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id_for_user(self, *, site_id: UUID, owner_user_id: UUID) -> WeddingSite | None:
        result = await self.session.exec(
            select(WeddingSite).where(
                WeddingSite.id == site_id,
                WeddingSite.owner_user_id == owner_user_id,
            )
        )
        return result.first()

    async def list_for_user(self, owner_user_id: UUID) -> list[WeddingSite]:
        result = await self.session.exec(
            select(WeddingSite)
            .where(WeddingSite.owner_user_id == owner_user_id)
            .order_by(WeddingSite.created_at)  # type: ignore[arg-type]
        )
        return list(result.all())

    async def get_by_slug(self, slug: str) -> WeddingSite | None:
        result = await self.session.exec(select(WeddingSite).where(WeddingSite.slug == slug))
        return result.first()

    async def create(self, site: WeddingSite) -> WeddingSite:
        try:
            self.session.add(site)
            await self.session.commit()
            await self.session.refresh(site)
            return site
        except IntegrityError:
            await self.session.rollback()
            raise

    async def save(self, site: WeddingSite) -> WeddingSite:
        try:
            self.session.add(site)
            await self.session.commit()
            await self.session.refresh(site)
            return site
        except IntegrityError:
            await self.session.rollback()
            raise

    async def delete(self, site: WeddingSite) -> None:
        await self.session.exec(delete(WeddingSite).where(col(WeddingSite.id) == site.id))
        await self.session.commit()

    async def list_agent_conversation_messages(
        self,
        *,
        wedding_site_id: UUID,
        limit: int | None = None,
        before_message_id: UUID | None = None,
    ) -> list[AgentConversationMessage]:
        """List messages oldest-first. When ``limit`` is set, only the last ``limit`` rows (by time)."""
        stmt = select(AgentConversationMessage).where(
            AgentConversationMessage.wedding_site_id == wedding_site_id
        )
        if before_message_id is not None:
            cursor_row_result = await self.session.exec(
                select(AgentConversationMessage).where(
                    AgentConversationMessage.wedding_site_id == wedding_site_id,
                    AgentConversationMessage.id == before_message_id,
                )
            )
            cursor_row = cursor_row_result.first()
            if cursor_row is None:
                return []
            stmt = stmt.where(
                or_(
                    col(AgentConversationMessage.created_at) < cursor_row.created_at,
                    and_(
                        col(AgentConversationMessage.created_at) == cursor_row.created_at,
                        col(AgentConversationMessage.id) < cursor_row.id,
                    ),
                )
            )
        if limit is not None:
            stmt = stmt.order_by(
                desc(col(AgentConversationMessage.created_at)),
                desc(col(AgentConversationMessage.id)),
            ).limit(limit)
            result = await self.session.exec(stmt)
            rows = list(result.all())
            rows.reverse()
            return rows
        result = await self.session.exec(
            stmt.order_by(
                col(AgentConversationMessage.created_at), col(AgentConversationMessage.id)
            )
        )
        return list(result.all())

    async def add_agent_conversation_messages(
        self, messages: list[AgentConversationMessage]
    ) -> None:
        for message in messages:
            self.session.add(message)
        await self.session.commit()
