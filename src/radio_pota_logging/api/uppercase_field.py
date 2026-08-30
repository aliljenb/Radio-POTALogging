"""Makes a QLineEdit uppercase its text live as the operator types."""

from __future__ import annotations

from PyQt6.QtWidgets import QLineEdit


def uppercase_as_typed(line_edit: QLineEdit) -> None:
    """Uppercase `line_edit`'s text on every edit, preserving cursor position."""

    def _on_text_edited(text: str) -> None:
        cursor_position = line_edit.cursorPosition()
        line_edit.setText(text.upper())
        line_edit.setCursorPosition(cursor_position)

    line_edit.textEdited.connect(_on_text_edited)
