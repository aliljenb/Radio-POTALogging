from datetime import date, time

import pytest
from radio_pota_logging.domain.logging_session.entities import LoggingSession
from radio_pota_logging.domain.logging_session.exceptions import (
    FrequencyFormatError,
    FrequencyOutOfBandError,
)
from radio_pota_logging.domain.logging_session.value_objects import QsoTimestamp, StationDefaults


def _new_session() -> LoggingSession:
    return LoggingSession.start(StationDefaults(), QsoTimestamp(date(2026, 8, 30), time(9, 0)))


def test_start_seeds_defaults_and_empty_qso_list() -> None:
    session = _new_session()
    assert session.qsos == ()
    assert session.next_entry_defaults.operator == "SM6Y"
    assert session.next_entry_defaults.freq == ""


def test_record_qso_sets_time_off_equal_to_time_on_and_fixed_my_sig() -> None:
    session = _new_session()
    qso = session.record_qso(
        call="W1AW",
        qso_date=date(2026, 8, 30),
        time_on=time(12, 0),
        mode="CW",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="14.062",
        operator="SM6Y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )
    assert qso.time_off == time(12, 0)
    assert qso.band.value == "20M"
    assert qso.my_sig == "POTA"


def test_record_qso_appends_and_is_append_only() -> None:
    session = _new_session()
    session.record_qso(
        call="W1AW",
        qso_date=date(2026, 8, 30),
        time_on=time(12, 0),
        mode="CW",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="14.062",
        operator="SM6Y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )
    session.record_qso(
        call="K1ABC",
        qso_date=date(2026, 8, 30),
        time_on=time(12, 2),
        mode="CW",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="14.062",
        operator="SM6Y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )
    assert [qso.call for qso in session.qsos] == ["W1AW", "K1ABC"]


def test_record_qso_carries_defaults_forward_except_call_and_advances_time_on() -> None:
    session = _new_session()
    session.record_qso(
        call="W1AW",
        qso_date=date(2026, 8, 30),
        time_on=time(12, 0),
        mode="CW",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="14.062",
        operator="SM6Y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )
    defaults = session.next_entry_defaults
    assert defaults.my_sig_info == "K-1234"
    assert defaults.freq == "14.062"
    assert defaults.timestamp == QsoTimestamp(date(2026, 8, 30), time(12, 2))


def test_record_qso_rejects_unparsable_frequency_and_leaves_state_unchanged() -> None:
    session = _new_session()
    with pytest.raises(FrequencyFormatError):
        session.record_qso(
            call="W1AW",
            qso_date=date(2026, 8, 30),
            time_on=time(12, 0),
            mode="CW",
            my_sig_info="K-1234",
            rst_sent="599",
            rst_rcvd="599",
            freq="not-a-number",
            operator="SM6Y",
            my_rig="Elecraft KX2",
            tx_pwr="5",
        )
    assert session.qsos == ()


def test_record_qso_rejects_out_of_band_frequency_and_leaves_state_unchanged() -> None:
    session = _new_session()
    with pytest.raises(FrequencyOutOfBandError):
        session.record_qso(
            call="W1AW",
            qso_date=date(2026, 8, 30),
            time_on=time(12, 0),
            mode="CW",
            my_sig_info="K-1234",
            rst_sent="599",
            rst_rcvd="599",
            freq="5.000",
            operator="SM6Y",
            my_rig="Elecraft KX2",
            tx_pwr="5",
        )
    assert session.qsos == ()
