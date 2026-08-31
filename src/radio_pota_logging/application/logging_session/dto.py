"""Data crossing the application boundary for the QSO Logging feature."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from pathlib import Path

from radio_pota_logging.domain.logging_session.value_objects import (
    MODE_OPTIONS,
    default_rst_for_mode,
)

__all__ = [
    "MODE_OPTIONS",
    "AdifExportResult",
    "EntryDefaultsDto",
    "QsoDto",
    "SessionStartResult",
    "SubmitQsoRequest",
    "SubmitQsoResult",
    "default_rst_for_mode",
]


@dataclass(frozen=True)
class SubmitQsoRequest:
    """Raw field values as typed/edited on the entry form."""

    call: str
    qso_date: date
    time_on: time
    mode: str
    my_sig_info: str
    rst_sent: str
    rst_rcvd: str
    freq: str
    operator: str
    my_rig: str
    tx_pwr: str


@dataclass(frozen=True)
class EntryDefaultsDto:
    """Fields to pre-fill on the next entry form."""

    operator: str
    mode: str
    my_sig_info: str
    rst_sent: str
    rst_rcvd: str
    freq: str
    my_rig: str
    tx_pwr: str
    qso_date: date
    time_on: time


@dataclass(frozen=True)
class QsoDto:
    """One row for the QSO list / ADIF export."""

    call: str
    qso_date: date
    time_on: time
    time_off: time
    band: str
    mode: str
    my_sig: str
    my_sig_info: str
    rst_sent: str
    rst_rcvd: str
    freq: str
    operator: str
    my_rig: str
    tx_pwr: str


@dataclass(frozen=True)
class SessionStartResult:
    entry_defaults: EntryDefaultsDto
    qsos: tuple[QsoDto, ...]


@dataclass(frozen=True)
class SubmitQsoResult:
    entry_defaults: EntryDefaultsDto
    submitted: QsoDto


@dataclass(frozen=True)
class AdifExportResult:
    path: Path
    qso_count: int
