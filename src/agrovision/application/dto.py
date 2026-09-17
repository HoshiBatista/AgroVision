"""Data transfer objects passed across application boundaries."""

from __future__ import annotations

from dataclasses import dataclass

from agrovision.domain.counting import VideoCountSummary
from agrovision.domain.user import User


@dataclass(frozen=True, slots=True)
class Credentials:
    """A user identity bundled with its stored password hash for verification."""

    user: User
    password_hash: str


@dataclass(frozen=True, slots=True)
class TokenPair:
    """An issued access/refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass(frozen=True, slots=True)
class TokenPayload:
    """Decoded JWT claims relevant to the application."""

    subject: int
    role: str
    kind: str  # "access" or "refresh"


@dataclass(frozen=True, slots=True)
class VideoAnalysis:
    """The raw output of analysing a video: count series and keyframe JPEGs."""

    summary: VideoCountSummary
    keyframes: tuple[bytes, ...]
