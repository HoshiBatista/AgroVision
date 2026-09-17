"""Unit tests for report rendering and session use cases."""

from __future__ import annotations

from datetime import UTC, datetime

from agrovision.application.use_cases.reports import ListSessions, RecordSession
from agrovision.domain.report import NewSessionRecord, SessionKind, SessionRecord
from agrovision.infrastructure.reports import render_csv, render_pdf
from tests.fakes import FakeSessionRepository


def _record(record_id: int, count: int) -> SessionRecord:
    return SessionRecord(
        id=record_id,
        user_id=1,
        kind=SessionKind.IMAGE,
        source_name=f"frame-{record_id}.jpg",
        sheep_count=count,
        mean_confidence=0.87,
        model_version="test-v1",
        created_at=datetime(2026, 9, 12, 10, 30, tzinfo=UTC),
    )


def test_render_csv_has_header_and_rows() -> None:
    csv_bytes = render_csv([_record(1, 5), _record(2, 8)])
    text = csv_bytes.decode("utf-8")
    assert "ID,Date (UTC),Kind,Source,Sheep,Mean conf.,Model" in text
    assert "frame-1.jpg" in text
    assert text.count("\n") >= 3


def test_render_pdf_is_a_pdf() -> None:
    pdf_bytes = render_pdf([_record(1, 5)])
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 400


def test_render_reports_handle_empty() -> None:
    assert render_csv([]).decode("utf-8").startswith("ID,")
    assert render_pdf([]).startswith(b"%PDF")


async def test_record_and_list_sessions() -> None:
    repo = FakeSessionRepository()
    await RecordSession(repo).execute(
        NewSessionRecord(
            user_id=1,
            kind=SessionKind.VIDEO,
            source_name="clip.mp4",
            sheep_count=12,
            mean_confidence=0.0,
            model_version="test-v1",
        )
    )
    records = await ListSessions(repo).execute(user_id=1)
    assert len(records) == 1
    assert records[0].sheep_count == 12
