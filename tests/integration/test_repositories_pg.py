"""Integration tests for the SQLAlchemy repositories against real Postgres."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agrovision.domain.report import NewSessionRecord, SessionKind
from agrovision.domain.user import Role
from agrovision.infrastructure.db.repositories import (
    SqlAlchemySessionRepository,
    SqlAlchemyUserRepository,
)


async def test_user_repository_crud(
    pg_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with pg_session_factory() as session:
        repo = SqlAlchemyUserRepository(session)
        assert await repo.email_exists("a@b.com") is False

        user = await repo.add("a@b.com", "hash-1", Role.OPERATOR)
        await session.commit()
        assert user.id > 0
        assert user.role == Role.OPERATOR

    async with pg_session_factory() as session:
        repo = SqlAlchemyUserRepository(session)
        assert await repo.email_exists("a@b.com") is True

        by_id = await repo.get_by_id(user.id)
        assert by_id is not None and by_id.email == "a@b.com"

        credentials = await repo.find_credentials("a@b.com")
        assert credentials is not None
        assert credentials.password_hash == "hash-1"
        assert credentials.user.id == user.id

        assert await repo.get_by_id(999_999) is None
        assert await repo.find_credentials("missing@b.com") is None


async def test_session_repository_orders_newest_first(
    pg_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with pg_session_factory() as session:
        user = await SqlAlchemyUserRepository(session).add("op@b.com", "h", Role.ADMIN)
        await session.commit()

    async with pg_session_factory() as session:
        repo = SqlAlchemySessionRepository(session)
        for index in range(3):
            await repo.add(
                NewSessionRecord(
                    user_id=user.id,
                    kind=SessionKind.IMAGE,
                    source_name=f"frame-{index}.jpg",
                    sheep_count=index * 5,
                    mean_confidence=0.8,
                    model_version="v1",
                    details={"i": index},
                )
            )
        await session.commit()

    async with pg_session_factory() as session:
        records = await SqlAlchemySessionRepository(session).list_for_user(user.id)
        assert len(records) == 3
        assert records[0].source_name == "frame-2.jpg"  # newest first
        assert records[0].details == {"i": 2}
        assert [r.sheep_count for r in records] == [10, 5, 0]


async def test_session_limit_is_respected(
    pg_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with pg_session_factory() as session:
        user = await SqlAlchemyUserRepository(session).add("c@b.com", "h", Role.OPERATOR)
        repo = SqlAlchemySessionRepository(session)
        for index in range(5):
            await repo.add(
                NewSessionRecord(
                    user_id=user.id,
                    kind=SessionKind.STREAM,
                    source_name=f"s{index}",
                    sheep_count=index,
                    mean_confidence=0.0,
                    model_version="v1",
                )
            )
        await session.commit()
        limited = await repo.list_for_user(user.id, limit=2)
        assert len(limited) == 2
