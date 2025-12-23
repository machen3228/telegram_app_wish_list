from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from .config import settings

async_engine: AsyncEngine = create_async_engine(
    url=settings.db_url,
    echo=True,
)

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    autoflush=False, bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
