from PyQt6.QtWidgets import QLineEdit
from pytestqt.qtbot import QtBot
from radio_pota_logging.api.uppercase_field import uppercase_as_typed


def test_typing_lowercase_displays_uppercase(qtbot: QtBot) -> None:
    line_edit = QLineEdit()
    qtbot.addWidget(line_edit)
    uppercase_as_typed(line_edit)

    qtbot.keyClicks(line_edit, "w1aw/p")

    assert line_edit.text() == "W1AW/P"


def test_cursor_position_preserved_after_mid_string_edit(qtbot: QtBot) -> None:
    line_edit = QLineEdit()
    qtbot.addWidget(line_edit)
    uppercase_as_typed(line_edit)

    qtbot.keyClicks(line_edit, "waw")
    line_edit.setCursorPosition(1)
    qtbot.keyClicks(line_edit, "1")

    assert line_edit.text() == "W1AW"
    assert line_edit.cursorPosition() == 2
