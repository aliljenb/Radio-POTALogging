from datetime import date, time
from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot
from radio_pota_logging.api import qso_entry_controller as controller_module
from radio_pota_logging.api.qso_entry_controller import QsoEntryController
from radio_pota_logging.api.qso_entry_form_widget import QsoEntryFormWidget
from radio_pota_logging.api.qso_list_widget import QsoListWidget
from radio_pota_logging.application.logging_session.dto import (
    EntryDefaultsDto,
    QsoDto,
    SubmitQsoRequest,
    SubmitQsoResult,
)
from radio_pota_logging.domain.logging_session.exceptions import FrequencyOutOfBandError


def _entry_defaults() -> EntryDefaultsDto:
    return EntryDefaultsDto(
        operator="SM6Y",
        mode="CW",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="14.062",
        my_rig="Elecraft KX2",
        tx_pwr="5",
        qso_date=date(2026, 8, 30),
        time_on=time(9, 2),
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


class FakeSubmitQsoCommand:
    def __init__(self, *, raises: Exception | None = None) -> None:
        self._raises = raises
        self.executed_with: object = None

    def execute(self, request: object) -> SubmitQsoResult:
        self.executed_with = request
        if self._raises is not None:
            raise self._raises
        return SubmitQsoResult(entry_defaults=_entry_defaults(), submitted=_qso_dto())


class FakeGenerateAdifCommand:
    def __init__(self) -> None:
        self.executed_with: Path | None = None

    def execute(self, destination: Path) -> None:
        self.executed_with = destination


def _make_controller(
    qtbot: QtBot, submit_command: object, generate_adif_command: object
) -> tuple[QsoEntryController, QsoEntryFormWidget, QsoListWidget]:
    form = QsoEntryFormWidget()
    qso_list = QsoListWidget()
    qtbot.addWidget(form)
    qtbot.addWidget(qso_list)
    form.show()
    controller = QsoEntryController(
        form=form,
        qso_list=qso_list,
        submit_command=submit_command,  # type: ignore[arg-type]
        generate_adif_command=generate_adif_command,  # type: ignore[arg-type]
        dialog_parent=form,
    )
    return controller, form, qso_list


def test_successful_submit_appends_to_list_and_reapplies_defaults(qtbot: QtBot) -> None:
    submit_command = FakeSubmitQsoCommand()
    _, form, qso_list = _make_controller(qtbot, submit_command, FakeGenerateAdifCommand())

    form._call.setText("W1AW")
    request = SubmitQsoRequest(
        call="W1AW",
        qso_date=date(2026, 8, 30),
        time_on=time(9, 0),
        mode="CW",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="14.062",
        operator="SM6Y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )
    form.submitted.emit(request)

    assert qso_list.rowCount() == 1
    assert form._freq.text() == "14.062"
    assert not form._error_label.isVisible()


def test_failed_submit_shows_inline_error_and_preserves_form(qtbot: QtBot) -> None:
    submit_command = FakeSubmitQsoCommand(raises=FrequencyOutOfBandError("5.000 MHz"))
    _, form, qso_list = _make_controller(qtbot, submit_command, FakeGenerateAdifCommand())

    form._call.setText("W1AW")
    form._freq.setText("5.000")
    request = SubmitQsoRequest(
        call="W1AW",
        qso_date=date(2026, 8, 30),
        time_on=time(9, 0),
        mode="CW",
        my_sig_info="K-1234",
        rst_sent="599",
        rst_rcvd="599",
        freq="5.000",
        operator="SM6Y",
        my_rig="Elecraft KX2",
        tx_pwr="5",
    )

    form.submitted.emit(request)

    assert qso_list.rowCount() == 0
    assert form._error_label.isVisible()
    assert form._call.text() == "W1AW"
    assert form._freq.text() == "5.000"


def test_generate_adif_invokes_command_with_chosen_destination(
    qtbot: QtBot, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    destination = tmp_path / "out.adi"
    monkeypatch.setattr(
        controller_module.QFileDialog,
        "getSaveFileName",
        classmethod(lambda *_args, **_kwargs: (str(destination), "")),
    )
    generate_adif_command = FakeGenerateAdifCommand()
    controller, _, _ = _make_controller(qtbot, FakeSubmitQsoCommand(), generate_adif_command)

    controller.generate_adif()

    assert generate_adif_command.executed_with == destination


def test_generate_adif_does_nothing_when_dialog_is_cancelled(
    qtbot: QtBot, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        controller_module.QFileDialog,
        "getSaveFileName",
        classmethod(lambda *_args, **_kwargs: ("", "")),
    )
    generate_adif_command = FakeGenerateAdifCommand()
    controller, _, _ = _make_controller(qtbot, FakeSubmitQsoCommand(), generate_adif_command)

    controller.generate_adif()

    assert generate_adif_command.executed_with is None
