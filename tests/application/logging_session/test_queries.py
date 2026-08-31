from datetime import date, time

import pytest
from radio_pota_logging.application.logging_session.queries import (
    CheckForResumableSessionQuery,
    SuggestAdifFilenameQuery,
)
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


def test_suggest_adif_filename_uses_session_start_date_and_park_reference() -> None:
    session = LoggingSession.start(
        StationDefaults(), QsoTimestamp(date(2026, 8, 31), time(9, 0)), my_sig_info="k-1234"
    )
    assert SuggestAdifFilenameQuery(FakeRepository(session)).execute() == "20260831-K-1234.adi"


def test_suggest_adif_filename_raises_when_no_current_session() -> None:
    with pytest.raises(RuntimeError):
        SuggestAdifFilenameQuery(FakeRepository()).execute()
