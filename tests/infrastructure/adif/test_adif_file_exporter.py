from datetime import date, time

from radio_pota_logging.domain.logging_session.entities import LoggingSession
from radio_pota_logging.domain.logging_session.value_objects import QsoTimestamp
from radio_pota_logging.infrastructure.adif.adif_file_exporter import AdifFileExporter

_STATION_KWARGS = {"operator": "SM6Y", "mode": "CW", "my_rig": "Elecraft KX2", "tx_pwr": "5"}


def test_export_produces_header_and_one_record_per_qso() -> None:
    session = LoggingSession.start(QsoTimestamp(date(2026, 8, 30), time(9, 0)), **_STATION_KWARGS)
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
    session.record_qso(
        call="K1ABC",
        qso_date=date(2026, 8, 30),
        time_on=time(9, 2),
        mode="CW",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="50.000",
        operator="SM6Y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )

    text = AdifFileExporter().export(session.qsos)

    assert "<EOH>" in text
    assert text.count("<EOR>") == 2
    assert "<CALL:4>W1AW" in text
    assert "<QSO_DATE:8>20260830" in text
    assert "<TIME_ON:6>090000" in text
    assert "<TIME_OFF:6>090000" in text
    assert "<BAND:3>20M" in text
    assert "<BAND:2>6M" in text
    assert "<MY_SIG:4>POTA" in text
    assert "<MY_SIG_INFO:6>K-1234" in text
    assert "<OPERATOR:4>SM6Y" in text
    assert "<MY_RIG:12>Elecraft KX2" in text
    assert "<TX_PWR:1>5" in text


def test_export_empty_session_has_header_but_no_records() -> None:
    text = AdifFileExporter().export(())
    assert "<EOH>" in text
    assert "<EOR>" not in text


def test_export_writes_zero_seconds_for_a_qso_built_from_nonzero_seconds_input() -> None:
    session = LoggingSession.start(QsoTimestamp(date(2026, 8, 30), time(9, 0)), **_STATION_KWARGS)
    session.record_qso(
        call="W1AW",
        qso_date=date(2026, 8, 30),
        time_on=time(14, 12, 47),
        mode="CW",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="14.062",
        operator="SM6Y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )

    text = AdifFileExporter().export(session.qsos)

    assert "<TIME_ON:6>141200" in text
    assert "<TIME_OFF:6>141200" in text
