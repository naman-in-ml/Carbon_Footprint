"""Async database session bound to Supabase (asyncpg + Transaction Pooler)."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import settings

# statement_cache_size=0 is mandatory with PgBouncer (Transaction Pooler mode).
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=5,
    max_overflow=0,
    connect_args={"statement_cache_size": 0},
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session