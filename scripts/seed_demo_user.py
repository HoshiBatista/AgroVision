"""Seed a demo operator account so the UI can be logged into immediately.

Idempotent: does nothing if the demo user already exists. Requires the database
to be up and migrated (`make db-up && make migrate`).

Usage:
    uv run python -m scripts.seed_demo_user
"""

from __future__ import annotations

import asyncio

from agrovision.config import get_settings
from agrovision.domain.user import Role
from agrovision.infrastructure.db.engine import create_engine, create_session_factory
from agrovision.infrastructure.db.repositories import SqlAlchemyUserRepository
from agrovision.infrastructure.security.passwords import Argon2PasswordHasher

DEMO_EMAIL = "operator@farm.com"
DEMO_PASSWORD = "sheep12345"


async def _seed() -> None:
    settings = get_settings()
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)
    hasher = Argon2PasswordHasher()
    try:
        async with session_factory() as session:
            repository = SqlAlchemyUserRepository(session)
            if await repository.email_exists(DEMO_EMAIL):
                print(f"Demo user already exists: {DEMO_EMAIL}")
                return
            await repository.add(DEMO_EMAIL, hasher.hash(DEMO_PASSWORD), Role.ADMIN)
            await session.commit()
            print(f"Created demo user: {DEMO_EMAIL} / {DEMO_PASSWORD}")
    finally:
        await engine.dispose()


def main() -> None:
    """Entry point."""
    asyncio.run(_seed())


if __name__ == "__main__":
    main()
