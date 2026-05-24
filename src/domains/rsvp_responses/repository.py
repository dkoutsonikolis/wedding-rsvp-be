from uuid import UUID

from sqlalchemy import and_, desc, or_
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from domains.rsvp_responses.models import RsvpResponse


class RsvpResponsesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, response: RsvpResponse) -> RsvpResponse:
        self.session.add(response)
        await self.session.commit()
        await self.session.refresh(response)
        return response

    async def list_by_wedding_site_id(
        self,
        wedding_site_id: UUID,
        limit: int | None = None,
        before_response_id: UUID | None = None,
    ) -> list[RsvpResponse]:
        """Newest-first. ``before_response_id`` returns rows older than that response."""
        stmt = select(RsvpResponse).where(RsvpResponse.wedding_site_id == wedding_site_id)
        if before_response_id is not None:
            cursor_row_result = await self.session.exec(
                select(RsvpResponse).where(
                    RsvpResponse.wedding_site_id == wedding_site_id,
                    RsvpResponse.id == before_response_id,
                )
            )
            cursor_row = cursor_row_result.first()
            if cursor_row is None:
                return []
            stmt = stmt.where(
                or_(
                    col(RsvpResponse.created_at) < cursor_row.created_at,
                    and_(
                        col(RsvpResponse.created_at) == cursor_row.created_at,
                        col(RsvpResponse.id) < cursor_row.id,
                    ),
                )
            )
        stmt = stmt.order_by(
            desc(col(RsvpResponse.created_at)),
            desc(col(RsvpResponse.id)),
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.exec(stmt)
        return list(result.all())
