from datetime import date, time

import pytest
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtWidgets import QComboBox, QLineEdit, QMenu, QTableWidget, QTimeEdit
from pytestqt.qtbot import QtBot
from radio_pota_logging.api.qso_list_widget import QsoListWidget
from radio_pota_logging.application.logging_session.dto import EditQsoRequest, QsoDto


def _qso(call: str, time_on: time) -> QsoDto:
    return QsoDto(
        call=call,
        qso_date=date(2026, 8, 30),
        time_on=time_on,
        time_off=time_on,
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


def _cell_text(widget: QsoListWidget, row: int, column: int) -> str:
    item = widget.item(row, column)
    assert item is not None
    return item.text()


def test_append_qso_adds_rows_in_order(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)

    widget.append_qso(_qso("W1AW", time(9, 0)))
    widget.append_qso(_qso("K1ABC", time(9, 2)))

    assert widget.rowCount() == 2
    assert _cell_text(widget, 0, 0) == "W1AW"
    assert _cell_text(widget, 1, 0) == "K1ABC"
    assert _cell_text(widget, 0, 6) == "CW"


def test_columns_are_fixed_and_reduced(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)

    assert widget.columnCount() == 7
    header_labels = [widget.horizontalHeaderItem(i).text() for i in range(7)]
    assert header_labels == [
        "CALL",
        "QSO_DATE",
        "TIME_ON",
        "RST_RCVD",
        "RST_SENT",
        "FREQ",
        "MODE",
    ]


def test_alternating_row_colors_enabled(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)

    assert widget.alternatingRowColors() is True


def test_edit_triggers_include_double_click(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)

    assert widget.editTriggers() & QTableWidget.EditTrigger.DoubleClicked


def test_append_qso_never_emits_edited(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    received: list[object] = []
    widget.edited.connect(lambda *args: received.append(args))

    widget.append_qso(_qso("W1AW", time(9, 0)))
    widget.append_qso(_qso("K1ABC", time(9, 2)))

    assert received == []


def test_editing_call_cell_uppercases_and_emits_edited(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    widget.show()
    widget.append_qso(_qso("W1AW", time(9, 0)))

    index = widget.model().index(0, 0)
    widget.edit(index)
    editor = widget.viewport().findChild(QLineEdit)
    assert editor is not None
    editor.clear()
    qtbot.keyClicks(editor, "k1abc")

    with qtbot.waitSignal(widget.edited) as blocker:
        qtbot.keyClick(editor, Qt.Key.Key_Return)

    row, request = blocker.args
    assert row == 0
    assert isinstance(request, EditQsoRequest)
    assert request.call == "K1ABC"
    assert _cell_text(widget, 0, 0) == "K1ABC"


def test_editing_mode_cell_only_offers_cw_and_ssb(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    widget.show()
    widget.append_qso(_qso("W1AW", time(9, 0)))

    index = widget.model().index(0, 6)
    widget.edit(index)
    editor = widget.viewport().findChild(QComboBox)

    assert editor is not None
    assert not editor.isEditable()
    assert [editor.itemText(i) for i in range(editor.count())] == ["CW", "SSB"]


def test_editing_time_on_cell_forces_zero_seconds_in_emitted_request(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    widget.show()
    widget.append_qso(_qso("W1AW", time(9, 0)))

    index = widget.model().index(0, 2)
    widget.edit(index)
    editor = widget.viewport().findChild(QTimeEdit)
    assert editor is not None
    editor.setTime(editor.time().addSecs(60 * 30 + 47))  # 09:30:47 if seconds survived

    with qtbot.waitSignal(widget.edited) as blocker:
        qtbot.keyClick(editor, Qt.Key.Key_Return)

    _, request = blocker.args
    assert request.time_on.second == 0
    assert _cell_text(widget, 0, 2) == "09:30:00"


def test_apply_edit_rewrites_the_row_and_updates_the_cache(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    widget.append_qso(_qso("W1AW", time(9, 0)))

    edited_qso = _qso("K1ABC", time(9, 2))
    widget.apply_edit(0, edited_qso)

    assert _cell_text(widget, 0, 0) == "K1ABC"
    assert _cell_text(widget, 0, 2) == "09:02:00"
    assert widget._qsos[0] == edited_qso


def test_revert_edit_restores_the_pre_edit_display(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    widget.append_qso(_qso("W1AW", time(9, 0)))

    item = widget.item(0, 0)
    assert item is not None
    item.setText("BOGUS")

    widget.revert_edit(0)

    assert _cell_text(widget, 0, 0) == "W1AW"
    assert widget._qsos[0].call == "W1AW"


def test_selection_is_row_based_and_single(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)

    assert widget.selectionBehavior() == QTableWidget.SelectionBehavior.SelectRows
    assert widget.selectionMode() == QTableWidget.SelectionMode.SingleSelection


def test_context_menu_policy_is_custom(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)

    assert widget.contextMenuPolicy() == Qt.ContextMenuPolicy.CustomContextMenu


def test_context_menu_on_a_row_selects_it_and_emits_delete_requested(
    qtbot: QtBot, monkeypatch: pytest.MonkeyPatch
) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    widget.append_qso(_qso("W1AW", time(9, 0)))
    delete_action_holder: list[object] = []
    original_add_action = QMenu.addAction

    def _capturing_add_action(self: QMenu, *args: object, **kwargs: object) -> object:
        action = original_add_action(self, *args, **kwargs)
        delete_action_holder.append(action)
        return action

    monkeypatch.setattr(QMenu, "addAction", _capturing_add_action)
    monkeypatch.setattr(QMenu, "exec", lambda self, *_args, **_kwargs: delete_action_holder[-1])

    with qtbot.waitSignal(widget.delete_requested) as blocker:
        widget._on_context_menu_requested(QPoint(0, widget.rowViewportPosition(0) + 1))

    assert blocker.args == [0]
    assert widget.currentRow() == 0


def test_context_menu_below_the_last_row_emits_nothing_and_keeps_selection(
    qtbot: QtBot,
) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    widget.append_qso(_qso("W1AW", time(9, 0)))
    received: list[object] = []
    widget.delete_requested.connect(lambda *args: received.append(args))

    widget._on_context_menu_requested(QPoint(0, widget.viewport().height() + 100))

    assert received == []
    assert widget.currentRow() == -1


def test_remove_row_drops_the_row_and_shifts_the_cache(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)
    widget.append_qso(_qso("W1AW", time(9, 0)))
    widget.append_qso(_qso("K1ABC", time(9, 2)))

    widget.remove_row(0)

    assert widget.rowCount() == 1
    assert _cell_text(widget, 0, 0) == "K1ABC"
    assert len(widget._qsos) == 1
    assert widget._qsos[0].call == "K1ABC"
