"""Asks the operator, once at startup, to resume or start clean."""

from __future__ import annotations

from enum import Enum, auto

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QWidget


class SessionResumeChoice(Enum):
    RESUME = auto()
    START_CLEAN = auto()


class SessionResumePromptDialog(QDialog):
    """Modal choice between resuming the previous session and starting clean."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Resume previous session?")
        self.choice = SessionResumeChoice.START_CLEAN

        label = QLabel(
            "An unfinished QSO logging session was found.\n"
            "Resume it, or start a new, clean session?"
        )
        buttons = QDialogButtonBox()
        resume_button = buttons.addButton("Resume", QDialogButtonBox.ButtonRole.AcceptRole)
        start_clean_button = buttons.addButton(
            "Start Clean", QDialogButtonBox.ButtonRole.DestructiveRole
        )
        assert resume_button is not None
        assert start_clean_button is not None
        resume_button.clicked.connect(self._choose_resume)
        start_clean_button.clicked.connect(self._choose_start_clean)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _choose_resume(self) -> None:
        self.choice = SessionResumeChoice.RESUME
        self.accept()

    def _choose_start_clean(self) -> None:
        self.choice = SessionResumeChoice.START_CLEAN
        self.accept()
