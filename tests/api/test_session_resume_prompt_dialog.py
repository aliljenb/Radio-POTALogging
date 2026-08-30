from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialogButtonBox, QPushButton
from pytestqt.qtbot import QtBot
from radio_pota_logging.api.session_resume_prompt_dialog import (
    SessionResumeChoice,
    SessionResumePromptDialog,
)


def _button(dialog: SessionResumePromptDialog, text: str) -> QPushButton:
    box = dialog.findChild(QDialogButtonBox)
    assert box is not None
    for button in box.findChildren(QPushButton):
        if button.text() == text:
            return button
    raise AssertionError(f"no button labelled {text!r}")


def test_clicking_resume_sets_choice_to_resume(qtbot: QtBot) -> None:
    dialog = SessionResumePromptDialog()
    qtbot.addWidget(dialog)

    qtbot.mouseClick(_button(dialog, "Resume"), Qt.MouseButton.LeftButton)

    assert dialog.choice == SessionResumeChoice.RESUME


def test_clicking_start_clean_sets_choice_to_start_clean(qtbot: QtBot) -> None:
    dialog = SessionResumePromptDialog()
    qtbot.addWidget(dialog)

    qtbot.mouseClick(_button(dialog, "Start Clean"), Qt.MouseButton.LeftButton)

    assert dialog.choice == SessionResumeChoice.START_CLEAN
