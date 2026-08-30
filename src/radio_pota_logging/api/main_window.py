"""Hosts the entry form, QSO list, and Generate ADIF action; runs the startup flow."""

from __future__ import annotations

from datetime import UTC, datetime

from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget

from radio_pota_logging.application.logging_session.commands import (
    GenerateAdifCommand,
    ResumeSessionCommand,
    StartNewSessionCommand,
    SubmitQsoCommand,
)
from radio_pota_logging.application.logging_session.dto import SessionStartResult
from radio_pota_logging.application.logging_session.queries import CheckForResumableSessionQuery

from .qso_entry_controller import QsoEntryController
from .qso_entry_form_widget import QsoEntryFormWidget
from .qso_list_widget import QsoListWidget
from .session_resume_prompt_dialog import SessionResumeChoice, SessionResumePromptDialog


class MainWindow(QMainWindow):
    """Top-level window; owns the startup resume/start-clean flow."""

    def __init__(
        self,
        check_for_resumable_session: CheckForResumableSessionQuery,
        resume_session: ResumeSessionCommand,
        start_new_session: StartNewSessionCommand,
        submit_qso: SubmitQsoCommand,
        generate_adif: GenerateAdifCommand,
    ) -> None:
        super().__init__()
        self.setWindowTitle("POTA QSO Logging")

        self._start_new_session = start_new_session

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

        self._run_startup_flow(check_for_resumable_session, resume_session)

    def _run_startup_flow(
        self,
        check_for_resumable_session: CheckForResumableSessionQuery,
        resume_session: ResumeSessionCommand,
    ) -> None:
        if check_for_resumable_session.execute():
            dialog = SessionResumePromptDialog(self)
            dialog.exec()
            if dialog.choice == SessionResumeChoice.RESUME:
                self._apply_session_start_result(resume_session.execute())
                return
        self._start_fresh_session()

    def _start_fresh_session(self) -> None:
        now = datetime.now(UTC)
        result = self._start_new_session.execute(qso_date=now.date(), time_on=now.time())
        self._apply_session_start_result(result)

    def _apply_session_start_result(self, result: SessionStartResult) -> None:
        for qso in result.qsos:
            self.qso_list.append_qso(qso)
        self.form.apply_defaults(result.entry_defaults)
