from datetime import date, time
from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot
from radio_pota_logging.api import main_window as main_window_module
from radio_pota_logging.api.main_window import MainWindow
from radio_pota_logging.api.session_resume_prompt_dialog import SessionResumeChoice
from radio_pota_logging.application.logging_session.dto import (
    EntryDefaultsDto,
    SessionStartResult,
    SubmitQsoResult,
)


def _entry_defaults() -> EntryDefaultsDto:
    return EntryDefaultsDto(
        operator="SM6Y",
        mode="CW",
        my_sig_info="",
        rst_sent="599",
        rst_rcvd="599",
        freq="",
        my_rig="Elecraft KX2",
        tx_pwr="5",
        qso_date=date(2026, 8, 30),
        time_on=time(9, 0),
    )


class FakeCheckForResumableSessionQuery:
    def __init__(self, value: bool) -> None:
        self._value = value

    def execute(self) -> bool:
        return self._value


class FakeResumeSessionCommand:
    def __init__(self) -> None:
        self.executed = False

    def execute(self) -> SessionStartResult:
        self.executed = True
        return SessionStartResult(entry_defaults=_entry_defaults(), qsos=())


class FakeStartNewSessionCommand:
    def __init__(self) -> None:
        self.executed = False
        self.called_with: tuple[date, time] | None = None

    def execute(self, *, qso_date: date, time_on: time) -> SessionStartResult:
        self.executed = True
        self.called_with = (qso_date, time_on)
        return SessionStartResult(entry_defaults=_entry_defaults(), qsos=())


class FakeSubmitQsoCommand:
    def execute(self, request: object) -> SubmitQsoResult:  # pragma: no cover - unused here
        raise NotImplementedError


class FakeGenerateAdifCommand:
    def execute(self, destination: Path) -> None:  # pragma: no cover - unused here
        raise NotImplementedError


def _build_window(
    qtbot: QtBot,
    check: FakeCheckForResumableSessionQuery,
    resume: FakeResumeSessionCommand,
    start_new: FakeStartNewSessionCommand,
) -> MainWindow:
    window = MainWindow(
        check_for_resumable_session=check,  # type: ignore[arg-type]
        resume_session=resume,  # type: ignore[arg-type]
        start_new_session=start_new,  # type: ignore[arg-type]
        submit_qso=FakeSubmitQsoCommand(),  # type: ignore[arg-type]
        generate_adif=FakeGenerateAdifCommand(),  # type: ignore[arg-type]
    )
    qtbot.addWidget(window)
    return window


def test_no_prompt_and_starts_clean_when_no_resumable_session(
    qtbot: QtBot, monkeypatch: pytest.MonkeyPatch
) -> None:
    exec_calls = []
    monkeypatch.setattr(
        main_window_module.SessionResumePromptDialog, "exec", lambda self: exec_calls.append(1)
    )
    resume = FakeResumeSessionCommand()
    start_new = FakeStartNewSessionCommand()

    _build_window(qtbot, FakeCheckForResumableSessionQuery(False), resume, start_new)

    assert exec_calls == []
    assert start_new.executed
    assert not resume.executed


def test_prompt_shown_and_resume_invoked_when_resume_chosen(
    qtbot: QtBot, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_exec(self: object) -> int:
        self.choice = SessionResumeChoice.RESUME  # type: ignore[attr-defined]
        return 0

    monkeypatch.setattr(main_window_module.SessionResumePromptDialog, "exec", fake_exec)
    resume = FakeResumeSessionCommand()
    start_new = FakeStartNewSessionCommand()

    _build_window(qtbot, FakeCheckForResumableSessionQuery(True), resume, start_new)

    assert resume.executed
    assert not start_new.executed


def test_prompt_shown_and_start_clean_invoked_when_start_clean_chosen(
    qtbot: QtBot, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_exec(self: object) -> int:
        self.choice = SessionResumeChoice.START_CLEAN  # type: ignore[attr-defined]
        return 0

    monkeypatch.setattr(main_window_module.SessionResumePromptDialog, "exec", fake_exec)
    resume = FakeResumeSessionCommand()
    start_new = FakeStartNewSessionCommand()

    _build_window(qtbot, FakeCheckForResumableSessionQuery(True), resume, start_new)

    assert start_new.executed
    assert not resume.executed
