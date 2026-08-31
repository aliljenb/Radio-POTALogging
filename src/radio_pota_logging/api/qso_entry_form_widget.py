"""Renders the QSO entry form and emits a SubmitQsoRequest on submit."""

from __future__ import annotations

from datetime import date, time
from typing import cast

from PyQt6.QtCore import QDate, QEvent, QObject, Qt, QTime, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from radio_pota_logging.application.logging_session.dto import (
    MODE_OPTIONS,
    EntryDefaultsDto,
    SubmitQsoRequest,
)

from .uppercase_field import uppercase_as_typed


class QsoEntryFormWidget(QWidget):
    """Renders the 11 entry fields; pre-fills from EntryDefaultsDto; emits on submit."""

    submitted = pyqtSignal(SubmitQsoRequest)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._call = QLineEdit()
        uppercase_as_typed(self._call)
        self._rst_rcvd = QLineEdit()
        self._rst_sent = QLineEdit()
        self._time_on = QTimeEdit()
        self._freq = QLineEdit()
        self._my_sig_info = QLineEdit()
        uppercase_as_typed(self._my_sig_info)
        self._qso_date = QDateEdit()
        self._qso_date.setCalendarPopup(True)
        self._mode = QComboBox()
        self._mode.addItems(MODE_OPTIONS)
        self._operator = QLineEdit()
        uppercase_as_typed(self._operator)
        self._my_rig = QLineEdit()
        self._tx_pwr = QLineEdit()
        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: red;")
        self._error_label.hide()

        self._column_1 = QFormLayout()
        self._column_1.addRow("CALL", self._call)
        self._column_1.addRow("RST_RCVD", self._rst_rcvd)
        self._column_1.addRow("RST_SENT", self._rst_sent)
        self._column_1.addRow("TIME_ON", self._time_on)

        self._column_2 = QFormLayout()
        self._column_2.addRow("FREQ", self._freq)
        self._column_2.addRow("MY_SIG_INFO", self._my_sig_info)
        self._column_2.addRow("QSO_DATE", self._qso_date)
        self._column_2.addRow("MODE", self._mode)

        self._column_3 = QFormLayout()
        self._column_3.addRow("OPERATOR", self._operator)
        self._column_3.addRow("MY_RIG", self._my_rig)
        self._column_3.addRow("TX_PWR", self._tx_pwr)

        columns_layout = QHBoxLayout()
        columns_layout.addLayout(self._column_1)
        columns_layout.addLayout(self._column_2)
        columns_layout.addLayout(self._column_3)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self._on_submit_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self._error_label)
        layout.addLayout(columns_layout)
        layout.addWidget(submit_button)
        self.setLayout(layout)

        self._fields = [
            self._call,
            self._rst_rcvd,
            self._rst_sent,
            self._time_on,
            self._freq,
            self._my_sig_info,
            self._qso_date,
            self._mode,
            self._operator,
            self._my_rig,
            self._tx_pwr,
        ]
        for field in self._fields:
            field.installEventFilter(self)
        for earlier, later in zip(self._fields, self._fields[1:], strict=False):
            QWidget.setTabOrder(earlier, later)

    def apply_defaults(self, defaults: EntryDefaultsDto) -> None:
        self._call.clear()
        self._qso_date.setDate(_to_qdate(defaults.qso_date))
        self._time_on.setTime(_to_qtime(defaults.time_on))
        self._mode.setCurrentText(defaults.mode)
        self._my_sig_info.setText(defaults.my_sig_info)
        self._rst_sent.setText(defaults.rst_sent)
        self._rst_rcvd.setText(defaults.rst_rcvd)
        self._freq.setText(defaults.freq)
        self._operator.setText(defaults.operator)
        self._my_rig.setText(defaults.my_rig)
        self._tx_pwr.setText(defaults.tx_pwr)
        self._call.setFocus()

    def show_error(self, message: str) -> None:
        self._error_label.setText(message)
        self._error_label.show()

    def clear_error(self) -> None:
        self._error_label.clear()
        self._error_label.hide()

    def eventFilter(self, obj: QObject | None, event: QEvent | None) -> bool:  # noqa: N802
        if event is not None and event.type() == QEvent.Type.KeyPress:
            key_event = cast(QKeyEvent, event)
            if key_event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self._on_enter_pressed()
                return True
        return super().eventFilter(obj, event)

    def _on_enter_pressed(self) -> None:
        if self._call.text():
            self._on_submit_clicked()

    def _on_submit_clicked(self) -> None:
        qso_date_value = self._qso_date.date()
        time_on_value = self._time_on.time()
        request = SubmitQsoRequest(
            call=self._call.text(),
            qso_date=date(qso_date_value.year(), qso_date_value.month(), qso_date_value.day()),
            time_on=time(time_on_value.hour(), time_on_value.minute(), time_on_value.second()),
            mode=self._mode.currentText(),
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
