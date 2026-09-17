"""Reusable in-memory fakes for tests (no model download, no database)."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from agrovision.application.dto import Credentials
from agrovision.application.ports import Image
from agrovision.domain.counting import FrameResult
from agrovision.domain.detection import BoundingBox, Detection
from agrovision.domain.model import ModelMetadata
from agrovision.domain.report import NewSessionRecord, SessionRecord
from agrovision.domain.user import Role, User


class FakeDetector:
    """Detector stub returning a fixed set of detections."""

    def __init__(self, detections: tuple[Detection, ...] = ()) -> None:
        self._detections = detections or (
            Detection("sheep", 0.9, BoundingBox(10, 10, 40, 40)),
            Detection("sheep", 0.2, BoundingBox(50, 50, 80, 80)),
        )
        self._metadata = ModelMetadata(
            name="fake",
            version="test",
            weights_path="memory://fake",
            weights_sha256="0" * 64,
            device="cpu",
            image_size=640,
            confidence_threshold=0.25,
            classes=("sheep",),
            limitations=("test model",),
        )

    @property
    def metadata(self) -> ModelMetadata:
        return self._metadata

    def detect(self, image: Image) -> FrameResult:
        height, width = image.shape[:2]
        return FrameResult(detections=self._detections, width=int(width), height=int(height))

    def set_confidence_threshold(self, threshold: float) -> None:
        self._metadata = replace(self._metadata, confidence_threshold=threshold)


class FakeUserRepository:
    """In-memory user repository."""

    def __init__(self) -> None:
        self._by_email: dict[str, tuple[User, str]] = {}
        self._by_id: dict[int, User] = {}
        self._next_id = 1

    async def add(self, email: str, password_hash: str, role: Role) -> User:
        user = User(id=self._next_id, email=email, role=role, created_at=datetime.now(UTC))
        self._next_id += 1
        self._by_email[email] = (user, password_hash)
        self._by_id[user.id] = user
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        return self._by_id.get(user_id)

    async def find_credentials(self, email: str) -> Credentials | None:
        found = self._by_email.get(email)
        if found is None:
            return None
        user, password_hash = found
        return Credentials(user=user, password_hash=password_hash)

    async def email_exists(self, email: str) -> bool:
        return email in self._by_email


class FakeSessionRepository:
    """In-memory session journal."""

    def __init__(self) -> None:
        self._records: list[SessionRecord] = []
        self._next_id = 1

    def seed(self, record: SessionRecord) -> None:
        """Insert a record synchronously (test helper)."""
        self._records.append(record)

    async def add(self, record: NewSessionRecord) -> SessionRecord:
        stored = SessionRecord(
            id=self._next_id,
            user_id=record.user_id,
            kind=record.kind,
            source_name=record.source_name,
            sheep_count=record.sheep_count,
            mean_confidence=record.mean_confidence,
            model_version=record.model_version,
            created_at=datetime.now(UTC),
            details=record.details,
        )
        self._next_id += 1
        self._records.append(stored)
        return stored

    async def list_for_user(self, user_id: int, limit: int = 100) -> list[SessionRecord]:
        rows = [r for r in self._records if r.user_id == user_id]
        return list(reversed(rows))[:limit]
