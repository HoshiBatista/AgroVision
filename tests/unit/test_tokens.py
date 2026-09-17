"""Unit tests for JWT token issuing, decoding, and expiry."""

from __future__ import annotations

from datetime import UTC, datetime

import jwt
import pytest

from agrovision.application.errors import UnauthorizedError
from agrovision.config import Settings
from agrovision.domain.user import Role, User
from agrovision.infrastructure.security.tokens import JwtTokenService


def _user() -> User:
    return User(id=7, email="a@b.com", role=Role.ADMIN, created_at=datetime.now(UTC))


def _service(**overrides: object) -> JwtTokenService:
    return JwtTokenService(Settings(jwt_secret="token-test-secret-000000000000000000", **overrides))


def test_access_and_refresh_roundtrip() -> None:
    service = _service()
    user = _user()

    access = service.decode(service.create_access_token(user))
    assert access.subject == 7
    assert access.role == "admin"
    assert access.kind == "access"

    refresh = service.decode(service.create_refresh_token(user))
    assert refresh.kind == "refresh"


def test_invalid_signature_rejected() -> None:
    token = _service().create_access_token(_user())
    other = JwtTokenService(Settings(jwt_secret="a-completely-different-secret-000000"))
    with pytest.raises(UnauthorizedError):
        other.decode(token)


def test_expired_token_rejected() -> None:
    service = _service(jwt_access_ttl_minutes=-1)  # already expired
    token = service.create_access_token(_user())
    with pytest.raises(UnauthorizedError):
        service.decode(token)


def test_malformed_claims_rejected() -> None:
    settings = Settings(jwt_secret="token-test-secret-000000000000000000")
    bogus = jwt.encode({"foo": "bar"}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    with pytest.raises(UnauthorizedError):
        JwtTokenService(settings).decode(bogus)


def test_garbage_token_rejected() -> None:
    with pytest.raises(UnauthorizedError):
        _service().decode("not-a-jwt")
