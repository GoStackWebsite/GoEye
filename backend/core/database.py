"""Async SQLAlchemy engine, session factory, declarative base and table setup."""
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from backend.core.config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# Parent class for every SQLAlchemy model
class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


async def create_tables() -> None:
    """Create tables for all imported models. Dev only; replace with Alembic migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
