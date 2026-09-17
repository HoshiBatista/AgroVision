"""Contract tests for stream listing and the dashboard (seeded manager, no threads)."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from agrovision.config import Settings
from agrovision.domain.stream import StreamMetrics, StreamSource, StreamStatus
from agrovision.domain.user import Role, User
from agrovision.infrastructure.streaming.manager import StreamManager
from apps.api.dependencies import get_current_user
from apps.api.main import create_app
from tests.fakes import FakeDetector


@pytest.fixture
def client() -> Iterator[TestClient]:
    settings = Settings()
    sources = [
        StreamSource("north-pasture", "North Pasture", "Sector A", "data/demo/north.mp4"),
        StreamSource("south-field", "South Field", "Sector B", "data/demo/south.mp4"),
    ]
    manager = StreamManager(sources, FakeDetector(), settings)
    # Seed metrics without starting worker threads for a deterministic test.
    manager.bus.publish(
        "north-pasture",
        b"jpeg",
        StreamMetrics("north-pasture", StreamStatus.RUNNING, 5, 0.9, 4.0, 1),
    )
    manager.bus.publish(
        "south-field",
        b"jpeg",
        StreamMetrics("south-field", StreamStatus.RUNNING, 3, 0.8, 6.0, 1),
    )
    app = create_app(settings, detector=FakeDetector(), stream_manager=manager)
    app.dependency_overrides[get_current_user] = lambda: User(
        id=1,
        email="operator@example.test",
        role=Role.ADMIN,
        created_at=datetime.now(UTC),
    )
    with TestClient(app) as test_client:
        yield test_client


def test_list_streams(client: TestClient) -> None:
    response = client.get("/v1/streams")
    assert response.status_code == 200
    ids = {stream["id"] for stream in response.json()}
    assert ids == {"north-pasture", "south-field"}


def test_dashboard_snapshot_aggregates(client: TestClient) -> None:
    response = client.get("/v1/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert body["total_sheep"] == 8
    assert body["active_streams"] == 2
    assert len(body["streams"]) == 2


def test_mjpeg_unknown_stream_404(client: TestClient) -> None:
    response = client.get("/v1/streams/does-not-exist/mjpeg")
    assert response.status_code == 404


def test_dashboard_websocket_pushes_snapshot(client: TestClient) -> None:
    with client.websocket_connect("/v1/dashboard/ws") as ws:
        message = ws.receive_json()
    assert message["total_sheep"] == 8
    assert message["active_streams"] == 2


def test_connect_and_disconnect_rtsp_stream(client: TestClient) -> None:
    response = client.post(
        "/v1/streams",
        json={
            "name": "Камера пастбища",
            "location": "Сектор В",
            "uri": "rtsp://camera.local/live",
        },
    )
    assert response.status_code == 201
    stream = response.json()
    assert stream["kind"] == "rtsp"
    assert "uri" not in stream
    assert client.delete(f"/v1/streams/{stream['id']}").status_code == 204


def test_update_model_threshold(client: TestClient) -> None:
    response = client.patch("/v1/model-threshold", json={"confidence_threshold": 0.55})
    assert response.status_code == 200
    assert response.json()["confidence_threshold"] == 0.55
