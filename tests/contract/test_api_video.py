"""Contract test for the video inference endpoint (fake detector, real OpenCV)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from agrovision.config import Settings
from apps.api.main import create_app
from tests.fakes import FakeDetector


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    settings = Settings(storage_root=tmp_path / "storage", stream_frame_stride=1)
    app = create_app(settings, detector=FakeDetector())
    with TestClient(app) as test_client:
        yield test_client


def _synthetic_video(path: Path, frames: int = 12) -> None:
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (160, 120))
    for value in range(frames):
        frame = np.full((120, 160, 3), (value * 10) % 255, dtype=np.uint8)
        writer.write(frame)
    writer.release()


def test_predict_video_returns_counts(client: TestClient, tmp_path: Path) -> None:
    clip = tmp_path / "clip.avi"
    _synthetic_video(clip)

    response = client.post(
        "/v1/predictions/video",
        files={"file": ("clip.mp4", clip.read_bytes(), "video/mp4")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["frames_processed"] > 0
    assert body["max_count"] == 1  # one detection is above the operational threshold
    assert body["annotated_video_url"].startswith("/media/")
    assert body["keyframes"]
    assert body["keyframes"][0].startswith("data:image/jpeg;base64,")


def test_predict_video_rejects_image(client: TestClient) -> None:
    response = client.post(
        "/v1/predictions/video",
        files={"file": ("photo.jpg", b"not-a-video", "image/jpeg")},
    )
    assert response.status_code == 415
