from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from domains.wedding_sites.models import WeddingSite


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
        await self.session.exec(delete(WeddingSite).where(WeddingSite.id == site.id))
        await self.session.commit()
