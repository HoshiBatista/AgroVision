"""Unit tests for the Argon2 password hasher."""

from __future__ import annotations

from agrovision.infrastructure.security.passwords import Argon2PasswordHasher


def test_hash_verifies_correct_password() -> None:
    hasher = Argon2PasswordHasher()
    digest = hasher.hash("correct horse battery")
    assert digest != "correct horse battery"
    assert hasher.verify("correct horse battery", digest) is True


def test_hash_rejects_wrong_password() -> None:
    hasher = Argon2PasswordHasher()
    digest = hasher.hash("password123")
    assert hasher.verify("password124", digest) is False


def test_hash_rejects_malformed_stored_hash() -> None:
    hasher = Argon2PasswordHasher()
    assert hasher.verify("password123", "not-a-real-hash") is False


def test_hashes_are_salted() -> None:
    hasher = Argon2PasswordHasher()
    assert hasher.hash("same") != hasher.hash("same")
