from datetime import date, time

from radio_pota_logging.application.logging_session.queries import CheckForResumableSessionQuery
from radio_pota_logging.domain.logging_session.entities import LoggingSession
from radio_pota_logging.domain.logging_session.value_objects import QsoTimestamp, StationDefaults


class FakeRepository:
    def __init__(self, session: LoggingSession | None = None) -> None:
        self.session = session

    def find_unfinished(self) -> LoggingSession | None:
        return self.session

    def save(self, session: LoggingSession) -> None:
        self.session = session

    def archive(self, session: LoggingSession) -> None:
        pass


def test_returns_false_when_no_session_exists() -> None:
    assert CheckForResumableSessionQuery(FakeRepository()).execute() is False


def test_returns_true_when_a_session_exists() -> None:
    session = LoggingSession.start(StationDefaults(), QsoTimestamp(date(2026, 8, 30), time(9, 0)))
    assert CheckForResumableSessionQuery(FakeRepository(session)).execute() is True
