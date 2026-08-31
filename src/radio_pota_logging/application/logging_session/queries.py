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


@dataclass(frozen=True)
class SuggestAdifFilenameQuery:
    """A default filename for the current session's ADIF export."""

    repository: LoggingSessionRepository

    def execute(self) -> str:
        session = self.repository.find_unfinished()
        if session is None:
            raise RuntimeError(
                "No current logging session; call StartNewSessionCommand or ResumeSessionCommand first"
            )
        start = session.session_start
        return f"{start.qso_date:%Y%m%d}-{start.my_sig_info}.adi"
