"""Renders the QSO entry form and emits a SubmitQsoRequest on submit."""

from __future__ import annotations

from datetime import date, time

from PyQt6.QtCore import QDate, QTime, pyqtSignal
from PyQt6.QtWidgets import (
    QDateEdit,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from radio_pota_logging.application.logging_session.dto import EntryDefaultsDto, SubmitQsoRequest


class QsoEntryFormWidget(QWidget):
    """Renders the 11 entry fields; pre-fills from EntryDefaultsDto; emits on submit."""

    submitted = pyqtSignal(SubmitQsoRequest)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._call = QLineEdit()
        self._call.textEdited.connect(self._uppercase_call)
        self._qso_date = QDateEdit()
        self._qso_date.setCalendarPopup(True)
        self._time_on = QTimeEdit()
        self._mode = QLineEdit()
        self._my_sig_info = QLineEdit()
        self._rst_sent = QLineEdit()
        self._rst_rcvd = QLineEdit()
        self._freq = QLineEdit()
        self._operator = QLineEdit()
        self._my_rig = QLineEdit()
        self._tx_pwr = QLineEdit()
        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: red;")
        self._error_label.hide()

        form = QFormLayout()
        form.addRow("CALL", self._call)
        form.addRow("QSO_DATE", self._qso_date)
        form.addRow("TIME_ON", self._time_on)
        form.addRow("MODE", self._mode)
        form.addRow("MY_SIG_INFO", self._my_sig_info)
        form.addRow("RST_SENT", self._rst_sent)
        form.addRow("RST_RCVD", self._rst_rcvd)
        form.addRow("FREQ", self._freq)
        form.addRow("OPERATOR", self._operator)
        form.addRow("MY_RIG", self._my_rig)
        form.addRow("TX_PWR", self._tx_pwr)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self._on_submit_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self._error_label)
        layout.addLayout(form)
        layout.addWidget(submit_button)
        self.setLayout(layout)

    def apply_defaults(self, defaults: EntryDefaultsDto) -> None:
        self._call.clear()
        self._qso_date.setDate(_to_qdate(defaults.qso_date))
        self._time_on.setTime(_to_qtime(defaults.time_on))
        self._mode.setText(defaults.mode)
        self._my_sig_info.setText(defaults.my_sig_info)
        self._rst_sent.setText(defaults.rst_sent)
        self._rst_rcvd.setText(defaults.rst_rcvd)
        self._freq.setText(defaults.freq)
        self._operator.setText(defaults.operator)
        self._my_rig.setText(defaults.my_rig)
        self._tx_pwr.setText(defaults.tx_pwr)
        self._call.setFocus()

    def _uppercase_call(self, text: str) -> None:
        cursor_position = self._call.cursorPosition()
        self._call.setText(text.upper())
        self._call.setCursorPosition(cursor_position)

    def show_error(self, message: str) -> None:
        self._error_label.setText(message)
        self._error_label.show()

    def clear_error(self) -> None:
        self._error_label.clear()
        self._error_label.hide()

    def _on_submit_clicked(self) -> None:
        qso_date_value = self._qso_date.date()
        time_on_value = self._time_on.time()
        request = SubmitQsoRequest(
            call=self._call.text(),
            qso_date=date(qso_date_value.year(), qso_date_value.month(), qso_date_value.day()),
            time_on=time(time_on_value.hour(), time_on_value.minute(), time_on_value.second()),
            mode=self._mode.text(),
            my_sig_info=self._my_sig_info.text(),
            rst_sent=self._rst_sent.text(),
            rst_rcvd=self._rst_rcvd.text(),
            freq=self._freq.text(),
            operator=self._operator.text(),
            my_rig=self._my_rig.text(),
            tx_pwr=self._tx_pwr.text(),
        )
        self.submitted.emit(request)


def _to_qdate(value: date) -> QDate:
    return QDate(value.year, value.month, value.day)


def _to_qtime(value: time) -> QTime:
    return QTime(value.hour, value.minute, value.second)
