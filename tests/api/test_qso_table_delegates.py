from datetime import date, time

from PyQt6.QtCore import QModelIndex
from PyQt6.QtWidgets import QComboBox, QDateEdit, QLineEdit, QStyleOptionViewItem, QTimeEdit
from pytestqt.qtbot import QtBot
from radio_pota_logging.api.qso_list_widget import QsoListWidget
from radio_pota_logging.api.qso_table_delegates import (
    ModeDelegate,
    QsoDateDelegate,
    TimeOnDelegate,
    UppercaseCallDelegate,
)
from radio_pota_logging.application.logging_session.dto import QsoDto


def _qso() -> QsoDto:
    return QsoDto(
        call="W1AW",
        qso_date=date(2026, 9, 7),
        time_on=time(14, 12),
        time_off=time(14, 12),
        band="20M",
        mode="CW",
        my_sig="POTA",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="14.062",
        operator="SM6Y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )


def _index_at(widget: QsoListWidget, row: int, column: int) -> QModelIndex:
    model = widget.model()
    assert model is not None
    return model.index(row, column)


def test_uppercase_call_delegate_creates_a_line_edit(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    widget.append_qso(_qso())
    delegate = UppercaseCallDelegate()

    editor = delegate.createEditor(widget, QStyleOptionViewItem(), _index_at(widget, 0, 0))

    assert isinstance(editor, QLineEdit)


def test_uppercase_call_delegate_round_trip_uppercases(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    widget.append_qso(_qso())
    delegate = UppercaseCallDelegate()
    index = _index_at(widget, 0, 0)
    editor = delegate.createEditor(widget, QStyleOptionViewItem(), index)
    assert isinstance(editor, QLineEdit)

    delegate.setEditorData(editor, index)
    editor.clear()
    qtbot.keyClicks(editor, "k1abc")
    model = widget.model()
    assert model is not None
    delegate.setModelData(editor, model, index)

    assert widget.item(0, 0).text() == "K1ABC"


def test_qso_date_delegate_creates_a_date_edit(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    widget.append_qso(_qso())
    delegate = QsoDateDelegate()

    editor = delegate.createEditor(widget, QStyleOptionViewItem(), _index_at(widget, 0, 1))

    assert isinstance(editor, QDateEdit)


def test_qso_date_delegate_set_editor_data_parses_iso_text(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    widget.append_qso(_qso())
    delegate = QsoDateDelegate()
    index = _index_at(widget, 0, 1)
    editor = delegate.createEditor(widget, QStyleOptionViewItem(), index)
    assert isinstance(editor, QDateEdit)

    delegate.setEditorData(editor, index)

    qdate = editor.date()
    assert (qdate.year(), qdate.month(), qdate.day()) == (2026, 9, 7)


def test_time_on_delegate_creates_a_time_edit_with_no_seconds(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    widget.append_qso(_qso())
    delegate = TimeOnDelegate()

    editor = delegate.createEditor(widget, QStyleOptionViewItem(), _index_at(widget, 0, 2))

    assert isinstance(editor, QTimeEdit)
    assert editor.displayFormat() == "HH:mm"


def test_time_on_delegate_set_model_data_forces_zero_seconds(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    widget.append_qso(_qso())
    delegate = TimeOnDelegate()
    index = _index_at(widget, 0, 2)
    editor = delegate.createEditor(widget, QStyleOptionViewItem(), index)
    assert isinstance(editor, QTimeEdit)
    delegate.setEditorData(editor, index)
    editor.setTime(editor.time().addSecs(47))  # would be 14:12:47 if seconds survived

    model = widget.model()
    assert model is not None
    delegate.setModelData(editor, model, index)

    assert widget.item(0, 2).text() == "14:12:00"


def test_mode_delegate_creates_a_non_editable_combo_box_with_cw_and_ssb(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    widget.append_qso(_qso())
    delegate = ModeDelegate()

    editor = delegate.createEditor(widget, QStyleOptionViewItem(), _index_at(widget, 0, 6))

    assert isinstance(editor, QComboBox)
    assert not editor.isEditable()
    assert [editor.itemText(i) for i in range(editor.count())] == ["CW", "SSB"]
