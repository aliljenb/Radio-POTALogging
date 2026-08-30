from datetime import date, time

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QPushButton
from pytestqt.qtbot import QtBot
from radio_pota_logging.api.qso_entry_form_widget import QsoEntryFormWidget
from radio_pota_logging.application.logging_session.dto import EntryDefaultsDto, SubmitQsoRequest


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
    assert widget._mode.text() == "CW"
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


def test_show_error_then_clear_error(qtbot: QtBot) -> None:
    widget = QsoEntryFormWidget()
    qtbot.addWidget(widget)
    widget.show()

    widget.show_error("out of band")
    assert widget._error_label.isVisible()
    assert widget._error_label.text() == "out of band"

    widget.clear_error()
    assert not widget._error_label.isVisible()
