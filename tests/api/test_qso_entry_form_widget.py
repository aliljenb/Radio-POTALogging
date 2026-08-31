from datetime import date, time

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QFormLayout, QPushButton, QWidget
from pytestqt.qtbot import QtBot
from radio_pota_logging.api.qso_entry_form_widget import QsoEntryFormWidget
from radio_pota_logging.application.logging_session.dto import (
    MODE_OPTIONS,
    EntryDefaultsDto,
    SubmitQsoRequest,
)


def _defaults() -> EntryDefaultsDto:
    return EntryDefaultsDto(
        operator="SM6Y",
        mode="CW",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="14.062",
        my_rig="Elecraft KX2",
        tx_pwr="5",
        qso_date=date(2026, 8, 30),
        time_on=time(9, 0),
    )


def test_apply_defaults_prefills_fields_and_focuses_call(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitExposed(widget)
    widget.activateWindow()
    QApplication.processEvents()

    widget.apply_defaults(_defaults())
    QApplication.processEvents()

    assert widget._call.text() == ""
    assert widget._mode.currentText() == "CW"
    assert widget._my_sig_info.text() == "K-1234"
    assert widget._freq.text() == "14.062"
    assert widget._operator.text() == "SM6Y"
    assert widget._call.hasFocus()


def test_submit_button_emits_request_with_typed_values(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)
    widget.apply_defaults(_defaults())
    widget._call.setText("W1AW")
    submit_button = widget.findChildren(QPushButton)[0]

    with qtbot.waitSignal(widget.submitted, timeout=1000) as blocker:
        qtbot.mouseClick(submit_button, Qt.MouseButton.LeftButton)

    request: SubmitQsoRequest = blocker.args[0]
    assert request.call == "W1AW"
    assert request.freq == "14.062"
    assert request.qso_date == date(2026, 8, 30)
    assert request.time_on == time(9, 0)


def test_typing_lowercase_into_call_displays_uppercase(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)
    widget.show()

    qtbot.keyClicks(widget._call, "w1aw/p")

    assert widget._call.text() == "W1AW/P"


def test_typing_lowercase_into_my_sig_info_displays_uppercase(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)
    widget.show()

    qtbot.keyClicks(widget._my_sig_info, "k-1234")

    assert widget._my_sig_info.text() == "K-1234"


def test_typing_lowercase_into_operator_displays_uppercase(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)
    widget.show()

    qtbot.keyClicks(widget._operator, "sm6y")

    assert widget._operator.text() == "SM6Y"


def test_mode_combo_box_offers_exactly_cw_and_ssb_and_is_not_editable(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)

    items = [widget._mode.itemText(i) for i in range(widget._mode.count())]

    assert items == list(MODE_OPTIONS)
    assert not widget._mode.isEditable()


def test_apply_defaults_sets_mode_combo_box_to_given_value(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)

    widget.apply_defaults(
        EntryDefaultsDto(
            operator="SM6Y",
            mode="SSB",
            my_sig_info="K-1234",
            rst_sent="599",
            rst_rcvd="599",
            freq="14.062",
            my_rig="Elecraft KX2",
            tx_pwr="5",
            qso_date=date(2026, 8, 30),
            time_on=time(9, 0),
        )
    )

    assert widget._mode.currentText() == "SSB"


def test_submit_includes_selected_mode(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)
    widget.apply_defaults(_defaults())
    widget._call.setText("W1AW")
    widget._mode.setCurrentText("SSB")
    submit_button = widget.findChildren(QPushButton)[0]

    with qtbot.waitSignal(widget.submitted, timeout=1000) as blocker:
        qtbot.mouseClick(submit_button, Qt.MouseButton.LeftButton)

    request: SubmitQsoRequest = blocker.args[0]
    assert request.mode == "SSB"


def test_enter_in_a_non_call_field_submits_when_call_is_non_empty(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)
    widget.show()
    widget.apply_defaults(_defaults())
    widget._call.setText("W1AW")
    widget._my_rig.setFocus()

    with qtbot.waitSignal(widget.submitted, timeout=1000) as blocker:
        qtbot.keyClick(widget._my_rig, Qt.Key.Key_Return)

    request: SubmitQsoRequest = blocker.args[0]
    assert request.call == "W1AW"


def test_enter_in_call_submits_when_call_is_non_empty(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)
    widget.show()
    widget.apply_defaults(_defaults())
    widget._call.setText("W1AW")
    widget._call.setFocus()

    with qtbot.waitSignal(widget.submitted, timeout=1000) as blocker:
        qtbot.keyClick(widget._call, Qt.Key.Key_Return)

    request: SubmitQsoRequest = blocker.args[0]
    assert request.call == "W1AW"


def test_enter_in_call_does_nothing_when_call_is_empty(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)
    widget.show()
    widget.apply_defaults(_defaults())
    widget._call.setFocus()

    with qtbot.waitSignal(widget.submitted, timeout=200, raising=False) as blocker:
        qtbot.keyClick(widget._call, Qt.Key.Key_Return)

    assert not blocker.signal_triggered


def _row_labels(column: QFormLayout, row_count: int) -> list[str]:
    return [
        column.itemAt(i, QFormLayout.ItemRole.LabelRole).widget().text()  # type: ignore[union-attr]
        for i in range(row_count)
    ]


def test_fields_are_displayed_in_the_fixed_column_order(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)

    assert _row_labels(widget._column_1, 4) == ["CALL", "RST_RCVD", "RST_SENT", "TIME_ON"]
    assert _row_labels(widget._column_2, 4) == ["FREQ", "MY_SIG_INFO", "QSO_DATE", "MODE"]
    assert _row_labels(widget._column_3, 3) == ["OPERATOR", "MY_RIG", "TX_PWR"]


def test_tab_order_follows_the_fixed_field_order(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)

    expected = [
        widget._call,
        widget._rst_rcvd,
        widget._rst_sent,
        widget._time_on,
        widget._freq,
        widget._my_sig_info,
        widget._qso_date,
        widget._mode,
        widget._operator,
        widget._my_rig,
        widget._tx_pwr,
    ]

    visited = []
    current: QWidget | None = widget._call
    for _ in range(100):
        assert current is not None
        current = current.nextInFocusChain()
        if current in expected:
            visited.append(current)
        if len(visited) == len(expected) - 1:
            break

    assert visited == expected[1:]


def test_mode_change_updates_rst_sent_and_rst_rcvd_to_the_new_mode_default(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)
    widget.apply_defaults(_defaults())
    assert widget._rst_sent.text() == "599"
    assert widget._rst_rcvd.text() == "599"

    widget._mode.setCurrentText("SSB")
    assert widget._rst_sent.text() == "59"
    assert widget._rst_rcvd.text() == "59"

    widget._mode.setCurrentText("CW")
    assert widget._rst_sent.text() == "599"
    assert widget._rst_rcvd.text() == "599"


def test_mode_change_leaves_a_manually_edited_rst_field_unchanged(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)
    widget.apply_defaults(_defaults())

    widget._rst_sent.setText("579")
    widget._mode.setCurrentText("SSB")

    assert widget._rst_sent.text() == "579"
    assert widget._rst_rcvd.text() == "59"


def test_time_on_display_format_hides_seconds(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)

    assert widget._time_on.displayFormat() == "HH:mm"


def test_submitted_time_on_always_has_zero_seconds(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)
    widget.apply_defaults(_defaults())
    widget._call.setText("W1AW")
    submit_button = widget.findChildren(QPushButton)[0]

    with qtbot.waitSignal(widget.submitted, timeout=1000) as blocker:
        qtbot.mouseClick(submit_button, Qt.MouseButton.LeftButton)

    request: SubmitQsoRequest = blocker.args[0]
    assert request.time_on.second == 0


def test_show_error_then_clear_error(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)
    widget.show()

    widget.show_error("out of band")
    assert widget._error_label.isVisible()
    assert widget._error_label.text() == "out of band"

    widget.clear_error()
    assert not widget._error_label.isVisible()
