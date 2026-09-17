"""Use cases for the session journal: record and list inference sessions."""

from __future__ import annotations

from agrovision.application.ports import SessionRepository
from agrovision.domain.report import NewSessionRecord, SessionRecord


class RecordSession:
    """Persists a session-journal entry."""

    def __init__(self, sessions: SessionRepository) -> None:
        self._sessions = sessions

    async def execute(self, record: NewSessionRecord) -> SessionRecord:
        """Persist and return a new session record."""
        return await self._sessions.add(record)


class ListSessions:
    """Lists recent session-journal entries for a user."""

    def __init__(self, sessions: SessionRepository) -> None:
        self._sessions = sessions

    async def execute(self, user_id: int, limit: int = 100) -> list[SessionRecord]:
        """Return recent session records for a user, newest first."""
        return await self._sessions.list_for_user(user_id, limit)
