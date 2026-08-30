"""Read-only, ordered display of submitted QSOs."""

from __future__ import annotations

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QWidget

from radio_pota_logging.application.logging_session.dto import QsoDto

_COLUMNS = (
    "OPERATOR",
    "CALL",
    "QSO_DATE",
    "TIME_ON",
    "TIME_OFF",
    "BAND",
    "MODE",
    "MY_SIG",
    "MY_SIG_INFO",
    "RST_SENT",
    "RST_RCVD",
    "FREQ",
    "MY_RIG",
    "TX_PWR",
)


class QsoListWidget(QTableWidget):
    """Displays submitted QSOs, in order, read-only."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(0, len(_COLUMNS), parent)
        self.setHorizontalHeaderLabels(_COLUMNS)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def append_qso(self, qso: QsoDto) -> None:
        row = self.rowCount()
        self.insertRow(row)
        values = (
            qso.operator,
            qso.call,
            qso.qso_date.isoformat(),
            qso.time_on.isoformat(),
            qso.time_off.isoformat(),
            qso.band,
            qso.mode,
            qso.my_sig,
            qso.my_sig_info,
            qso.rst_sent,
            qso.rst_rcvd,
            qso.freq,
            qso.my_rig,
            qso.tx_pwr,
        )
        for column, value in enumerate(values):
            self.setItem(row, column, QTableWidgetItem(value))
