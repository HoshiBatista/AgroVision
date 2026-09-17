"""Contract tests for upload validation and limits (size, pixels, decoding)."""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np
import pytest
from fastapi.testclient import TestClient

from agrovision.config import Settings
from agrovision.infrastructure.imaging import encode_jpeg
from agrovision.infrastructure.streaming.manager import StreamManager
from apps.api.main import create_app
from tests.fakes import FakeDetector


def _make_client(**overrides: object) -> TestClient:
    settings = Settings(**overrides)
    manager = StreamManager([], FakeDetector(), settings)
    return TestClient(create_app(settings, detector=FakeDetector(), stream_manager=manager))


@pytest.fixture
def small_limit_client(tmp_path_factory: pytest.TempPathFactory) -> Iterator[TestClient]:
    root = tmp_path_factory.mktemp("storage")
    with _make_client(max_upload_mb=1, storage_root=root) as client:
        yield client


@pytest.fixture
def small_pixel_client(tmp_path_factory: pytest.TempPathFactory) -> Iterator[TestClient]:
    root = tmp_path_factory.mktemp("storage")
    with _make_client(max_image_pixels=100, storage_root=root) as client:
        yield client


def _jpeg() -> bytes:
    return encode_jpeg(np.full((80, 100, 3), 120, dtype=np.uint8), quality=90)


def test_oversized_upload_rejected(small_limit_client: TestClient) -> None:
    oversized = b"\xff\xd8" + b"0" * (2 * 1024 * 1024)  # ~2 MB, limit is 1 MB
    response = small_limit_client.post(
        "/v1/predictions", files={"file": ("big.jpg", oversized, "image/jpeg")}
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "payload_too_large"


def test_empty_upload_rejected(small_limit_client: TestClient) -> None:
    response = small_limit_client.post(
        "/v1/predictions", files={"file": ("empty.jpg", b"", "image/jpeg")}
    )
    assert response.status_code == 415


def test_undecodable_image_rejected(small_limit_client: TestClient) -> None:
    response = small_limit_client.post(
        "/v1/predictions", files={"file": ("broken.jpg", b"\xff\xd8not-a-jpeg", "image/jpeg")}
    )
    assert response.status_code == 415


def test_pixel_limit_rejected(small_pixel_client: TestClient) -> None:
    response = small_pixel_client.post(
        "/v1/predictions", files={"file": ("frame.jpg", _jpeg(), "image/jpeg")}
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "validation_error"
