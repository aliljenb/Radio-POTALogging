from datetime import date, time

import pytest
from pytestqt.qtbot import QtBot
from radio_pota_logging.api import session_bootstrap as session_bootstrap_module
from radio_pota_logging.api.session_bootstrap import bootstrap_session
from radio_pota_logging.api.session_resume_prompt_dialog import SessionResumeChoice
from radio_pota_logging.api.session_setup_dialog import SessionSetupResult
from radio_pota_logging.application.logging_session.dto import EntryDefaultsDto, SessionStartResult


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
        self.called_with: dict[str, object] | None = None

    def execute(
        self,
        *,
        qso_date: date,
        time_on: time,
        park_reference: str,
        freq: str,
        operator: str,
        mode: str,
        my_rig: str,
        tx_pwr: str,
    ) -> SessionStartResult:
        self.executed = True
        self.called_with = {
            "qso_date": qso_date,
            "time_on": time_on,
            "park_reference": park_reference,
            "freq": freq,
            "operator": operator,
            "mode": mode,
            "my_rig": my_rig,
            "tx_pwr": tx_pwr,
        }
        return SessionStartResult(entry_defaults=_entry_defaults(), qsos=())


class _FakeSetupDialogWithResult:
    def __init__(self) -> None:
        self.setup_result: SessionSetupResult | None = SessionSetupResult(
            park_reference="K-1234",
            qso_date=date(2026, 8, 30),
            time_on=time(9, 0),
            freq="14.062",
            operator="W1AW",
            my_rig="FT-891",
            tx_pwr="10",
            mode="SSB",
        )

    def exec(self) -> int:
        return 0


class _FakeSetupDialogQuit:
    def __init__(self) -> None:
        self.setup_result: SessionSetupResult | None = None

    def exec(self) -> int:
        return 0


def _fake_resume_dialog(choice: SessionResumeChoice) -> type:
    class _FakeResumeDialog:
        def __init__(self) -> None:
            self.choice = choice

        def exec(self) -> int:
            return 0

    return _FakeResumeDialog


def test_no_resumable_session_shows_setup_dialog_and_starts_new_session(
    qtbot: QtBot, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(session_bootstrap_module, "SessionSetupDialog", _FakeSetupDialogWithResult)
    resume = FakeResumeSessionCommand()
    start_new = FakeStartNewSessionCommand()

    result = bootstrap_session(
        FakeCheckForResumableSessionQuery(False),  # type: ignore[arg-type]
        resume,  # type: ignore[arg-type]
        start_new,  # type: ignore[arg-type]
    )

    assert result is not None
    assert start_new.executed
    assert start_new.called_with == {
        "qso_date": date(2026, 8, 30),
        "time_on": time(9, 0),
        "park_reference": "K-1234",
        "freq": "14.062",
        "operator": "W1AW",
        "mode": "SSB",
        "my_rig": "FT-891",
        "tx_pwr": "10",
    }
    assert not resume.executed


def test_resume_chosen_runs_resume_command_without_setup_dialog(
    qtbot: QtBot, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        session_bootstrap_module,
        "SessionResumePromptDialog",
        _fake_resume_dialog(SessionResumeChoice.RESUME),
    )

    def _fail_if_constructed() -> None:
        raise AssertionError("SessionSetupDialog should not be constructed on Resume")

    monkeypatch.setattr(
        session_bootstrap_module,
        "SessionSetupDialog",
        lambda: _fail_if_constructed(),
    )
    resume = FakeResumeSessionCommand()
    start_new = FakeStartNewSessionCommand()

    result = bootstrap_session(
        FakeCheckForResumableSessionQuery(True),  # type: ignore[arg-type]
        resume,  # type: ignore[arg-type]
        start_new,  # type: ignore[arg-type]
    )

    assert result is not None
    assert resume.executed
    assert not start_new.executed


def test_start_clean_chosen_shows_setup_dialog_then_starts_new_session(
    qtbot: QtBot, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        session_bootstrap_module,
        "SessionResumePromptDialog",
        _fake_resume_dialog(SessionResumeChoice.START_CLEAN),
    )
    monkeypatch.setattr(session_bootstrap_module, "SessionSetupDialog", _FakeSetupDialogWithResult)
    resume = FakeResumeSessionCommand()
    start_new = FakeStartNewSessionCommand()

    result = bootstrap_session(
        FakeCheckForResumableSessionQuery(True),  # type: ignore[arg-type]
        resume,  # type: ignore[arg-type]
        start_new,  # type: ignore[arg-type]
    )

    assert result is not None
    assert start_new.executed
    assert not resume.executed


def test_quit_on_setup_dialog_returns_none_and_runs_no_command(
    qtbot: QtBot, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(session_bootstrap_module, "SessionSetupDialog", _FakeSetupDialogQuit)
    resume = FakeResumeSessionCommand()
    start_new = FakeStartNewSessionCommand()

    result = bootstrap_session(
        FakeCheckForResumableSessionQuery(False),  # type: ignore[arg-type]
        resume,  # type: ignore[arg-type]
        start_new,  # type: ignore[arg-type]
    )

    assert result is None
    assert not resume.executed
    assert not start_new.executed
