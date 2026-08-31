from datetime import date, time

import pytest
from radio_pota_logging.domain.logging_session.entities import LoggingSession
from radio_pota_logging.domain.logging_session.exceptions import (
    FrequencyFormatError,
    FrequencyOutOfBandError,
)
from radio_pota_logging.domain.logging_session.value_objects import (
    QsoTimestamp,
    SessionStart,
    StationDefaults,
)


def _new_session() -> LoggingSession:
    return LoggingSession.start(StationDefaults(), QsoTimestamp(date(2026, 8, 30), time(9, 0)))


def test_start_seeds_defaults_and_empty_qso_list() -> None:
    session = _new_session()
    assert session.qsos == ()
    assert session.next_entry_defaults.operator == "SM6Y"
    assert session.next_entry_defaults.freq == ""


def test_start_seeds_my_sig_info_from_given_park_reference() -> None:
    session = LoggingSession.start(
        StationDefaults(), QsoTimestamp(date(2026, 8, 30), time(9, 0)), my_sig_info="K-1234"
    )
    assert session.next_entry_defaults.my_sig_info == "K-1234"


def test_start_seeds_freq_from_given_frequency() -> None:
    session = LoggingSession.start(
        StationDefaults(), QsoTimestamp(date(2026, 8, 30), time(9, 0)), freq="14.062"
    )
    assert session.next_entry_defaults.freq == "14.062"


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


def test_record_qso_normalizes_carried_forward_my_sig_info_to_uppercase() -> None:
    session = _new_session()
    session.record_qso(
        call="W1AW",
        qso_date=date(2026, 8, 30),
        time_on=time(12, 0),
        mode="CW",
        my_sig_info="k-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="14.062",
        operator="SM6Y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )
    assert session.next_entry_defaults.my_sig_info == "K-1234"


def test_record_qso_normalizes_carried_forward_operator_to_uppercase() -> None:
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
        operator="sm6y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )
    assert session.next_entry_defaults.operator == "SM6Y"


def test_record_qso_resets_rst_sent_and_rst_rcvd_instead_of_carrying_them_forward() -> None:
    session = _new_session()
    session.record_qso(
        call="W1AW",
        qso_date=date(2026, 8, 30),
        time_on=time(12, 0),
        mode="CW",
        my_sig_info="K-1234",
        rst_sent="579",
        rst_rcvd="588",
        freq="14.062",
        operator="SM6Y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )
    assert session.next_entry_defaults.rst_sent == "599"
    assert session.next_entry_defaults.rst_rcvd == "599"


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


def test_start_sets_session_start_from_qso_date_and_my_sig_info() -> None:
    session = LoggingSession.start(
        StationDefaults(), QsoTimestamp(date(2026, 8, 30), time(9, 0)), my_sig_info="k-1234"
    )
    assert session.session_start == SessionStart(qso_date=date(2026, 8, 30), my_sig_info="K-1234")


def test_record_qso_leaves_session_start_unchanged() -> None:
    session = _new_session()
    original_session_start = session.session_start
    session.record_qso(
        call="W1AW",
        qso_date=date(2026, 8, 30),
        time_on=time(23, 59),
        mode="CW",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="14.062",
        operator="SM6Y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )

    # TIME_ON + 2 minutes rolls next_entry_defaults' QSO_DATE to the next
    # day; session_start must not follow that rollover.
    assert session.next_entry_defaults.timestamp.qso_date == date(2026, 8, 31)
    assert session.session_start == original_session_start
    assert session.session_start.qso_date == date(2026, 8, 30)


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
