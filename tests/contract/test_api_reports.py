"""Contract tests for the session journal and report exports (fakes, no DB)."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from agrovision.domain.report import SessionKind, SessionRecord
from agrovision.domain.user import Role, User
from apps.api.dependencies import get_current_user, get_session_repository
from apps.api.main import create_app
from tests.fakes import FakeDetector, FakeSessionRepository


@pytest.fixture
def sessions() -> FakeSessionRepository:
    repo = FakeSessionRepository()
    repo.seed(
        SessionRecord(
            id=1,
            user_id=1,
            kind=SessionKind.IMAGE,
            source_name="frame.jpg",
            sheep_count=7,
            mean_confidence=0.9,
            model_version="test-v1",
            created_at=datetime(2026, 9, 12, 10, 0, tzinfo=UTC),
        )
    )
    return repo


@pytest.fixture
def client(sessions: FakeSessionRepository) -> Iterator[TestClient]:
    app = create_app(detector=FakeDetector())
    user = User(id=1, email="a@b.com", role=Role.OPERATOR, created_at=datetime.now(UTC))
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_session_repository] = lambda: sessions
    with TestClient(app) as test_client:
        yield test_client


def test_list_sessions(client: TestClient) -> None:
    response = client.get("/v1/reports/sessions")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["source_name"] == "frame.jpg"
    assert body[0]["sheep_count"] == 7


def test_sessions_require_auth() -> None:
    app = create_app(detector=FakeDetector())
    with TestClient(app) as anonymous:
        assert anonymous.get("/v1/reports/sessions").status_code == 401


def test_export_csv(client: TestClient) -> None:
    response = client.get("/v1/reports/export.csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.text.startswith("ID,")


def test_export_pdf(client: TestClient) -> None:
    response = client.get("/v1/reports/export.pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
