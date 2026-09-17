"""Ports (Protocols) that the application depends on; adapters live in infrastructure."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol, runtime_checkable

import numpy as np
from numpy.typing import NDArray

from agrovision.application.dto import Credentials, TokenPayload, VideoAnalysis
from agrovision.domain.counting import FrameResult
from agrovision.domain.model import ModelMetadata
from agrovision.domain.report import NewSessionRecord, SessionRecord
from agrovision.domain.stream import StreamMetrics, StreamSource
from agrovision.domain.user import Role, User

Image = NDArray[np.uint8]


@runtime_checkable
class DetectorPort(Protocol):
    """A loaded object detector that runs inference on BGR image arrays."""

    @property
    def metadata(self) -> ModelMetadata:
        """Descriptive metadata about the loaded model."""
        ...

    def detect(self, image: Image) -> FrameResult:
        """Run detection on a single BGR image and return the frame result."""
        ...


class VideoAnalyzerPort(Protocol):
    """Analyse a video file frame by frame, writing an annotated output."""

    @property
    def metadata(self) -> ModelMetadata:
        """Descriptive metadata about the underlying model."""
        ...

    def analyze(self, input_path: Path, output_path: Path) -> VideoAnalysis:
        """Analyse ``input_path`` and write an annotated video to ``output_path``."""
        ...


class PasswordHasher(Protocol):
    """Hashing and verification of user passwords."""

    def hash(self, password: str) -> str:
        """Return a salted hash for the given plaintext password."""
        ...

    def verify(self, password: str, password_hash: str) -> bool:
        """Return whether the plaintext password matches the stored hash."""
        ...


class TokenService(Protocol):
    """Issue and decode signed authentication tokens."""

    def create_access_token(self, user: User) -> str:
        """Create a signed short-lived access token for the user."""
        ...

    def create_refresh_token(self, user: User) -> str:
        """Create a signed long-lived refresh token for the user."""
        ...

    def decode(self, token: str) -> TokenPayload:
        """Decode and validate a token, raising on failure."""
        ...


class UserRepository(Protocol):
    """Persistence for user identities and credentials."""

    async def add(self, email: str, password_hash: str, role: Role) -> User:
        """Create and return a new user."""
        ...

    async def get_by_id(self, user_id: int) -> User | None:
        """Return the user with the given id, or None."""
        ...

    async def find_credentials(self, email: str) -> Credentials | None:
        """Return the user's identity and password hash by email, or None."""
        ...

    async def email_exists(self, email: str) -> bool:
        """Return whether a user with the given email already exists."""
        ...


class SessionRepository(Protocol):
    """Persistence for the inference session journal."""

    async def add(self, record: NewSessionRecord) -> SessionRecord:
        """Persist and return a new session record."""
        ...

    async def list_for_user(self, user_id: int, limit: int = 100) -> list[SessionRecord]:
        """Return recent session records for a user, newest first."""
        ...


class StreamSourcePort(Protocol):
    """A frame source for a drone feed (file, RTSP, ...)."""

    @property
    def source(self) -> StreamSource:
        """The stream configuration this source reads from."""
        ...

    def frames(self) -> Iterator[Image]:
        """Yield BGR frames, looping the underlying source indefinitely."""
        ...


class FrameBusPort(Protocol):
    """In-memory bus holding the latest annotated frame and metrics per stream."""

    def publish(self, stream_id: str, jpeg: bytes, metrics: StreamMetrics) -> None:
        """Publish the latest annotated JPEG and metrics for a stream."""
        ...

    def update_metrics(self, metrics: StreamMetrics) -> None:
        """Publish metrics only (e.g. a status change) without a new frame."""
        ...

    def latest_jpeg(self, stream_id: str) -> bytes | None:
        """Return the latest annotated JPEG for a stream, or None."""
        ...

    def metrics(self) -> list[StreamMetrics]:
        """Return the latest metrics for all known streams."""
        ...
