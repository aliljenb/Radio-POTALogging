"""File-based adapter for LoggingSessionRepository — no ORM/database."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Any

from radio_pota_logging.domain.logging_session.entities import LoggingSession
from radio_pota_logging.domain.logging_session.value_objects import (
    EntryDefaults,
    Frequency,
    Qso,
    QsoTimestamp,
    SessionId,
    SessionStart,
)

_SESSION_FILENAME = ".qso_session.json"


class FileLoggingSessionRepository:
    """Persists the single active LoggingSession as a JSON file in `directory`."""

    def __init__(self, directory: Path) -> None:
        self._directory = directory
        self._path = directory / _SESSION_FILENAME

    def find_unfinished(self) -> LoggingSession | None:
        if not self._path.exists():
            return None
        return _session_from_dict(json.loads(self._path.read_text()))

    def save(self, session: LoggingSession) -> None:
        self._path.write_text(json.dumps(_session_to_dict(session), indent=2))

    def archive(self, session: LoggingSession) -> None:
        if not self._path.exists():
            return
        archived_at = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        self._path.rename(self._directory / f".qso_session.{archived_at}.json")


def _qso_timestamp_to_dict(timestamp: QsoTimestamp) -> dict[str, str]:
    return {
        "qso_date": timestamp.qso_date.isoformat(),
        "time_on": timestamp.time_on.isoformat(),
    }


def _qso_timestamp_from_dict(data: dict[str, Any]) -> QsoTimestamp:
    return QsoTimestamp(
        qso_date=date.fromisoformat(data["qso_date"]),
        time_on=time.fromisoformat(data["time_on"]),
    )


def _session_start_to_dict(session_start: SessionStart) -> dict[str, str]:
    return {
        "qso_date": session_start.qso_date.isoformat(),
        "my_sig_info": session_start.my_sig_info,
    }


def _session_start_from_dict(data: dict[str, Any]) -> SessionStart:
    return SessionStart(
        qso_date=date.fromisoformat(data["qso_date"]),
        my_sig_info=data["my_sig_info"],
    )


def _entry_defaults_to_dict(entry_defaults: EntryDefaults) -> dict[str, Any]:
    return {
        "operator": entry_defaults.operator,
        "mode": entry_defaults.mode,
        "my_sig_info": entry_defaults.my_sig_info,
        "rst_sent": entry_defaults.rst_sent,
        "rst_rcvd": entry_defaults.rst_rcvd,
        "freq": entry_defaults.freq,
        "my_rig": entry_defaults.my_rig,
        "tx_pwr": entry_defaults.tx_pwr,
        "timestamp": _qso_timestamp_to_dict(entry_defaults.timestamp),
    }


def _entry_defaults_from_dict(data: dict[str, Any]) -> EntryDefaults:
    return EntryDefaults(
        operator=data["operator"],
        mode=data["mode"],
        my_sig_info=data["my_sig_info"],
        rst_sent=data["rst_sent"],
        rst_rcvd=data["rst_rcvd"],
        freq=data["freq"],
        my_rig=data["my_rig"],
        tx_pwr=data["tx_pwr"],
        timestamp=_qso_timestamp_from_dict(data["timestamp"]),
    )


def _qso_to_dict(qso: Qso) -> dict[str, Any]:
    return {
        "call": qso.call,
        "timestamp": _qso_timestamp_to_dict(qso.timestamp),
        "mode": qso.mode,
        "my_sig": qso.my_sig,
        "my_sig_info": qso.my_sig_info,
        "rst_sent": qso.rst_sent,
        "rst_rcvd": qso.rst_rcvd,
        "freq": str(qso.freq.megahertz),
        "operator": qso.operator,
        "my_rig": qso.my_rig,
        "tx_pwr": qso.tx_pwr,
    }


def _qso_from_dict(data: dict[str, Any]) -> Qso:
    return Qso(
        call=data["call"],
        timestamp=_qso_timestamp_from_dict(data["timestamp"]),
        mode=data["mode"],
        my_sig=data["my_sig"],
        my_sig_info=data["my_sig_info"],
        rst_sent=data["rst_sent"],
        rst_rcvd=data["rst_rcvd"],
        freq=Frequency.parse(data["freq"]),
        operator=data["operator"],
        my_rig=data["my_rig"],
        tx_pwr=data["tx_pwr"],
    )


def _session_to_dict(session: LoggingSession) -> dict[str, Any]:
    return {
        "session_id": str(session.session_id.value),
        "qsos": [_qso_to_dict(qso) for qso in session.qsos],
        "next_entry_defaults": _entry_defaults_to_dict(session.next_entry_defaults),
        "session_start": _session_start_to_dict(session.session_start),
    }


def _session_from_dict(data: dict[str, Any]) -> LoggingSession:
    return LoggingSession(
        session_id=SessionId(uuid.UUID(data["session_id"])),
        qsos=tuple(_qso_from_dict(qso) for qso in data["qsos"]),
        next_entry_defaults=_entry_defaults_from_dict(data["next_entry_defaults"]),
        session_start=_session_start_from_dict(data["session_start"]),
    )
