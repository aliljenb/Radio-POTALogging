"""Per-column Qt editors for QsoListWidget's in-place cell editing."""

from __future__ import annotations

from datetime import date, time
from typing import cast

from PyQt6.QtCore import QAbstractItemModel, QDate, QModelIndex, Qt, QTime
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QLineEdit,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTimeEdit,
    QWidget,
)

from radio_pota_logging.application.logging_session.dto import MODE_OPTIONS

from .uppercase_field import uppercase_as_typed


class UppercaseCallDelegate(QStyledItemDelegate):
    """Presents and commits CALL edits through an uppercase-as-typed line edit."""

    def createEditor(  # noqa: N802
        self, parent: QWidget | None, option: QStyleOptionViewItem, index: QModelIndex
    ) -> QWidget | None:
        editor = QLineEdit(parent)
        uppercase_as_typed(editor)
        return editor

    def setEditorData(self, editor: QWidget | None, index: QModelIndex) -> None:  # noqa: N802
        assert editor is not None
        cast(QLineEdit, editor).setText(str(index.data()))

    def setModelData(  # noqa: N802
        self, editor: QWidget | None, model: QAbstractItemModel | None, index: QModelIndex
    ) -> None:
        assert editor is not None
        if model is None:
            return
        model.setData(index, cast(QLineEdit, editor).text(), Qt.ItemDataRole.EditRole)


class QsoDateDelegate(QStyledItemDelegate):
    """Presents and commits QSO_DATE edits through a calendar date picker."""

    def createEditor(  # noqa: N802
        self, parent: QWidget | None, option: QStyleOptionViewItem, index: QModelIndex
    ) -> QWidget | None:
        editor = QDateEdit(parent)
        editor.setCalendarPopup(True)
        return editor

    def setEditorData(self, editor: QWidget | None, index: QModelIndex) -> None:  # noqa: N802
        assert editor is not None
        value = date.fromisoformat(str(index.data()))
        cast(QDateEdit, editor).setDate(_to_qdate(value))

    def setModelData(  # noqa: N802
        self, editor: QWidget | None, model: QAbstractItemModel | None, index: QModelIndex
    ) -> None:
        assert editor is not None
        if model is None:
            return
        qdate = cast(QDateEdit, editor).date()
        value = date(qdate.year(), qdate.month(), qdate.day())
        model.setData(index, value.isoformat(), Qt.ItemDataRole.EditRole)


class TimeOnDelegate(QStyledItemDelegate):
    """Presents and commits TIME_ON edits through a seconds-free time picker."""

    def createEditor(  # noqa: N802
        self, parent: QWidget | None, option: QStyleOptionViewItem, index: QModelIndex
    ) -> QWidget | None:
        editor = QTimeEdit(parent)
        editor.setDisplayFormat("HH:mm")
        return editor

    def setEditorData(self, editor: QWidget | None, index: QModelIndex) -> None:  # noqa: N802
        assert editor is not None
        value = time.fromisoformat(str(index.data()))
        cast(QTimeEdit, editor).setTime(_to_qtime(value))

    def setModelData(  # noqa: N802
        self, editor: QWidget | None, model: QAbstractItemModel | None, index: QModelIndex
    ) -> None:
        assert editor is not None
        if model is None:
            return
        qtime = cast(QTimeEdit, editor).time()
        value = time(qtime.hour(), qtime.minute(), 0)
        model.setData(index, value.isoformat(), Qt.ItemDataRole.EditRole)


class ModeDelegate(QStyledItemDelegate):
    """Presents and commits MODE edits through the fixed CW/SSB dropdown."""

    def createEditor(  # noqa: N802
        self, parent: QWidget | None, option: QStyleOptionViewItem, index: QModelIndex
    ) -> QWidget | None:
        editor = QComboBox(parent)
        editor.addItems(MODE_OPTIONS)
        return editor

    def setEditorData(self, editor: QWidget | None, index: QModelIndex) -> None:  # noqa: N802
        assert editor is not None
        cast(QComboBox, editor).setCurrentText(str(index.data()))

    def setModelData(  # noqa: N802
        self, editor: QWidget | None, model: QAbstractItemModel | None, index: QModelIndex
    ) -> None:
        assert editor is not None
        if model is None:
            return
        model.setData(index, cast(QComboBox, editor).currentText(), Qt.ItemDataRole.EditRole)


def _to_qdate(value: date) -> QDate:
    return QDate(value.year, value.month, value.day)


def _to_qtime(value: time) -> QTime:
    return QTime(value.hour, value.minute, value.second)
