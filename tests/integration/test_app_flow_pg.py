"""Full authenticated app flow against real Postgres (register → journal → report).

Skipped automatically when the Postgres test database is unreachable.
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import Iterator
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from agrovision.config import Settings
from agrovision.infrastructure.imaging import encode_jpeg
from agrovision.infrastructure.streaming.manager import StreamManager
from apps.api.main import create_app
from tests.fakes import FakeDetector
from tests.integration.conftest import TEST_DATABASE_URL, _reset_schema


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    if not asyncio.run(_reset_schema()):
        pytest.skip("Postgres test database not reachable")
    settings = Settings(
        database_url=TEST_DATABASE_URL,
        storage_root=tmp_path / "storage",
        jwt_secret="integration-test-secret-00000000000000",
    )
    empty_manager = StreamManager([], FakeDetector(), settings)
    app = create_app(settings, detector=FakeDetector(), stream_manager=empty_manager)
    with TestClient(app) as test_client:
        yield test_client


def _jpeg() -> bytes:
    return encode_jpeg(np.full((80, 100, 3), 120, dtype=np.uint8), quality=90)


def test_full_authenticated_flow_persists_to_postgres(client: TestClient) -> None:
    email = f"user_{uuid.uuid4().hex}@farm.com"

    register = client.post("/v1/auth/register", json={"email": email, "password": "password123"})
    assert register.status_code == 201
    access = register.json()["access_token"]
    auth = {"Authorization": f"Bearer {access}"}

    me = client.get("/v1/auth/me", headers=auth)
    assert me.status_code == 200
    assert me.json()["email"] == email

    # Predict with the token -> a session must be journaled to Postgres.
    prediction = client.post(
        "/v1/predictions", headers=auth, files={"file": ("frame.jpg", _jpeg(), "image/jpeg")}
    )
    assert prediction.status_code == 200
    assert prediction.json()["count"] == 1
    assert prediction.json()["uncertain_count"] == 1

    sessions = client.get("/v1/reports/sessions", headers=auth)
    assert sessions.status_code == 200
    body = sessions.json()
    assert len(body) == 1
    assert body[0]["kind"] == "image"
    assert body[0]["sheep_count"] == 1

    csv_export = client.get("/v1/reports/export.csv", headers=auth)
    assert csv_export.status_code == 200
    assert "frame.jpg" in csv_export.text

    pdf_export = client.get("/v1/reports/export.pdf", headers=auth)
    assert pdf_export.status_code == 200
    assert pdf_export.content.startswith(b"%PDF")


def test_login_and_refresh_against_postgres(client: TestClient) -> None:
    email = f"user_{uuid.uuid4().hex}@farm.com"
    client.post("/v1/auth/register", json={"email": email, "password": "password123"})

    login = client.post("/v1/auth/login", json={"email": email, "password": "password123"})
    assert login.status_code == 200
    refresh_token = login.json()["refresh_token"]

    refreshed = client.post("/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]

    bad = client.post("/v1/auth/login", json={"email": email, "password": "wrong-password"})
    assert bad.status_code == 401
