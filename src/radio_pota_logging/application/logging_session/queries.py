"""Read use cases for the QSO Logging feature."""

from __future__ import annotations

from dataclasses import dataclass

from radio_pota_logging.domain.logging_session.repository import LoggingSessionRepository


@dataclass(frozen=True)
class CheckForResumableSessionQuery:
    """Whether a previously started session exists, to decide if the startup prompt is shown."""

    repository: LoggingSessionRepository

    def execute(self) -> bool:
        return self.repository.find_unfinished() is not None
