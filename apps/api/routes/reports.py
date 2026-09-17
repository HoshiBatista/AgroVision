"""Session journal and report export endpoints (require authentication)."""

from __future__ import annotations

from fastapi import APIRouter, Response

from agrovision.infrastructure.reports import render_csv, render_pdf
from agrovision.presentation.presenters import session_to_schema
from agrovision.presentation.schemas import SessionRecordSchema
from apps.api.dependencies import CurrentUserDep, ListSessionsDep

router = APIRouter(prefix="/v1/reports", tags=["reports"])


@router.get("/sessions", response_model=list[SessionRecordSchema])
async def list_sessions(
    user: CurrentUserDep, use_case: ListSessionsDep
) -> list[SessionRecordSchema]:
    """Return the authenticated user's recent inference sessions."""
    records = await use_case.execute(user.id)
    return [session_to_schema(record) for record in records]


@router.get("/export.csv")
async def export_csv(user: CurrentUserDep, use_case: ListSessionsDep) -> Response:
    """Export the user's sessions as a CSV file."""
    records = await use_case.execute(user.id)
    return Response(
        content=render_csv(records),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=agrovision_sessions.csv"},
    )


@router.get("/export.pdf")
async def export_pdf(user: CurrentUserDep, use_case: ListSessionsDep) -> Response:
    """Export the user's sessions as a PDF file."""
    records = await use_case.execute(user.id)
    return Response(
        content=render_pdf(records),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=agrovision_sessions.pdf"},
    )
