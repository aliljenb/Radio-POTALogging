from datetime import UTC, date, datetime, time

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialogButtonBox, QPushButton
from pytestqt.qtbot import QtBot
from radio_pota_logging.api.session_setup_dialog import SessionSetupDialog, SessionSetupResult


def _button(dialog: SessionSetupDialog, text: str) -> QPushButton:
    box = dialog.findChild(QDialogButtonBox)
    assert box is not None
    for button in box.findChildren(QPushButton):
        if button.text() == text:
            return button
    raise AssertionError(f"no button labelled {text!r}")


def test_ok_disabled_until_park_reference_and_freq_are_non_empty(qtbot: QtBot) -> None:
    dialog = SessionSetupDialog()
    qtbot.addWidget(dialog)
    ok_button = _button(dialog, "OK")

    assert not ok_button.isEnabled()

    qtbot.keyClicks(dialog._park_reference, "K-1234")
    assert not ok_button.isEnabled()

    qtbot.keyClicks(dialog._freq, "14.062")
    assert ok_button.isEnabled()

    dialog._park_reference.setText("")
    assert not ok_button.isEnabled()


def test_ok_disabled_with_freq_but_empty_park_reference(qtbot: QtBot) -> None:
    dialog = SessionSetupDialog()
    qtbot.addWidget(dialog)
    ok_button = _button(dialog, "OK")

    qtbot.keyClicks(dialog._freq, "14.062")

    assert not ok_button.isEnabled()


def test_clicking_ok_sets_result_from_entered_values(qtbot: QtBot) -> None:
    now = datetime(2026, 8, 30, 9, 0, 0, tzinfo=UTC)
    dialog = SessionSetupDialog(now=now)
    qtbot.addWidget(dialog)
    qtbot.keyClicks(dialog._park_reference, "K-1234")
    qtbot.keyClicks(dialog._freq, "14.062")

    qtbot.mouseClick(_button(dialog, "OK"), Qt.MouseButton.LeftButton)

    assert dialog.setup_result == SessionSetupResult(
        park_reference="K-1234", qso_date=date(2026, 8, 30), time_on=time(9, 0), freq="14.062"
    )


def test_typing_lowercase_into_park_reference_displays_uppercase(qtbot: QtBot) -> None:
    dialog = SessionSetupDialog()
    qtbot.addWidget(dialog)

    qtbot.keyClicks(dialog._park_reference, "k-1234")

    assert dialog._park_reference.text() == "K-1234"


def test_dialog_prefills_date_and_time_from_now(qtbot: QtBot) -> None:
    now = datetime(2026, 8, 30, 14, 30, 0, tzinfo=UTC)
    dialog = SessionSetupDialog(now=now)
    qtbot.addWidget(dialog)

    assert dialog._qso_date.date().toPyDate() == date(2026, 8, 30)
    assert dialog._time_on.time().toPyTime() == time(14, 30, 0)


def test_clicking_quit_leaves_result_none(qtbot: QtBot) -> None:
    dialog = SessionSetupDialog()
    qtbot.addWidget(dialog)
    qtbot.keyClicks(dialog._park_reference, "K-1234")
    qtbot.keyClicks(dialog._freq, "14.062")

    qtbot.mouseClick(_button(dialog, "Quit"), Qt.MouseButton.LeftButton)

    assert dialog.setup_result is None
