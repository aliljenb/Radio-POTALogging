"""Collects the park reference, date, start time, and frequency for a new session, or quit."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time

from PyQt6.QtCore import QDate, QTime
from PyQt6.QtWidgets import (
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from .uppercase_field import uppercase_as_typed


@dataclass(frozen=True)
class SessionSetupResult:
    park_reference: str
    qso_date: date
    time_on: time
    freq: str


class SessionSetupDialog(QDialog):
    """Modal collection of park reference/date/time/frequency before a clean session begins."""

    def __init__(self, parent: QWidget | None = None, now: datetime | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Session")
        self.setup_result: SessionSetupResult | None = None

        current = now if now is not None else datetime.now(UTC)

        self._park_reference = QLineEdit()
        uppercase_as_typed(self._park_reference)
        self._qso_date = QDateEdit()
        self._qso_date.setCalendarPopup(True)
        self._qso_date.setDate(QDate(current.year, current.month, current.day))
        self._time_on = QTimeEdit()
        self._time_on.setTime(QTime(current.hour, current.minute, current.second))
        self._freq = QLineEdit()

        form = QFormLayout()
        form.addRow("POTA park reference number", self._park_reference)
        form.addRow("Date", self._qso_date)
        form.addRow("Time of first QSO", self._time_on)
        form.addRow("Frequency", self._freq)

        buttons = QDialogButtonBox()
        ok_button = buttons.addButton("OK", QDialogButtonBox.ButtonRole.AcceptRole)
        quit_button = buttons.addButton("Quit", QDialogButtonBox.ButtonRole.RejectRole)
        assert ok_button is not None
        assert quit_button is not None
        self._ok_button = ok_button
        self._ok_button.setEnabled(False)
        self._ok_button.clicked.connect(self._accept_setup)
        quit_button.clicked.connect(self.reject)

        self._park_reference.textChanged.connect(self._update_ok_enabled)
        self._freq.textChanged.connect(self._update_ok_enabled)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _update_ok_enabled(self) -> None:
        self._ok_button.setEnabled(
            bool(self._park_reference.text().strip()) and bool(self._freq.text().strip())
        )

    def _accept_setup(self) -> None:
        qso_date_value = self._qso_date.date()
        time_on_value = self._time_on.time()
        self.setup_result = SessionSetupResult(
            park_reference=self._park_reference.text(),
            qso_date=date(qso_date_value.year(), qso_date_value.month(), qso_date_value.day()),
            time_on=time(time_on_value.hour(), time_on_value.minute(), time_on_value.second()),
            freq=self._freq.text(),
        )
        self.accept()
