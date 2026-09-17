"""Best-effort session journaling for authenticated inference calls."""

from __future__ import annotations

import logging

from fastapi import Request

from agrovision.application.use_cases.reports import RecordSession
from agrovision.domain.report import NewSessionRecord
from agrovision.infrastructure.db.repositories import SqlAlchemySessionRepository

logger = logging.getLogger("agrovision.api")


async def record_session(request: Request, record: NewSessionRecord) -> None:
    """Persist a journal entry, logging (not raising) on failure.

    Journaling must never break an otherwise-successful prediction, so database
    errors are swallowed after logging.
    """
    factory = request.app.state.session_factory
    try:
        async with factory() as session:
            await RecordSession(SqlAlchemySessionRepository(session)).execute(record)
            await session.commit()
    except Exception:  # noqa: BLE001 - journaling is best-effort
        logger.warning("Failed to journal session for source %s", record.source_name)
