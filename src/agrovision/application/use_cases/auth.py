"""Authentication use cases: register, login, refresh."""

from __future__ import annotations

from dataclasses import dataclass

from agrovision.application.dto import TokenPair
from agrovision.application.errors import ConflictError, UnauthorizedError, ValidationError
from agrovision.application.ports import PasswordHasher, TokenService, UserRepository
from agrovision.domain.user import Role, User

_MIN_PASSWORD_LENGTH = 8


@dataclass(frozen=True, slots=True)
class AuthResult:
    """A successful authentication returning the user and a token pair."""

    user: User
    tokens: TokenPair


class AuthService:
    """Registration, login, and refresh built on the auth ports."""

    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        tokens: TokenService,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens

    async def register(self, email: str, password: str, role: Role = Role.OPERATOR) -> AuthResult:
        """Create a new user and return issued tokens."""
        email = email.strip().lower()
        if len(password) < _MIN_PASSWORD_LENGTH:
            raise ValidationError("Password must be at least 8 characters")
        if await self._users.email_exists(email):
            raise ConflictError("A user with this email already exists")
        user = await self._users.add(email, self._hasher.hash(password), role)
        return AuthResult(user=user, tokens=self._issue(user))

    async def login(self, email: str, password: str) -> AuthResult:
        """Authenticate a user and return issued tokens."""
        email = email.strip().lower()
        credentials = await self._users.find_credentials(email)
        if credentials is None or not self._hasher.verify(password, credentials.password_hash):
            raise UnauthorizedError("Invalid email or password")
        return AuthResult(user=credentials.user, tokens=self._issue(credentials.user))

    async def refresh(self, refresh_token: str) -> AuthResult:
        """Exchange a valid refresh token for a new token pair."""
        payload = self._tokens.decode(refresh_token)
        if payload.kind != "refresh":
            raise UnauthorizedError("Expected a refresh token")
        user = await self._users.get_by_id(payload.subject)
        if user is None:
            raise UnauthorizedError("User no longer exists")
        return AuthResult(user=user, tokens=self._issue(user))

    def _issue(self, user: User) -> TokenPair:
        return TokenPair(
            access_token=self._tokens.create_access_token(user),
            refresh_token=self._tokens.create_refresh_token(user),
        )


class GetCurrentUser:
    """Resolve a user from an access token."""

    def __init__(self, users: UserRepository, tokens: TokenService) -> None:
        self._users = users
        self._tokens = tokens

    async def execute(self, access_token: str) -> User:
        """Decode an access token and load the corresponding user."""
        payload = self._tokens.decode(access_token)
        if payload.kind != "access":
            raise UnauthorizedError("Expected an access token")
        user = await self._users.get_by_id(payload.subject)
        if user is None:
            raise UnauthorizedError("User no longer exists")
        return user
