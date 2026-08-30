"""Outbound port for persisting the LoggingSession aggregate."""

from __future__ import annotations

from typing import Protocol

from .entities import LoggingSession


class LoggingSessionRepository(Protocol):
    def find_unfinished(self) -> LoggingSession | None:
        """Return the current session, if one has been started/resumed, else None."""
        ...

    def save(self, session: LoggingSession) -> None:
        """Persist the session after every submitted QSO."""
        ...

    def archive(self, session: LoggingSession) -> None:
        """Set aside the session's persisted data (without deleting it)."""
        ...
