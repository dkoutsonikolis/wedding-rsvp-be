from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from config import settings

# Create async engine with connection pooling
# - pool_size: number of connections to maintain
# - max_overflow: additional connections beyond pool_size
# - pool_pre_ping: verify connections before using (prevents stale connections)
# - echo: log SQL queries (useful for debugging)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(engine) as session:
        yield session
