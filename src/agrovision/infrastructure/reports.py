"""Render session-journal records to CSV and PDF (reportlab)."""

from __future__ import annotations

import csv
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from agrovision.domain.report import SessionRecord

_HEADERS = ("ID", "Date (UTC)", "Kind", "Source", "Sheep", "Mean conf.", "Model")


def _row(record: SessionRecord) -> tuple[str, ...]:
    return (
        str(record.id),
        record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        str(record.kind),
        record.source_name,
        str(record.sheep_count),
        f"{record.mean_confidence:.2f}",
        record.model_version,
    )


def render_csv(records: list[SessionRecord]) -> bytes:
    """Render session records as UTF-8 CSV bytes."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(_HEADERS)
    writer.writerows(_row(record) for record in records)
    return buffer.getvalue().encode("utf-8")


def render_pdf(records: list[SessionRecord]) -> bytes:
    """Render session records as a simple tabular PDF."""
    buffer = io.BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, title="AgroVision session report")
    data = [list(_HEADERS)] + [list(_row(record)) for record in records]
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f6f43")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f7f4")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm / 4),
            ]
        )
    )
    document.build([table])
    return buffer.getvalue()
