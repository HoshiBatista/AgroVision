"""FastAPI dependency-injection helpers reading from application state."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agrovision.application.errors import UnauthorizedError
from agrovision.application.ports import (
    DetectorPort,
    PasswordHasher,
    SessionRepository,
    TokenService,
    UserRepository,
)
from agrovision.application.use_cases.auth import AuthService, GetCurrentUser
from agrovision.application.use_cases.detect_image import DetectImageUseCase
from agrovision.application.use_cases.detect_video import DetectVideoUseCase
from agrovision.application.use_cases.reports import ListSessions
from agrovision.config import Settings
from agrovision.domain.user import User
from agrovision.infrastructure.db.repositories import (
    SqlAlchemySessionRepository,
    SqlAlchemyUserRepository,
)
from agrovision.infrastructure.storage.local_storage import LocalStorage
from agrovision.infrastructure.streaming.manager import StreamManager
from agrovision.infrastructure.video import VideoAnalyzer

BEARER_PREFIX = "Bearer "


def get_settings(request: Request) -> Settings:
    """Return the application settings from app state."""
    return request.app.state.settings


def get_detector(request: Request) -> DetectorPort:
    """Return the loaded detector from app state."""
    return request.app.state.detector


def get_request_id(request: Request) -> str:
    """Return the correlation id assigned to this request."""
    return request.state.request_id


def get_password_hasher(request: Request) -> PasswordHasher:
    """Return the shared password hasher."""
    return request.app.state.password_hasher


def get_token_service(request: Request) -> TokenService:
    """Return the shared token service."""
    return request.app.state.token_service


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield a database session, committing on success and rolling back on error."""
    factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_user_repository(session: SessionDep) -> UserRepository:
    """Construct the user repository for this request."""
    return SqlAlchemyUserRepository(session)


def get_session_repository(session: SessionDep) -> SessionRepository:
    """Construct the session-journal repository for this request."""
    return SqlAlchemySessionRepository(session)


def get_storage(request: Request) -> LocalStorage:
    """Return the shared local storage adapter."""
    return request.app.state.storage


def get_stream_manager(request: Request) -> StreamManager:
    """Return the shared stream manager."""
    return request.app.state.stream_manager


def get_detect_image_use_case(
    detector: Annotated[DetectorPort, Depends(get_detector)],
) -> DetectImageUseCase:
    """Construct the image detection use case."""
    return DetectImageUseCase(detector)


def get_detect_video_use_case(
    detector: Annotated[DetectorPort, Depends(get_detector)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DetectVideoUseCase:
    """Construct the video detection use case."""
    return DetectVideoUseCase(VideoAnalyzer(detector, settings))


def get_auth_service(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    tokens: Annotated[TokenService, Depends(get_token_service)],
) -> AuthService:
    """Construct the authentication service."""
    return AuthService(users, hasher, tokens)


def get_list_sessions(
    sessions: Annotated[SessionRepository, Depends(get_session_repository)],
) -> ListSessions:
    """Construct the list-sessions use case."""
    return ListSessions(sessions)


async def get_current_user(
    request: Request,
    users: Annotated[UserRepository, Depends(get_user_repository)],
    tokens: Annotated[TokenService, Depends(get_token_service)],
) -> User:
    """Resolve the authenticated user from the bearer access token."""
    header = request.headers.get("Authorization", "")
    if not header.startswith(BEARER_PREFIX):
        raise UnauthorizedError("Missing bearer token")
    token = header[len(BEARER_PREFIX) :]
    return await GetCurrentUser(users, tokens).execute(token)


def get_optional_user_id(
    request: Request,
    tokens: Annotated[TokenService, Depends(get_token_service)],
) -> int | None:
    """Return the user id from a valid bearer access token, or None.

    Used to attach a journal entry when the caller is authenticated, without
    forcing authentication on the public inference endpoints.
    """
    header = request.headers.get("Authorization", "")
    if not header.startswith(BEARER_PREFIX):
        return None
    try:
        payload = tokens.decode(header[len(BEARER_PREFIX) :])
    except UnauthorizedError:
        return None
    return payload.subject if payload.kind == "access" else None


SettingsDep = Annotated[Settings, Depends(get_settings)]
RequestIdDep = Annotated[str, Depends(get_request_id)]
StorageDep = Annotated[LocalStorage, Depends(get_storage)]
StreamManagerDep = Annotated[StreamManager, Depends(get_stream_manager)]
DetectImageDep = Annotated[DetectImageUseCase, Depends(get_detect_image_use_case)]
DetectVideoDep = Annotated[DetectVideoUseCase, Depends(get_detect_video_use_case)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
OptionalUserIdDep = Annotated[int | None, Depends(get_optional_user_id)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
SessionRepositoryDep = Annotated[SessionRepository, Depends(get_session_repository)]
ListSessionsDep = Annotated[ListSessions, Depends(get_list_sessions)]
