"""Write use cases for the QSO Logging feature.

Each command depends only on domain ports (LoggingSessionRepository /
AdifExporter) — none hold cross-call state of their own. The "current"
session is always the one `LoggingSessionRepository.find_unfinished()`
returns, so every command re-reads it before acting; for a human typing
one QSO every couple of minutes this costs nothing and keeps every
command trivially testable against a fake repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from pathlib import Path

from radio_pota_logging.domain.logging_session.entities import LoggingSession
from radio_pota_logging.domain.logging_session.exporter import AdifExporter
from radio_pota_logging.domain.logging_session.repository import LoggingSessionRepository
from radio_pota_logging.domain.logging_session.value_objects import (
    EntryDefaults,
    Qso,
    QsoTimestamp,
    StationDefaults,
)

from .dto import (
    AdifExportResult,
    EntryDefaultsDto,
    QsoDto,
    SessionStartResult,
    SubmitQsoRequest,
    SubmitQsoResult,
)


def _to_entry_defaults_dto(entry_defaults: EntryDefaults) -> EntryDefaultsDto:
    return EntryDefaultsDto(
        operator=entry_defaults.operator,
        mode=entry_defaults.mode,
        my_sig_info=entry_defaults.my_sig_info,
        rst_sent=entry_defaults.rst_sent,
        rst_rcvd=entry_defaults.rst_rcvd,
        freq=entry_defaults.freq,
        my_rig=entry_defaults.my_rig,
        tx_pwr=entry_defaults.tx_pwr,
        qso_date=entry_defaults.timestamp.qso_date,
        time_on=entry_defaults.timestamp.time_on,
    )


def _to_qso_dto(qso: Qso) -> QsoDto:
    return QsoDto(
        call=qso.call,
        qso_date=qso.timestamp.qso_date,
        time_on=qso.timestamp.time_on,
        time_off=qso.time_off,
        band=qso.band.value,
        mode=qso.mode,
        my_sig=qso.my_sig,
        my_sig_info=qso.my_sig_info,
        rst_sent=qso.rst_sent,
        rst_rcvd=qso.rst_rcvd,
        freq=str(qso.freq.megahertz),
        operator=qso.operator,
        my_rig=qso.my_rig,
        tx_pwr=qso.tx_pwr,
    )


def _require_current_session(repository: LoggingSessionRepository) -> LoggingSession:
    session = repository.find_unfinished()
    if session is None:
        raise RuntimeError(
            "No current logging session; call StartNewSessionCommand or ResumeSessionCommand first"
        )
    return session


@dataclass(frozen=True)
class ResumeSessionCommand:
    repository: LoggingSessionRepository

    def execute(self) -> SessionStartResult:
        session = _require_current_session(self.repository)
        return SessionStartResult(
            entry_defaults=_to_entry_defaults_dto(session.next_entry_defaults),
            qsos=tuple(_to_qso_dto(qso) for qso in session.qsos),
        )


@dataclass(frozen=True)
class StartNewSessionCommand:
    repository: LoggingSessionRepository

    def execute(
        self, *, qso_date: date, time_on: time, park_reference: str, freq: str
    ) -> SessionStartResult:
        existing = self.repository.find_unfinished()
        if existing is not None:
            self.repository.archive(existing)

        session = LoggingSession.start(
            StationDefaults(),
            QsoTimestamp(qso_date, time_on),
            my_sig_info=park_reference,
            freq=freq,
        )
        self.repository.save(session)
        return SessionStartResult(
            entry_defaults=_to_entry_defaults_dto(session.next_entry_defaults),
            qsos=(),
        )


@dataclass(frozen=True)
class SubmitQsoCommand:
    repository: LoggingSessionRepository

    def execute(self, request: SubmitQsoRequest) -> SubmitQsoResult:
        session = _require_current_session(self.repository)
        qso = session.record_qso(
            call=request.call,
            qso_date=request.qso_date,
            time_on=request.time_on,
            mode=request.mode,
            my_sig_info=request.my_sig_info,
            rst_sent=request.rst_sent,
            rst_rcvd=request.rst_rcvd,
            freq=request.freq,
            operator=request.operator,
            my_rig=request.my_rig,
            tx_pwr=request.tx_pwr,
        )
        self.repository.save(session)
        return SubmitQsoResult(
            entry_defaults=_to_entry_defaults_dto(session.next_entry_defaults),
            submitted=_to_qso_dto(qso),
        )


@dataclass(frozen=True)
class GenerateAdifCommand:
    repository: LoggingSessionRepository
    exporter: AdifExporter

    def execute(self, destination: Path) -> AdifExportResult:
        session = _require_current_session(self.repository)
        text = self.exporter.export(session.qsos)
        destination.write_text(text)
        return AdifExportResult(path=destination, qso_count=len(session.qsos))
