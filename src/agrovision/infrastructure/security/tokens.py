"""JWT token service implementing the TokenService port."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt

from agrovision.application.dto import TokenPayload
from agrovision.application.errors import UnauthorizedError
from agrovision.config import Settings
from agrovision.domain.user import User

_ACCESS = "access"
_REFRESH = "refresh"


class JwtTokenService:
    """Issue and decode signed JWT access/refresh tokens."""

    def __init__(self, settings: Settings) -> None:
        self._secret = settings.jwt_secret
        self._algorithm = settings.jwt_algorithm
        self._access_ttl = timedelta(minutes=settings.jwt_access_ttl_minutes)
        self._refresh_ttl = timedelta(days=settings.jwt_refresh_ttl_days)

    def create_access_token(self, user: User) -> str:
        """Create a signed short-lived access token."""
        return self._encode(user, _ACCESS, self._access_ttl)

    def create_refresh_token(self, user: User) -> str:
        """Create a signed long-lived refresh token."""
        return self._encode(user, _REFRESH, self._refresh_ttl)

    def _encode(self, user: User, kind: str, ttl: timedelta) -> str:
        now = datetime.now(UTC)
        claims = {
            "sub": str(user.id),
            "role": str(user.role),
            "kind": kind,
            "iat": int(now.timestamp()),
            "exp": int((now + ttl).timestamp()),
        }
        return jwt.encode(claims, self._secret, algorithm=self._algorithm)

    def decode(self, token: str) -> TokenPayload:
        """Decode and validate a token, raising UnauthorizedError on failure."""
        try:
            claims = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Invalid or expired token") from exc
        try:
            return TokenPayload(
                subject=int(claims["sub"]),
                role=str(claims["role"]),
                kind=str(claims["kind"]),
            )
        except (KeyError, ValueError) as exc:
            raise UnauthorizedError("Malformed token claims") from exc
