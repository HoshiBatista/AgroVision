"""Unit tests for the authentication service."""

from __future__ import annotations

import pytest

from agrovision.application.errors import ConflictError, UnauthorizedError, ValidationError
from agrovision.application.use_cases.auth import AuthService, GetCurrentUser
from agrovision.config import Settings
from agrovision.infrastructure.security.passwords import Argon2PasswordHasher
from agrovision.infrastructure.security.tokens import JwtTokenService
from tests.fakes import FakeUserRepository


def _service() -> tuple[AuthService, FakeUserRepository, JwtTokenService]:
    settings = Settings(jwt_secret="unit-test-secret-please-change-000000")
    users = FakeUserRepository()
    tokens = JwtTokenService(settings)
    return AuthService(users, Argon2PasswordHasher(), tokens), users, tokens


async def test_register_normalizes_email_and_issues_tokens() -> None:
    service, _, _ = _service()
    result = await service.register("  User@Example.COM ", "password123")
    assert result.user.email == "user@example.com"
    assert result.tokens.access_token
    assert result.tokens.refresh_token


async def test_register_rejects_short_password() -> None:
    service, _, _ = _service()
    with pytest.raises(ValidationError):
        await service.register("a@b.com", "short")


async def test_register_rejects_duplicate() -> None:
    service, _, _ = _service()
    await service.register("a@b.com", "password123")
    with pytest.raises(ConflictError):
        await service.register("a@b.com", "password123")


async def test_login_rejects_wrong_password() -> None:
    service, _, _ = _service()
    await service.register("a@b.com", "password123")
    with pytest.raises(UnauthorizedError):
        await service.login("a@b.com", "wrong-password")


async def test_refresh_round_trip() -> None:
    service, _, _ = _service()
    registered = await service.register("a@b.com", "password123")
    refreshed = await service.refresh(registered.tokens.refresh_token)
    assert refreshed.user.email == "a@b.com"
    assert refreshed.tokens.access_token


async def test_refresh_rejects_access_token() -> None:
    service, _, _ = _service()
    registered = await service.register("a@b.com", "password123")
    with pytest.raises(UnauthorizedError):
        await service.refresh(registered.tokens.access_token)


async def test_get_current_user_from_access_token() -> None:
    service, users, tokens = _service()
    registered = await service.register("a@b.com", "password123")
    user = await GetCurrentUser(users, tokens).execute(registered.tokens.access_token)
    assert user.id == registered.user.id


async def test_get_current_user_rejects_refresh_token() -> None:
    service, users, tokens = _service()
    registered = await service.register("a@b.com", "password123")
    with pytest.raises(UnauthorizedError):
        await GetCurrentUser(users, tokens).execute(registered.tokens.refresh_token)
