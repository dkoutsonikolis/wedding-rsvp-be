from uuid import UUID

from sqlalchemy import and_, case, desc, func, or_
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from domains.rsvp_responses.models import RsvpResponse

_ILIKE_ESCAPE = "\\"


def _non_empty_notes_condition():
    trimmed = func.trim(col(RsvpResponse.notes))
    return and_(col(RsvpResponse.notes).is_not(None), trimmed != "")


def _ilike_contains_pattern(term: str) -> str:
    escaped = (
        term.replace(_ILIKE_ESCAPE, _ILIKE_ESCAPE + _ILIKE_ESCAPE)
        .replace("%", _ILIKE_ESCAPE + "%")
        .replace("_", _ILIKE_ESCAPE + "_")
    )
    return f"%{escaped}%"


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
        q: str | None = None,
        is_attending: bool | None = None,
    ) -> list[RsvpResponse]:
        """Newest-first. ``before_response_id`` returns rows older than that response."""
        stmt = select(RsvpResponse).where(RsvpResponse.wedding_site_id == wedding_site_id)
        if is_attending is not None:
            stmt = stmt.where(RsvpResponse.is_attending == is_attending)
        if q is not None:
            pattern = _ilike_contains_pattern(q)
            stmt = stmt.where(
                or_(
                    col(RsvpResponse.name).ilike(pattern, escape=_ILIKE_ESCAPE),
                    col(RsvpResponse.email).ilike(pattern, escape=_ILIKE_ESCAPE),
                    col(RsvpResponse.phone).ilike(pattern, escape=_ILIKE_ESCAPE),
                    col(RsvpResponse.notes).ilike(pattern, escape=_ILIKE_ESCAPE),
                )
            )
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

    async def get_summary_counts_for_wedding_site_id(
        self,
        wedding_site_id: UUID,
    ) -> tuple[int, int, int, int]:
        """Returns total_responses, attending_count, declined_count, total_guests."""
        stmt = select(
            func.count(),
            func.sum(case((col(RsvpResponse.is_attending).is_(True), 1), else_=0)),
            func.sum(case((col(RsvpResponse.is_attending).is_(False), 1), else_=0)),
            func.coalesce(
                func.sum(
                    case(
                        (col(RsvpResponse.is_attending).is_(True), col(RsvpResponse.party_size)),
                        else_=0,
                    )
                ),
                0,
            ),
        ).where(RsvpResponse.wedding_site_id == wedding_site_id)
        result = await self.session.exec(stmt)
        row = result.one()
        total_responses = int(row[0] or 0)
        attending_count = int(row[1] or 0)
        declined_count = int(row[2] or 0)
        total_guests = int(row[3] or 0)
        return total_responses, attending_count, declined_count, total_guests

    async def list_recent_by_wedding_site_id(
        self,
        wedding_site_id: UUID,
        limit: int,
    ) -> list[RsvpResponse]:
        return await self.list_by_wedding_site_id(
            wedding_site_id=wedding_site_id,
            limit=limit,
        )

    async def list_with_notes_by_wedding_site_id(
        self,
        wedding_site_id: UUID,
        limit: int,
    ) -> list[RsvpResponse]:
        stmt = (
            select(RsvpResponse)
            .where(
                RsvpResponse.wedding_site_id == wedding_site_id,
                _non_empty_notes_condition(),
            )
            .order_by(
                desc(col(RsvpResponse.created_at)),
                desc(col(RsvpResponse.id)),
            )
            .limit(limit)
        )
        result = await self.session.exec(stmt)
        return list(result.all())
