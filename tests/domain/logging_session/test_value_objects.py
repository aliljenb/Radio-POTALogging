from datetime import date, time

import pytest
from radio_pota_logging.domain.logging_session.exceptions import (
    FrequencyFormatError,
    FrequencyOutOfBandError,
)
from radio_pota_logging.domain.logging_session.value_objects import (
    MODE_OPTIONS,
    Band,
    EntryDefaults,
    Frequency,
    Qso,
    QsoTimestamp,
    SessionStart,
    StationDefaults,
)


def _qso(call: str = "W1AW", my_sig_info: str = "K-1234", operator: str = "SM6Y") -> Qso:
    return Qso(
        call=call,
        timestamp=QsoTimestamp(date(2026, 8, 30), time(9, 0)),
        mode="CW",
        my_sig="POTA",
        my_sig_info=my_sig_info,
        rst_sent="599",
        rst_rcvd="599",
        freq=Frequency.parse("14.062"),
        operator=operator,
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )


@pytest.mark.parametrize(
    ("freq_text", "expected_band"),
    [
        ("1.800", Band.M160),
        ("2.000", Band.M160),
        ("3.500", Band.M80),
        ("4.000", Band.M80),
        ("7.000", Band.M40),
        ("7.300", Band.M40),
        ("10.100", Band.M30),
        ("10.150", Band.M30),
        ("14.000", Band.M20),
        ("14.350", Band.M20),
        ("18.068", Band.M17),
        ("18.168", Band.M17),
        ("21.000", Band.M15),
        ("21.450", Band.M15),
        ("24.890", Band.M12),
        ("24.990", Band.M12),
        ("28.000", Band.M10),
        ("29.700", Band.M10),
        ("50.000", Band.M6),
        ("54.000", Band.M6),
    ],
)
def test_frequency_band_boundaries(freq_text: str, expected_band: Band) -> None:
    assert Frequency.parse(freq_text).band is expected_band


@pytest.mark.parametrize("freq_text", ["1.799", "2.001", "6.999", "54.001", "0", "100.000"])
def test_frequency_out_of_band(freq_text: str) -> None:
    with pytest.raises(FrequencyOutOfBandError):
        _ = Frequency.parse(freq_text).band


@pytest.mark.parametrize("freq_text", ["", "abc", "14.06.2", "MHz"])
def test_frequency_format_error(freq_text: str) -> None:
    with pytest.raises(FrequencyFormatError):
        Frequency.parse(freq_text)


def test_frequency_str_roundtrips_decimal() -> None:
    assert str(Frequency.parse("14.0625").megahertz) == "14.0625"


def test_qso_timestamp_plus_two_minutes() -> None:
    timestamp = QsoTimestamp(date(2026, 8, 30), time(12, 0))
    assert timestamp.plus_two_minutes() == QsoTimestamp(date(2026, 8, 30), time(12, 2))


def test_qso_timestamp_plus_two_minutes_rolls_over_midnight() -> None:
    timestamp = QsoTimestamp(date(2026, 8, 30), time(23, 59))
    assert timestamp.plus_two_minutes() == QsoTimestamp(date(2026, 8, 31), time(0, 1))


def test_entry_defaults_seed_leaves_my_sig_info_and_freq_empty() -> None:
    now = QsoTimestamp(date(2026, 8, 30), time(9, 0))
    defaults = EntryDefaults.seed(StationDefaults(), now)
    assert defaults.my_sig_info == ""
    assert defaults.freq == ""
    assert defaults.operator == "SM6Y"
    assert defaults.mode == "CW"
    assert defaults.rst_sent == "599"
    assert defaults.rst_rcvd == "599"
    assert defaults.my_rig == "Elecraft KX2"
    assert defaults.tx_pwr == "5"


def test_entry_defaults_seed_uses_given_my_sig_info() -> None:
    now = QsoTimestamp(date(2026, 8, 30), time(9, 0))
    defaults = EntryDefaults.seed(StationDefaults(), now, my_sig_info="K-1234")
    assert defaults.my_sig_info == "K-1234"
    assert defaults.timestamp == now


def test_entry_defaults_seed_normalizes_my_sig_info_to_uppercase() -> None:
    now = QsoTimestamp(date(2026, 8, 30), time(9, 0))
    defaults = EntryDefaults.seed(StationDefaults(), now, my_sig_info="k-1234")
    assert defaults.my_sig_info == "K-1234"


def test_entry_defaults_seed_uses_given_freq() -> None:
    now = QsoTimestamp(date(2026, 8, 30), time(9, 0))
    defaults = EntryDefaults.seed(StationDefaults(), now, freq="14.062")
    assert defaults.freq == "14.062"


def test_entry_defaults_seed_normalizes_operator_to_uppercase() -> None:
    now = QsoTimestamp(date(2026, 8, 30), time(9, 0))
    defaults = EntryDefaults.seed(StationDefaults(operator="sm6y"), now)
    assert defaults.operator == "SM6Y"


def test_mode_options_is_cw_and_ssb() -> None:
    assert MODE_OPTIONS == ("CW", "SSB")


def test_session_start_normalizes_my_sig_info_to_uppercase() -> None:
    session_start = SessionStart(qso_date=date(2026, 8, 30), my_sig_info="k-1234")
    assert session_start.my_sig_info == "K-1234"


@pytest.mark.parametrize(
    ("call_text", "expected"),
    [
        ("w1aw", "W1AW"),
        ("W1aw", "W1AW"),
        ("sm6y/p", "SM6Y/P"),
        ("K1ABC", "K1ABC"),
    ],
)
def test_qso_call_is_normalized_to_uppercase(call_text: str, expected: str) -> None:
    assert _qso(call=call_text).call == expected


@pytest.mark.parametrize(
    ("my_sig_info_text", "expected"),
    [
        ("k-1234", "K-1234"),
        ("K-1234", "K-1234"),
        ("k-1234ab", "K-1234AB"),
    ],
)
def test_qso_my_sig_info_is_normalized_to_uppercase(my_sig_info_text: str, expected: str) -> None:
    assert _qso(my_sig_info=my_sig_info_text).my_sig_info == expected


@pytest.mark.parametrize(
    ("operator_text", "expected"),
    [
        ("sm6y", "SM6Y"),
        ("Sm6y", "SM6Y"),
        ("SM6Y", "SM6Y"),
    ],
)
def test_qso_operator_is_normalized_to_uppercase(operator_text: str, expected: str) -> None:
    assert _qso(operator=operator_text).operator == expected
