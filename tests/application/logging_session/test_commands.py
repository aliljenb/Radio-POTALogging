from collections.abc import Sequence
from datetime import date, time
from pathlib import Path

import pytest
from radio_pota_logging.application.logging_session.commands import (
    GenerateAdifCommand,
    ResumeSessionCommand,
    StartNewSessionCommand,
    SubmitQsoCommand,
)
from radio_pota_logging.application.logging_session.dto import SubmitQsoRequest
from radio_pota_logging.domain.logging_session.entities import LoggingSession
from radio_pota_logging.domain.logging_session.exceptions import FrequencyOutOfBandError
from radio_pota_logging.domain.logging_session.value_objects import (
    Qso,
    QsoTimestamp,
    StationDefaults,
)


class FakeRepository:
    def __init__(self, session: LoggingSession | None = None) -> None:
        self.session = session
        self.archived: list[LoggingSession] = []
        self.saved: list[LoggingSession] = []

    def find_unfinished(self) -> LoggingSession | None:
        return self.session

    def save(self, session: LoggingSession) -> None:
        self.session = session
        self.saved.append(session)

    def archive(self, session: LoggingSession) -> None:
        self.archived.append(session)


class FakeExporter:
    def __init__(self, text: str = "ADIF-TEXT") -> None:
        self.text = text
        self.exported_qsos: list[Qso] = []

    def export(self, qsos: Sequence[Qso]) -> str:
        self.exported_qsos = list(qsos)
        return self.text


def _submit_request(**overrides: object) -> SubmitQsoRequest:
    fields: dict[str, object] = {
        "call": "W1AW",
        "qso_date": date(2026, 8, 30),
        "time_on": time(9, 0),
        "mode": "CW",
        "my_sig_info": "K-1234",
        "rst_sent": "599",
        "rst_rcvd": "599",
        "freq": "14.062",
        "operator": "SM6Y",
        "my_rig": "Elecraft KX2",
        "tx_pwr": "5",
    }
    fields.update(overrides)
    return SubmitQsoRequest(**fields)  # type: ignore[arg-type]


def test_start_new_session_seeds_defaults_and_saves() -> None:
    repository = FakeRepository()
    result = StartNewSessionCommand(repository).execute(
        qso_date=date(2026, 8, 30), time_on=time(9, 0)
    )
    assert result.entry_defaults.operator == "SM6Y"
    assert result.qsos == ()
    assert repository.session is not None


def test_start_new_session_archives_existing_unfinished_session() -> None:
    existing = LoggingSession.start(StationDefaults(), QsoTimestamp(date(2026, 8, 29), time(9, 0)))
    repository = FakeRepository(existing)
    StartNewSessionCommand(repository).execute(qso_date=date(2026, 8, 30), time_on=time(9, 0))
    assert repository.archived == [existing]


def test_resume_session_returns_existing_state() -> None:
    session = LoggingSession.start(StationDefaults(), QsoTimestamp(date(2026, 8, 30), time(9, 0)))
    session.record_qso(
        call="W1AW",
        qso_date=date(2026, 8, 30),
        time_on=time(9, 0),
        mode="CW",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="14.062",
        operator="SM6Y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )
    result = ResumeSessionCommand(FakeRepository(session)).execute()
    assert len(result.qsos) == 1
    assert result.qsos[0].call == "W1AW"


def test_submit_qso_saves_and_returns_next_defaults() -> None:
    session = LoggingSession.start(StationDefaults(), QsoTimestamp(date(2026, 8, 30), time(9, 0)))
    repository = FakeRepository(session)
    result = SubmitQsoCommand(repository).execute(_submit_request())
    assert result.submitted.call == "W1AW"
    assert result.entry_defaults.time_on == time(9, 2)
    assert repository.saved[-1] is session


def test_submit_qso_propagates_domain_validation_errors() -> None:
    session = LoggingSession.start(StationDefaults(), QsoTimestamp(date(2026, 8, 30), time(9, 0)))
    repository = FakeRepository(session)
    with pytest.raises(FrequencyOutOfBandError):
        SubmitQsoCommand(repository).execute(_submit_request(freq="5.000"))


def test_generate_adif_writes_exported_text_and_counts_qsos(tmp_path: Path) -> None:
    session = LoggingSession.start(StationDefaults(), QsoTimestamp(date(2026, 8, 30), time(9, 0)))
    session.record_qso(
        call="W1AW",
        qso_date=date(2026, 8, 30),
        time_on=time(9, 0),
        mode="CW",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="14.062",
        operator="SM6Y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )
    repository = FakeRepository(session)
    exporter = FakeExporter("ADIF-TEXT")
    destination = tmp_path / "out.adi"

    result = GenerateAdifCommand(repository, exporter).execute(destination)

    assert destination.read_text() == "ADIF-TEXT"
    assert result.qso_count == 1
    assert result.path == destination
    assert len(exporter.exported_qsos) == 1
