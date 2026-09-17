"""SQLAlchemy implementations of the repository ports."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agrovision.application.dto import Credentials
from agrovision.domain.report import NewSessionRecord, SessionKind, SessionRecord
from agrovision.domain.user import Role, User
from agrovision.infrastructure.db.models import SessionModel, UserModel


def _to_user(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        role=Role(model.role),
        created_at=model.created_at,
    )


def _to_session_record(model: SessionModel) -> SessionRecord:
    return SessionRecord(
        id=model.id,
        user_id=model.user_id,
        kind=SessionKind(model.kind),
        source_name=model.source_name,
        sheep_count=model.sheep_count,
        mean_confidence=model.mean_confidence,
        model_version=model.model_version,
        created_at=model.created_at,
        details=dict(model.details),
    )


class SqlAlchemyUserRepository:
    """User persistence backed by SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, email: str, password_hash: str, role: Role) -> User:
        model = UserModel(email=email, password_hash=password_hash, role=str(role))
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_user(model)

    async def get_by_id(self, user_id: int) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return _to_user(model) if model is not None else None

    async def find_credentials(self, email: str) -> Credentials | None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return Credentials(user=_to_user(model), password_hash=model.password_hash)

    async def email_exists(self, email: str) -> bool:
        result = await self._session.execute(select(UserModel.id).where(UserModel.email == email))
        return result.first() is not None


class SqlAlchemySessionRepository:
    """Session-journal persistence backed by SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, record: NewSessionRecord) -> SessionRecord:
        model = SessionModel(
            user_id=record.user_id,
            kind=str(record.kind),
            source_name=record.source_name,
            sheep_count=record.sheep_count,
            mean_confidence=record.mean_confidence,
            model_version=record.model_version,
            details=record.details,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_session_record(model)

    async def list_for_user(self, user_id: int, limit: int = 100) -> list[SessionRecord]:
        result = await self._session.execute(
            select(SessionModel)
            .where(SessionModel.user_id == user_id)
            .order_by(SessionModel.created_at.desc(), SessionModel.id.desc())
            .limit(limit)
        )
        return [_to_session_record(model) for model in result.scalars().all()]
