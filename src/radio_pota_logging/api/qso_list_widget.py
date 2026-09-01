"""Read-only, ordered display of submitted QSOs."""

from __future__ import annotations

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QWidget

from radio_pota_logging.application.logging_session.dto import QsoDto

_COLUMNS = (
    "CALL",
    "QSO_DATE",
    "TIME_ON",
    "RST_RCVD",
    "RST_SENT",
    "FREQ",
    "MODE",
)


class QsoListWidget(QTableWidget):
    """Displays submitted QSOs, in order, read-only."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(0, len(_COLUMNS), parent)
        self.setHorizontalHeaderLabels(_COLUMNS)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)

    def append_qso(self, qso: QsoDto) -> None:
        row = self.rowCount()
        self.insertRow(row)
        values = (
            qso.call,
            qso.qso_date.isoformat(),
            qso.time_on.isoformat(),
            qso.rst_rcvd,
            qso.rst_sent,
            qso.freq,
            qso.mode,
        )
        for column, value in enumerate(values):
            self.setItem(row, column, QTableWidgetItem(value))
