"""Wires the entry form and Generate ADIF action to their application commands."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget

from radio_pota_logging.application.logging_session.commands import (
    DeleteQsoCommand,
    EditQsoCommand,
    GenerateAdifCommand,
    SubmitQsoCommand,
)
from radio_pota_logging.application.logging_session.dto import (
    DeleteQsoRequest,
    EditQsoRequest,
    SubmitQsoRequest,
)
from radio_pota_logging.application.logging_session.queries import SuggestAdifFilenameQuery
from radio_pota_logging.domain.logging_session.exceptions import (
    FrequencyFormatError,
    FrequencyOutOfBandError,
)

from .qso_entry_form_widget import QsoEntryFormWidget
from .qso_list_widget import QsoListWidget


class QsoEntryController:
    """Mediates between the form/list widgets and the application commands."""

    def __init__(
        self,
        form: QsoEntryFormWidget,
        qso_list: QsoListWidget,
        submit_command: SubmitQsoCommand,
        edit_command: EditQsoCommand,
        delete_command: DeleteQsoCommand,
        generate_adif_command: GenerateAdifCommand,
        suggest_adif_filename_command: SuggestAdifFilenameQuery,
        dialog_parent: QWidget,
    ) -> None:
        self._form = form
        self._qso_list = qso_list
        self._submit_command = submit_command
        self._edit_command = edit_command
        self._delete_command = delete_command
        self._generate_adif_command = generate_adif_command
        self._suggest_adif_filename_command = suggest_adif_filename_command
        self._dialog_parent = dialog_parent
        form.submitted.connect(self._on_submit)
        qso_list.edited.connect(self._on_qso_edited)
        qso_list.delete_requested.connect(self._on_delete_requested)

    def _on_submit(self, request: SubmitQsoRequest) -> None:
        try:
            result = self._submit_command.execute(request)
        except (FrequencyFormatError, FrequencyOutOfBandError) as exc:
            self._form.show_error(str(exc))
            return
        self._form.clear_error()
        self._qso_list.append_qso(result.submitted)
        self._form.apply_defaults(result.entry_defaults)

    def _on_qso_edited(self, row: int, request: EditQsoRequest) -> None:
        try:
            result = self._edit_command.execute(request)
        except (FrequencyFormatError, FrequencyOutOfBandError) as exc:
            self._form.show_error(str(exc))
            self._qso_list.revert_edit(row)
            return
        self._form.clear_error()
        self._qso_list.apply_edit(row, result.qso)

    def _on_delete_requested(self, row: int) -> None:
        confirmed = (
            QMessageBox.question(
                self._dialog_parent,
                "Delete QSO",
                "Delete this QSO?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        )
        if not confirmed:
            return
        self._delete_command.execute(DeleteQsoRequest(index=row))
        self._qso_list.remove_row(row)

    def generate_adif(self) -> None:
        suggested_filename = self._suggest_adif_filename_command.execute()
        destination_text, _ = QFileDialog.getSaveFileName(
            self._dialog_parent, "Generate ADIF", suggested_filename, "ADIF files (*.adi)"
        )
        if not destination_text:
            return
        self._generate_adif_command.execute(Path(destination_text))
