from datetime import date, time

from pytestqt.qtbot import QtBot
from radio_pota_logging.api.qso_list_widget import QsoListWidget
from radio_pota_logging.application.logging_session.dto import QsoDto


def _qso(call: str, time_on: time) -> QsoDto:
    return QsoDto(
        call=call,
        qso_date=date(2026, 8, 30),
        time_on=time_on,
        time_off=time_on,
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


def _cell_text(widget: QsoListWidget, row: int, column: int) -> str:
    item = widget.item(row, column)
    assert item is not None
    return item.text()


def test_append_qso_adds_rows_in_order(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)

    widget.append_qso(_qso("W1AW", time(9, 0)))
    widget.append_qso(_qso("K1ABC", time(9, 2)))

    assert widget.rowCount() == 2
    assert _cell_text(widget, 0, 0) == "W1AW"
    assert _cell_text(widget, 1, 0) == "K1ABC"
    assert _cell_text(widget, 0, 6) == "CW"


def test_columns_are_fixed_and_reduced(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)

    assert widget.columnCount() == 7
    header_labels = [widget.horizontalHeaderItem(i).text() for i in range(7)]
    assert header_labels == [
        "CALL",
        "QSO_DATE",
        "TIME_ON",
        "RST_RCVD",
        "RST_SENT",
        "FREQ",
        "MODE",
    ]


def test_alternating_row_colors_enabled(qtbot: QtBot) -> None:
    widget = QsoListWidget()
    qtbot.addWidget(widget)

    assert widget.alternatingRowColors() is True
