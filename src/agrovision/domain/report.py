"""Session journal domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class SessionKind(StrEnum):
    """The kind of inference that produced a journal entry."""

    IMAGE = "image"
    VIDEO = "video"
    STREAM = "stream"


@dataclass(frozen=True, slots=True)
class SessionRecord:
    """A persisted record of one inference session for the audit journal."""

    id: int
    user_id: int
    kind: SessionKind
    source_name: str
    sheep_count: int
    mean_confidence: float
    model_version: str
    created_at: datetime
    details: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class NewSessionRecord:
    """A session record to persist (before it receives a database id)."""

    user_id: int
    kind: SessionKind
    source_name: str
    sheep_count: int
    mean_confidence: float
    model_version: str
    details: dict[str, object] = field(default_factory=dict)
