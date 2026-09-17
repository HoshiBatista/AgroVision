"""Drone stream domain model."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class StreamStatus(StrEnum):
    """Runtime status of a drone stream."""

    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class StreamSource:
    """Configuration for a single drone video feed.

    ``uri`` points at a local video file or an authenticated RTSP camera.
    """

    id: str
    name: str
    location: str
    uri: str
    kind: str = "file"


@dataclass(frozen=True, slots=True)
class StreamMetrics:
    """Latest metrics published for a running stream."""

    stream_id: str
    status: StreamStatus
    sheep_count: int
    mean_confidence: float
    latency_ms: float
    frame_index: int
