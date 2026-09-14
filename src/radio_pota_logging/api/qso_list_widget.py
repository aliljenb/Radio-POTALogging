"""Editable, ordered display of submitted QSOs."""

from __future__ import annotations

from datetime import date, time

from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtWidgets import QMenu, QTableWidget, QTableWidgetItem, QWidget

from radio_pota_logging.application.logging_session.dto import EditQsoRequest, QsoDto

from .qso_table_delegates import ModeDelegate, QsoDateDelegate, TimeOnDelegate, UppercaseCallDelegate

_COLUMNS = (
    "CALL",
    "QSO_DATE",
    "TIME_ON",
    "RST_RCVD",
    "RST_SENT",
    "FREQ",
    "MODE",
)

_CALL_COLUMN = _COLUMNS.index("CALL")
_QSO_DATE_COLUMN = _COLUMNS.index("QSO_DATE")
_TIME_ON_COLUMN = _COLUMNS.index("TIME_ON")
_RST_RCVD_COLUMN = _COLUMNS.index("RST_RCVD")
_RST_SENT_COLUMN = _COLUMNS.index("RST_SENT")
_FREQ_COLUMN = _COLUMNS.index("FREQ")
_MODE_COLUMN = _COLUMNS.index("MODE")


class QsoListWidget(QTableWidget):
    """Displays submitted QSOs, in order, and lets the operator edit them in place."""

    edited = pyqtSignal(int, EditQsoRequest)
    delete_requested = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(0, len(_COLUMNS), parent)
        self.setHorizontalHeaderLabels(_COLUMNS)
        self.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        self.setAlternatingRowColors(True)
        self.setItemDelegateForColumn(_CALL_COLUMN, UppercaseCallDelegate(self))
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)
        self._qsos: list[QsoDto] = []
        self.cellChanged.connect(self._on_cell_changed)

    def append_qso(self, qso: QsoDto) -> None:
        row = self.rowCount()
        self.insertRow(row)
        self._qsos.append(qso)
        self._write_row(row, qso)

    def apply_edit(self, row: int, qso: QsoDto) -> None:
        self._qsos[row] = qso
        self._write_row(row, qso)

    def revert_edit(self, row: int) -> None:
        self._write_row(row, self._qsos[row])

    def remove_row(self, row: int) -> None:
        del self._qsos[row]
        self.removeRow(row)

    def _on_context_menu_requested(self, pos: QPoint) -> None:
        row = self.rowAt(pos.y())
        if row < 0:
            return
        self.selectRow(row)
        menu = QMenu(self)
        delete_action = menu.addAction("Delete")
        chosen_action = menu.exec(self.viewport().mapToGlobal(pos))
        if chosen_action == delete_action:
            self.delete_requested.emit(row)

    def _write_row(self, row: int, qso: QsoDto) -> None:
        values = (
            qso.call,
            qso.qso_date.isoformat(),
            qso.time_on.isoformat(),
            qso.rst_rcvd,
            qso.rst_sent,
            qso.freq,
            qso.mode,
        )
        self.blockSignals(True)
        try:
            for column, value in enumerate(values):
                self.setItem(row, column, QTableWidgetItem(value))
        finally:
            self.blockSignals(False)

    def _on_cell_changed(self, row: int, column: int) -> None:
        item = self.item(row, column)
        if item is None:
            return
        text = item.text()
        cached = self._qsos[row]
        request = EditQsoRequest(
            index=row,
            call=text if column == _CALL_COLUMN else cached.call,
            qso_date=date.fromisoformat(text) if column == _QSO_DATE_COLUMN else cached.qso_date,
            time_on=time.fromisoformat(text) if column == _TIME_ON_COLUMN else cached.time_on,
            mode=text if column == _MODE_COLUMN else cached.mode,
            rst_sent=text if column == _RST_SENT_COLUMN else cached.rst_sent,
            rst_rcvd=text if column == _RST_RCVD_COLUMN else cached.rst_rcvd,
            freq=text if column == _FREQ_COLUMN else cached.freq,
        )
        self.edited.emit(row, request)
