"""Wires the entry form and Generate ADIF action to their application commands."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QWidget

from radio_pota_logging.application.logging_session.commands import (
    GenerateAdifCommand,
    SubmitQsoCommand,
)
from radio_pota_logging.application.logging_session.dto import SubmitQsoRequest
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
        generate_adif_command: GenerateAdifCommand,
        dialog_parent: QWidget,
    ) -> None:
        self._form = form
        self._qso_list = qso_list
        self._submit_command = submit_command
        self._generate_adif_command = generate_adif_command
        self._dialog_parent = dialog_parent
        form.submitted.connect(self._on_submit)

    def _on_submit(self, request: SubmitQsoRequest) -> None:
        try:
            result = self._submit_command.execute(request)
        except (FrequencyFormatError, FrequencyOutOfBandError) as exc:
            self._form.show_error(str(exc))
            return
        self._form.clear_error()
        self._qso_list.append_qso(result.submitted)
        self._form.apply_defaults(result.entry_defaults)

    def generate_adif(self) -> None:
        destination_text, _ = QFileDialog.getSaveFileName(
            self._dialog_parent, "Generate ADIF", "", "ADIF files (*.adi)"
        )
        if not destination_text:
            return
        self._generate_adif_command.execute(Path(destination_text))
