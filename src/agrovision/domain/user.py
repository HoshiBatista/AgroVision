"""User identity domain model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Role(StrEnum):
    """Access role for an authenticated user."""

    OPERATOR = "operator"
    ADMIN = "admin"


@dataclass(frozen=True, slots=True)
class User:
    """An authenticated user identity (never carries the password hash)."""

    id: int
    email: str
    role: Role
    created_at: datetime
