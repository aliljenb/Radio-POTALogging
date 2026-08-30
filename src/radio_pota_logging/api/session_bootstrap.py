"""Decides how (or whether) the session starts, before any window exists."""

from __future__ import annotations

from radio_pota_logging.application.logging_session.commands import (
    ResumeSessionCommand,
    StartNewSessionCommand,
)
from radio_pota_logging.application.logging_session.dto import SessionStartResult
from radio_pota_logging.application.logging_session.queries import CheckForResumableSessionQuery

from .session_resume_prompt_dialog import SessionResumeChoice, SessionResumePromptDialog
from .session_setup_dialog import SessionSetupDialog


def bootstrap_session(
    check_for_resumable_session: CheckForResumableSessionQuery,
    resume_session: ResumeSessionCommand,
    start_new_session: StartNewSessionCommand,
) -> SessionStartResult | None:
    """Run the resume prompt (if applicable) and/or the new-session setup dialog.

    Returns None if the operator chose to quit on the setup dialog.
    """
    if check_for_resumable_session.execute():
        resume_dialog = SessionResumePromptDialog()
        resume_dialog.exec()
        if resume_dialog.choice == SessionResumeChoice.RESUME:
            return resume_session.execute()

    setup_dialog = SessionSetupDialog()
    setup_dialog.exec()
    if setup_dialog.setup_result is None:
        return None

    return start_new_session.execute(
        qso_date=setup_dialog.setup_result.qso_date,
        time_on=setup_dialog.setup_result.time_on,
        park_reference=setup_dialog.setup_result.park_reference,
        freq=setup_dialog.setup_result.freq,
    )
