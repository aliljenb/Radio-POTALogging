"""Value objects for the QSO Logging bounded context."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation
from enum import Enum

from .exceptions import FrequencyFormatError, FrequencyOutOfBandError


@dataclass(frozen=True)
class SessionId:
    """Opaque identity for a LoggingSession, stable across resume."""

    value: uuid.UUID

    @classmethod
    def generate(cls) -> SessionId:
        return cls(uuid.uuid4())


class Band(Enum):
    """An amateur radio band, derived from a Frequency."""

    M160 = "160M"
    M80 = "80M"
    M40 = "40M"
    M30 = "30M"
    M20 = "20M"
    M17 = "17M"
    M15 = "15M"
    M12 = "12M"
    M10 = "10M"
    M6 = "6M"


# requirements.md Story 4 band-plan table.
_BAND_PLAN: tuple[tuple[Decimal, Decimal, Band], ...] = (
    (Decimal("1.800"), Decimal("2.000"), Band.M160),
    (Decimal("3.500"), Decimal("4.000"), Band.M80),
    (Decimal("7.000"), Decimal("7.300"), Band.M40),
    (Decimal("10.100"), Decimal("10.150"), Band.M30),
    (Decimal("14.000"), Decimal("14.350"), Band.M20),
    (Decimal("18.068"), Decimal("18.168"), Band.M17),
    (Decimal("21.000"), Decimal("21.450"), Band.M15),
    (Decimal("24.890"), Decimal("24.990"), Band.M12),
    (Decimal("28.000"), Decimal("29.700"), Band.M10),
    (Decimal("50.000"), Decimal("54.000"), Band.M6),
)


@dataclass(frozen=True)
class Frequency:
    """A QSO's operating frequency in MHz."""

    megahertz: Decimal

    @classmethod
    def parse(cls, text: str) -> Frequency:
        try:
            value = Decimal(text)
        except InvalidOperation as exc:
            raise FrequencyFormatError(f"{text!r} is not a valid decimal MHz value") from exc
        return cls(value)

    @property
    def band(self) -> Band:
        for low, high, band in _BAND_PLAN:
            if low <= self.megahertz <= high:
                return band
        raise FrequencyOutOfBandError(f"{self.megahertz} MHz is not within any known amateur band")


@dataclass(frozen=True)
class QsoTimestamp:
    """A QSO's date + time-on, always UTC (no timezone conversion)."""

    qso_date: date
    time_on: time

    def __post_init__(self) -> None:
        object.__setattr__(self, "time_on", self.time_on.replace(second=0, microsecond=0))

    def plus_two_minutes(self) -> QsoTimestamp:
        combined = datetime.combine(self.qso_date, self.time_on) + timedelta(minutes=2)
        return QsoTimestamp(combined.date(), combined.time())


@dataclass(frozen=True)
class SessionStart:
    """The QSO_DATE and park reference a session began with — fixed for its
    whole lifetime, unlike EntryDefaults, which mutates after every submitted QSO."""

    qso_date: date
    my_sig_info: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "my_sig_info", self.my_sig_info.upper())


@dataclass(frozen=True)
class StationDefaults:
    """Fixed application-level constants used to seed a brand-new session."""

    operator: str = "SM6Y"
    mode: str = "CW"
    my_sig: str = "POTA"
    my_rig: str = "Elecraft KX2"
    tx_pwr: str = "5"


# The only two supported MODE values (requirements.md Story 9).
MODE_OPTIONS: tuple[str, str] = ("CW", "SSB")

# The RST report each MODE defaults to (requirements.md Story 13).
_RST_DEFAULTS_BY_MODE: dict[str, str] = {"CW": "599", "SSB": "59"}


def default_rst_for_mode(mode: str) -> str:
    """The default RST_SENT/RST_RCVD value for a given MODE ("CW" or "SSB")."""
    return _RST_DEFAULTS_BY_MODE[mode]


@dataclass(frozen=True)
class EntryDefaults:
    """Pre-fill template for the next entry form — every field except CALL."""

    operator: str
    mode: str
    my_sig_info: str
    rst_sent: str
    rst_rcvd: str
    freq: str
    my_rig: str
    tx_pwr: str
    timestamp: QsoTimestamp

    def __post_init__(self) -> None:
        object.__setattr__(self, "my_sig_info", self.my_sig_info.upper())
        object.__setattr__(self, "operator", self.operator.upper())

    @classmethod
    def seed(
        cls,
        station_defaults: StationDefaults,
        now: QsoTimestamp,
        my_sig_info: str = "",
        freq: str = "",
    ) -> EntryDefaults:
        return cls(
            operator=station_defaults.operator,
            mode=station_defaults.mode,
            my_sig_info=my_sig_info,
            rst_sent=default_rst_for_mode(station_defaults.mode),
            rst_rcvd=default_rst_for_mode(station_defaults.mode),
            freq=freq,
            my_rig=station_defaults.my_rig,
            tx_pwr=station_defaults.tx_pwr,
            timestamp=now,
        )


@dataclass(frozen=True)
class Qso:
    """One immutable, submitted contact."""

    call: str
    timestamp: QsoTimestamp
    mode: str
    my_sig: str
    my_sig_info: str
    rst_sent: str
    rst_rcvd: str
    freq: Frequency
    operator: str
    my_rig: str
    tx_pwr: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "call", self.call.upper())
        object.__setattr__(self, "my_sig_info", self.my_sig_info.upper())
        object.__setattr__(self, "operator", self.operator.upper())

    @property
    def time_off(self) -> time:
        return self.timestamp.time_on

    @property
    def band(self) -> Band:
        return self.freq.band
