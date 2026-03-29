from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from domains.anonymous_agent_sessions.models import AnonymousAgentSession


class AnonymousAgentSessionsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, row: AnonymousAgentSession) -> AnonymousAgentSession:
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def get_by_token_hash(self, token_hash: str) -> AnonymousAgentSession | None:
        result = await self.session.exec(
            select(AnonymousAgentSession).where(AnonymousAgentSession.token_hash == token_hash)
        )
        return result.first()

    async def get_by_token_hash_for_update(self, token_hash: str) -> AnonymousAgentSession | None:
        result = await self.session.exec(
            select(AnonymousAgentSession)
            .where(AnonymousAgentSession.token_hash == token_hash)
            .with_for_update()
        )
        return result.first()

    async def save(self, row: AnonymousAgentSession) -> AnonymousAgentSession:
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return row
