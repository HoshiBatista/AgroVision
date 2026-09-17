"""Contract tests for health, readiness, model-info, and photo inference."""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np
import pytest
from fastapi.testclient import TestClient

from agrovision.infrastructure.imaging import encode_jpeg
from apps.api.main import create_app
from tests.fakes import FakeDetector


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app(detector=FakeDetector())
    with TestClient(app) as test_client:
        yield test_client


def _jpeg_bytes() -> bytes:
    return encode_jpeg(np.full((90, 120, 3), 100, dtype=np.uint8), quality=90)


def test_health_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["X-Request-ID"]


def test_ready_reports_model_loaded(client: TestClient) -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["ready"] is True
    assert body["model_loaded"] is True


def test_model_info(client: TestClient) -> None:
    response = client.get("/v1/model-info")
    assert response.status_code == 200
    body = response.json()
    assert body["classes"] == ["sheep"]
    assert body["limitations"]


def test_predict_image_counts_sheep(client: TestClient) -> None:
    response = client.post(
        "/v1/predictions",
        files={"file": ("frame.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["uncertain_count"] == 1
    assert body["annotated_image"].startswith("data:image/jpeg;base64,")
    assert len(body["detections"]) == 2


def test_predict_rejects_non_image(client: TestClient) -> None:
    response = client.post(
        "/v1/predictions",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "unsupported_media_type"
