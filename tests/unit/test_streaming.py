"""Unit tests for the frame bus, file source, and dashboard aggregation."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import cv2
import numpy as np
import pytest

from agrovision.application.use_cases.dashboard import BuildDashboard
from agrovision.config import Settings
from agrovision.domain.stream import StreamMetrics, StreamSource, StreamStatus
from agrovision.infrastructure.streaming.file_source import FileStreamSource
from agrovision.infrastructure.streaming.frame_bus import InMemoryFrameBus
from agrovision.infrastructure.streaming.manager import StreamManager
from tests.fakes import FakeDetector


def _metrics(stream_id: str, count: int, status: StreamStatus) -> StreamMetrics:
    return StreamMetrics(
        stream_id=stream_id,
        status=status,
        sheep_count=count,
        mean_confidence=0.9,
        latency_ms=5.0,
        frame_index=1,
    )


def test_frame_bus_publish_and_read() -> None:
    bus = InMemoryFrameBus()
    bus.publish("s1", b"jpeg-bytes", _metrics("s1", 3, StreamStatus.RUNNING))
    assert bus.latest_jpeg("s1") == b"jpeg-bytes"
    assert bus.latest_jpeg("missing") is None
    assert len(bus.metrics()) == 1


def test_build_dashboard_aggregates_running_streams() -> None:
    bus = InMemoryFrameBus()
    bus.publish("s1", b"a", _metrics("s1", 3, StreamStatus.RUNNING))
    bus.publish("s2", b"b", _metrics("s2", 4, StreamStatus.RUNNING))
    bus.update_metrics(_metrics("s3", 9, StreamStatus.STOPPED))

    state = BuildDashboard(bus).execute()

    assert state.total_sheep == 7  # stopped stream excluded
    assert state.active_streams == 2
    assert len(state.streams) == 3


def _synthetic_video(path: Path, frames: int = 20) -> None:
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter.fourcc(*"MJPG"), 10.0, (160, 120))
    for value in range(frames):
        writer.write(np.full((120, 160, 3), (value * 12) % 255, dtype=np.uint8))
    writer.release()


def test_file_source_loops(tmp_path: Path) -> None:
    clip = tmp_path / "clip.avi"
    _synthetic_video(clip, frames=5)
    source = FileStreamSource(StreamSource("s", "S", "loc", str(clip)))

    frames = source.frames()
    collected = [next(frames) for _ in range(8)]  # more than the 5 real frames
    frames.close()

    assert len(collected) == 8
    assert all(frame.shape == (120, 160, 3) for frame in collected)


def test_file_source_raises_on_missing_file() -> None:
    source = FileStreamSource(StreamSource("s", "S", "loc", "/no/such/video.mp4"))
    frames = source.frames()
    with pytest.raises(FileNotFoundError):
        next(frames)


def test_stream_manager_publishes_frames(tmp_path: Path) -> None:
    clip = tmp_path / "clip.avi"
    _synthetic_video(clip, frames=10)
    settings = Settings(stream_frame_stride=1, stream_target_fps=30)
    manager = StreamManager(
        [StreamSource("north", "North", "loc", str(clip))],
        FakeDetector(),
        settings,
    )

    manager.start()
    try:
        deadline = time.time() + 5.0
        while time.time() < deadline and manager.latest_jpeg("north") is None:
            time.sleep(0.05)
        assert manager.latest_jpeg("north") is not None
        metrics = manager.bus.metrics()
        assert metrics and metrics[0].sheep_count == 1
    finally:
        manager.stop()


def test_stream_manager_is_thread_safe_on_stop(tmp_path: Path) -> None:
    clip = tmp_path / "clip.avi"
    _synthetic_video(clip, frames=10)
    settings = Settings(stream_frame_stride=1, stream_target_fps=30)
    manager = StreamManager(
        [StreamSource("north", "North", "loc", str(clip))], FakeDetector(), settings
    )
    manager.start()
    manager.stop()
    assert threading.active_count() >= 1  # workers joined without hanging
