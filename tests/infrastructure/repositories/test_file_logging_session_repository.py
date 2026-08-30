import json
import uuid
from datetime import date, time
from pathlib import Path

from radio_pota_logging.domain.logging_session.entities import LoggingSession
from radio_pota_logging.domain.logging_session.value_objects import QsoTimestamp, StationDefaults
from radio_pota_logging.infrastructure.repositories.file_logging_session_repository import (
    FileLoggingSessionRepository,
)


def test_find_unfinished_returns_none_when_no_file(tmp_path: Path) -> None:
    repository = FileLoggingSessionRepository(tmp_path)
    assert repository.find_unfinished() is None


def test_save_then_find_unfinished_round_trips(tmp_path: Path) -> None:
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
    repository = FileLoggingSessionRepository(tmp_path)
    repository.save(session)

    reloaded = repository.find_unfinished()

    assert reloaded is not None
    assert reloaded.session_id == session.session_id
    assert len(reloaded.qsos) == 1
    assert reloaded.qsos[0].call == "W1AW"
    assert reloaded.qsos[0].freq.megahertz == session.qsos[0].freq.megahertz
    assert reloaded.next_entry_defaults == session.next_entry_defaults


def test_archive_renames_file_without_deleting_data(tmp_path: Path) -> None:
    session = LoggingSession.start(StationDefaults(), QsoTimestamp(date(2026, 8, 30), time(9, 0)))
    repository = FileLoggingSessionRepository(tmp_path)
    repository.save(session)

    repository.archive(session)

    assert repository.find_unfinished() is None
    archived_files = list(tmp_path.glob(".qso_session.*.json"))
    assert len(archived_files) == 1
    assert archived_files[0].read_text() != ""


def test_find_unfinished_normalizes_a_legacy_lowercase_call(tmp_path: Path) -> None:
    legacy_session = {
        "session_id": str(uuid.uuid4()),
        "qsos": [
            {
                "call": "w1aw",
                "timestamp": {"qso_date": "2026-08-30", "time_on": "09:00:00"},
                "mode": "CW",
                "my_sig": "POTA",
                "my_sig_info": "K-1234",
                "rst_sent": "599",
                "rst_rcvd": "599",
                "freq": "14.062",
                "operator": "SM6Y",
                "my_rig": "Elecraft KX2",
                "tx_pwr": "5",
            }
        ],
        "next_entry_defaults": {
            "operator": "SM6Y",
            "mode": "CW",
            "my_sig_info": "K-1234",
            "rst_sent": "599",
            "rst_rcvd": "599",
            "freq": "14.062",
            "my_rig": "Elecraft KX2",
            "tx_pwr": "5",
            "timestamp": {"qso_date": "2026-08-30", "time_on": "09:02:00"},
        },
    }
    (tmp_path / ".qso_session.json").write_text(json.dumps(legacy_session))
    repository = FileLoggingSessionRepository(tmp_path)

    reloaded = repository.find_unfinished()

    assert reloaded is not None
    assert reloaded.qsos[0].call == "W1AW"


def test_find_unfinished_normalizes_a_legacy_lowercase_my_sig_info(tmp_path: Path) -> None:
    legacy_session = {
        "session_id": str(uuid.uuid4()),
        "qsos": [
            {
                "call": "W1AW",
                "timestamp": {"qso_date": "2026-08-30", "time_on": "09:00:00"},
                "mode": "CW",
                "my_sig": "POTA",
                "my_sig_info": "k-1234",
                "rst_sent": "599",
                "rst_rcvd": "599",
                "freq": "14.062",
                "operator": "SM6Y",
                "my_rig": "Elecraft KX2",
                "tx_pwr": "5",
            }
        ],
        "next_entry_defaults": {
            "operator": "SM6Y",
            "mode": "CW",
            "my_sig_info": "k-1234",
            "rst_sent": "599",
            "rst_rcvd": "599",
            "freq": "14.062",
            "my_rig": "Elecraft KX2",
            "tx_pwr": "5",
            "timestamp": {"qso_date": "2026-08-30", "time_on": "09:02:00"},
        },
    }
    (tmp_path / ".qso_session.json").write_text(json.dumps(legacy_session))
    repository = FileLoggingSessionRepository(tmp_path)

    reloaded = repository.find_unfinished()

    assert reloaded is not None
    assert reloaded.qsos[0].my_sig_info == "K-1234"
    assert reloaded.next_entry_defaults.my_sig_info == "K-1234"


def test_find_unfinished_normalizes_a_legacy_lowercase_operator(tmp_path: Path) -> None:
    legacy_session = {
        "session_id": str(uuid.uuid4()),
        "qsos": [
            {
                "call": "W1AW",
                "timestamp": {"qso_date": "2026-08-30", "time_on": "09:00:00"},
                "mode": "CW",
                "my_sig": "POTA",
                "my_sig_info": "K-1234",
                "rst_sent": "599",
                "rst_rcvd": "599",
                "freq": "14.062",
                "operator": "sm6y",
                "my_rig": "Elecraft KX2",
                "tx_pwr": "5",
            }
        ],
        "next_entry_defaults": {
            "operator": "sm6y",
            "mode": "CW",
            "my_sig_info": "K-1234",
            "rst_sent": "599",
            "rst_rcvd": "599",
            "freq": "14.062",
            "my_rig": "Elecraft KX2",
            "tx_pwr": "5",
            "timestamp": {"qso_date": "2026-08-30", "time_on": "09:02:00"},
        },
    }
    (tmp_path / ".qso_session.json").write_text(json.dumps(legacy_session))
    repository = FileLoggingSessionRepository(tmp_path)

    reloaded = repository.find_unfinished()

    assert reloaded is not None
    assert reloaded.qsos[0].operator == "SM6Y"
    assert reloaded.next_entry_defaults.operator == "SM6Y"


def test_archive_without_a_saved_session_is_a_no_op(tmp_path: Path) -> None:
    session = LoggingSession.start(StationDefaults(), QsoTimestamp(date(2026, 8, 30), time(9, 0)))
    repository = FileLoggingSessionRepository(tmp_path)

    repository.archive(session)

    assert list(tmp_path.iterdir()) == []
