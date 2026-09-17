"""Unit tests for domain value objects."""

from __future__ import annotations

import pytest

from agrovision.domain.counting import CountSample, FrameResult, VideoCountSummary
from agrovision.domain.detection import BoundingBox, Detection


def test_bounding_box_geometry() -> None:
    box = BoundingBox(10, 20, 40, 60)
    assert box.width == 30
    assert box.height == 40
    assert box.area == 1200
    assert box.center == (25, 40)


def test_bounding_box_rejects_inverted_coordinates() -> None:
    with pytest.raises(ValueError):
        BoundingBox(40, 10, 10, 40)


def test_detection_confidence_bounds() -> None:
    with pytest.raises(ValueError):
        Detection("sheep", 1.5, BoundingBox(0, 0, 1, 1))


def test_frame_result_counts_and_confidence() -> None:
    frame = FrameResult(
        detections=(
            Detection("sheep", 0.9, BoundingBox(0, 0, 1, 1)),
            Detection("sheep", 0.1, BoundingBox(1, 1, 2, 2)),
        ),
        width=100,
        height=100,
    )
    assert frame.count == 2
    assert frame.mean_confidence == pytest.approx(0.5)
    assert len(frame.uncertain(0.25)) == 1
    assert frame.count_above(0.25) == 1


def test_video_count_summary_from_samples() -> None:
    samples = [
        CountSample(timestamp_s=0.0, frame_index=0, count=2),
        CountSample(timestamp_s=1.0, frame_index=30, count=5),
        CountSample(timestamp_s=2.0, frame_index=60, count=3),
    ]
    summary = VideoCountSummary.from_samples(samples)
    assert summary.frames_processed == 3
    assert summary.max_count == 5
    assert summary.peak_timestamp_s == 1.0
    assert summary.mean_count == pytest.approx(10 / 3)


def test_video_count_summary_empty() -> None:
    summary = VideoCountSummary.from_samples([])
    assert summary.frames_processed == 0
    assert summary.max_count == 0
