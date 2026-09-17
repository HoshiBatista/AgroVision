"""Async SQLAlchemy engine and session factory."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from agrovision.config import Settings


def create_engine(settings: Settings) -> AsyncEngine:
    """Create an async engine. Connections are lazy; the DB need not be up yet."""
    return create_async_engine(settings.database_url, pool_pre_ping=True, future=True)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    """Create a session factory bound to the engine."""
    return async_sessionmaker(engine, expire_on_commit=False)
