"""Assembles the object graph and runs the application."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from radio_pota_logging.application.logging_session.commands import (
    GenerateAdifCommand,
    ResumeSessionCommand,
    StartNewSessionCommand,
    SubmitQsoCommand,
)
from radio_pota_logging.application.logging_session.queries import CheckForResumableSessionQuery
from radio_pota_logging.infrastructure.adif.adif_file_exporter import AdifFileExporter
from radio_pota_logging.infrastructure.repositories.file_logging_session_repository import (
    FileLoggingSessionRepository,
)

from .main_window import MainWindow


def main() -> int:
    repository = FileLoggingSessionRepository(Path.cwd())
    exporter = AdifFileExporter()

    app = QApplication(sys.argv)
    window = MainWindow(
        check_for_resumable_session=CheckForResumableSessionQuery(repository),
        resume_session=ResumeSessionCommand(repository),
        start_new_session=StartNewSessionCommand(repository),
        submit_qso=SubmitQsoCommand(repository),
        generate_adif=GenerateAdifCommand(repository, exporter),
    )
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
