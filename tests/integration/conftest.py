"""Shared fixtures for real-database integration tests (PostgreSQL).

These exercise the actual SQLAlchemy repositories and DB-backed endpoints against a
real Postgres engine — the same code path used in production. They are skipped
automatically when the test database is unreachable, so the suite still passes
without Docker.

Point them at a database with ``TEST_DATABASE_URL``; the default matches
``docker compose up -d db`` plus a dedicated ``agrovision_test`` database.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from agrovision.infrastructure.db.models import Base

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://agrovision:agrovision@localhost:5432/agrovision_test",
)


async def _reset_schema() -> bool:
    """Drop and recreate all tables. Returns False if the database is unreachable."""
    engine = create_async_engine(TEST_DATABASE_URL)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)
        return True
    except (SQLAlchemyError, OSError, ConnectionError):
        return False
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def pg_session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    """A clean Postgres schema and a session factory bound to it."""
    engine = create_async_engine(TEST_DATABASE_URL)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)
    except (SQLAlchemyError, OSError, ConnectionError) as exc:
        await engine.dispose()
        pytest.skip(f"Postgres test database not reachable: {exc}")
    try:
        yield async_sessionmaker(engine, expire_on_commit=False)
    finally:
        await engine.dispose()
