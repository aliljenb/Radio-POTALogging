"""Entities for the QSO Logging bounded context."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time

from .value_objects import (
    EntryDefaults,
    Frequency,
    Qso,
    QsoTimestamp,
    SessionId,
    SessionStart,
    StationDefaults,
    default_rst_for_mode,
)


@dataclass(eq=False)
class LoggingSession:
    """One activation's ordered, append-only sequence of QSOs.

    Identity is `session_id`; two sessions are equal only if they share one,
    regardless of their QSO contents (entity semantics, not value semantics).
    """

    session_id: SessionId
    qsos: tuple[Qso, ...]
    next_entry_defaults: EntryDefaults
    session_start: SessionStart

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LoggingSession) and self.session_id == other.session_id

    def __hash__(self) -> int:
        return hash(self.session_id)

    @classmethod
    def start(
        cls,
        now: QsoTimestamp,
        *,
        operator: str,
        mode: str,
        my_rig: str,
        tx_pwr: str,
        my_sig_info: str = "",
        freq: str = "",
    ) -> LoggingSession:
        return cls(
            session_id=SessionId.generate(),
            qsos=(),
            next_entry_defaults=EntryDefaults.seed(
                now,
                operator=operator,
                mode=mode,
                my_rig=my_rig,
                tx_pwr=tx_pwr,
                my_sig_info=my_sig_info,
                freq=freq,
            ),
            session_start=SessionStart(qso_date=now.qso_date, my_sig_info=my_sig_info),
        )

    def record_qso(
        self,
        *,
        call: str,
        qso_date: date,
        time_on: time,
        mode: str,
        my_sig_info: str,
        rst_sent: str,
        rst_rcvd: str,
        freq: str,
        operator: str,
        my_rig: str,
        tx_pwr: str,
    ) -> Qso:
        """Validate, append, and recompute next_entry_defaults; raise and leave state
        unchanged on invalid FREQ."""
        frequency = Frequency.parse(freq)
        _ = frequency.band  # raises FrequencyOutOfBandError before any state changes

        timestamp = QsoTimestamp(qso_date=qso_date, time_on=time_on)
        qso = Qso(
            call=call,
            timestamp=timestamp,
            mode=mode,
            my_sig=StationDefaults.my_sig,
            my_sig_info=my_sig_info,
            rst_sent=rst_sent,
            rst_rcvd=rst_rcvd,
            freq=frequency,
            operator=operator,
            my_rig=my_rig,
            tx_pwr=tx_pwr,
        )

        self.qsos = (*self.qsos, qso)
        self.next_entry_defaults = EntryDefaults(
            operator=operator,
            mode=mode,
            my_sig_info=my_sig_info,
            rst_sent=default_rst_for_mode(mode),
            rst_rcvd=default_rst_for_mode(mode),
            freq=str(frequency.megahertz),
            my_rig=my_rig,
            tx_pwr=tx_pwr,
            timestamp=timestamp.plus_two_minutes(),
        )
        return qso
