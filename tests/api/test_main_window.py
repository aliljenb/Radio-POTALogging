from datetime import date, time
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot
from radio_pota_logging.api.main_window import MainWindow
from radio_pota_logging.application.logging_session.dto import (
    EntryDefaultsDto,
    QsoDto,
    SessionStartResult,
)


class FakeSubmitQsoCommand:
    def execute(self, request: object) -> object:  # pragma: no cover - unused here
        raise NotImplementedError


class FakeGenerateAdifCommand:
    def execute(self, destination: Path) -> None:  # pragma: no cover - unused here
        raise NotImplementedError


class FakeSuggestAdifFilenameQuery:
    def execute(self) -> str:  # pragma: no cover - unused here
        raise NotImplementedError


def _entry_defaults() -> EntryDefaultsDto:
    return EntryDefaultsDto(
        operator="SM6Y",
        mode="CW",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="",
        my_rig="Elecraft KX2",
        tx_pwr="5",
        qso_date=date(2026, 8, 30),
        time_on=time(9, 0),
    )


def _qso_dto() -> QsoDto:
    return QsoDto(
        call="W1AW",
        qso_date=date(2026, 8, 30),
        time_on=time(9, 0),
        time_off=time(9, 0),
        band="20M",
        mode="CW",
        my_sig="POTA",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="14.062",
        operator="SM6Y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )


def test_main_window_renders_the_given_session_start_result(qtbot: QtBot) -> None:
    initial_result = SessionStartResult(entry_defaults=_entry_defaults(), qsos=(_qso_dto(),))

    window = MainWindow(
        initial_result=initial_result,
        submit_qso=FakeSubmitQsoCommand(),  # type: ignore[arg-type]
        generate_adif=FakeGenerateAdifCommand(),  # type: ignore[arg-type]
        suggest_adif_filename=FakeSuggestAdifFilenameQuery(),  # type: ignore[arg-type]
    )
    qtbot.addWidget(window)

    assert window.qso_list.rowCount() == 1
    assert window.form._my_sig_info.text() == "K-1234"


def test_main_window_renders_an_empty_qso_list_for_a_brand_new_session(qtbot: QtBot) -> None:
    initial_result = SessionStartResult(entry_defaults=_entry_defaults(), qsos=())

    window = MainWindow(
        initial_result=initial_result,
        submit_qso=FakeSubmitQsoCommand(),  # type: ignore[arg-type]
        generate_adif=FakeGenerateAdifCommand(),  # type: ignore[arg-type]
        suggest_adif_filename=FakeSuggestAdifFilenameQuery(),  # type: ignore[arg-type]
    )
    qtbot.addWidget(window)

    assert window.qso_list.rowCount() == 0


def test_main_window_sizes_itself_to_half_width_and_three_quarters_height(qtbot: QtBot) -> None:
    initial_result = SessionStartResult(entry_defaults=_entry_defaults(), qsos=())

    window = MainWindow(
        initial_result=initial_result,
        submit_qso=FakeSubmitQsoCommand(),  # type: ignore[arg-type]
        generate_adif=FakeGenerateAdifCommand(),  # type: ignore[arg-type]
        suggest_adif_filename=FakeSuggestAdifFilenameQuery(),  # type: ignore[arg-type]
    )
    qtbot.addWidget(window)

    screen = QApplication.primaryScreen()
    assert screen is not None
    geometry = screen.availableGeometry()
    assert window.size().width() == geometry.width() // 2
    assert window.size().height() == geometry.height() * 3 // 4
