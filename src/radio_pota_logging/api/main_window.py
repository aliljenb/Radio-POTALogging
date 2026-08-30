"""Hosts the entry form, QSO list, and Generate ADIF action."""

from __future__ import annotations

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

from radio_pota_logging.application.logging_session.commands import (
    GenerateAdifCommand,
    SubmitQsoCommand,
)
from radio_pota_logging.application.logging_session.dto import SessionStartResult

from .qso_entry_controller import QsoEntryController
from .qso_entry_form_widget import QsoEntryFormWidget
from .qso_list_widget import QsoListWidget


class MainWindow(QMainWindow):
    """Top-level window; renders the SessionStartResult it's given at construction."""

    def __init__(
        self,
        initial_result: SessionStartResult,
        submit_qso: SubmitQsoCommand,
        generate_adif: GenerateAdifCommand,
    ) -> None:
        super().__init__()
        self.setWindowTitle("POTA QSO Logging")

        self.form = QsoEntryFormWidget()
        self.qso_list = QsoListWidget()
        generate_adif_button = QPushButton("Generate ADIF")

        self.controller = QsoEntryController(
            form=self.form,
            qso_list=self.qso_list,
            submit_command=submit_qso,
            generate_adif_command=generate_adif,
            dialog_parent=self,
        )
        generate_adif_button.clicked.connect(self.controller.generate_adif)

        central = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.qso_list)
        layout.addWidget(self.form)
        layout.addWidget(generate_adif_button)
        central.setLayout(layout)
        self.setCentralWidget(central)

        self._apply_session_start_result(initial_result)

        screen = QApplication.primaryScreen()
        if screen is not None:
            geometry = screen.availableGeometry()
            self.resize(geometry.width() // 2, geometry.height() * 3 // 4)

    def _apply_session_start_result(self, result: SessionStartResult) -> None:
        for qso in result.qsos:
            self.qso_list.append_qso(qso)
        self.form.apply_defaults(result.entry_defaults)
