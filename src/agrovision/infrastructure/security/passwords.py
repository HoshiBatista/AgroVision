"""Argon2 password hasher implementing the PasswordHasher port."""

from __future__ import annotations

from argon2 import PasswordHasher as _Argon2
from argon2.exceptions import Argon2Error, InvalidHashError, VerifyMismatchError


class Argon2PasswordHasher:
    """Hash and verify passwords with Argon2id."""

    def __init__(self) -> None:
        self._hasher = _Argon2()

    def hash(self, password: str) -> str:
        """Return a salted Argon2 hash for the given plaintext password."""
        return self._hasher.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        """Return whether the plaintext password matches the stored hash."""
        try:
            return self._hasher.verify(password_hash, password)
        except (VerifyMismatchError, InvalidHashError, Argon2Error):
            return False
