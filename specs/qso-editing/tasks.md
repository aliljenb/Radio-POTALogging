# Tasks: qso-editing

## Status

- [x] Draft
- [x] In Review
- [x] Approved

_All tasks through `composition_root.py`'s `EditQsoCommand` wiring (Stories
1-5, double-click-to-edit) were previously approved and are already
implemented. The Stories 6-7 tasks appended below (right-click-to-delete)
approved 2026-09-14._

## How to use this file

Each task must name the exact file(s) and function/class/method it creates
or changes, and cite the design.md section it implements. Vague tasks
("wire up the backend") are not allowed — split them until each one is a
single, independently completable unit of work with a clear file target.

## Domain Layer

`src/radio_pota_logging/domain/logging_session/`

- [x] `entities.py` — **modify** `LoggingSession`: implement `edit_qso(self,
      index: int, *, call: str, qso_date: date, time_on: time, mode: str,
      rst_sent: str, rst_rcvd: str, freq: str) -> Qso`. Reads `existing =
      self.qsos[index]`; calls `Frequency.parse(freq)` and accesses
      `.band` (raising `FrequencyFormatError`/`FrequencyOutOfBandError`
      before any state changes, exactly like `record_qso`); builds
      `timestamp = QsoTimestamp(qso_date=qso_date, time_on=time_on)`;
      constructs a new `Qso` with `call`/`timestamp`/`mode`/`rst_sent`/
      `rst_rcvd`/`freq=frequency` from the arguments and `my_sig`/
      `my_sig_info`/`operator`/`my_rig`/`tx_pwr` carried forward unchanged
      from `existing`; replaces `self.qsos` with `(*self.qsos[:index],
      edited, *self.qsos[index + 1:])`; returns the edited `Qso`. Does
      **not** touch `self.next_entry_defaults` at all per design.md §
      Aggregates, § Entities (updated invariant), § Domain Exceptions
      (no new exception — an out-of-range `index` raises the built-in
      `IndexError` from `self.qsos[index]`).
- [x] `entities.py` — **modify** `LoggingSession`: implement `delete_qso(self,
      index: int) -> None`. Does `qsos = list(self.qsos)`, `del
      qsos[index]` (raises the built-in `IndexError` for an out-of-range
      index, before any state changes), then `self.qsos = tuple(qsos)`.
      Deliberately implemented via a `list` copy and `del` rather than
      slice arithmetic (`(*self.qsos[:index], *self.qsos[index + 1:])`)
      specifically so an out-of-range `index` raises instead of silently
      clipping. Does **not** touch `self.next_entry_defaults` at all per
      design.md § Aggregates, § Entities (updated invariant), § Domain
      Exceptions (Stories 6-7 amendment).

## Application Layer

`src/radio_pota_logging/application/logging_session/`

- [x] `dto.py` — implement `EditQsoRequest` (`index: int, call: str,
      qso_date: date, time_on: time, mode: str, rst_sent: str, rst_rcvd:
      str, freq: str`) per design.md § DTOs
- [x] `dto.py` — implement `EditQsoResult` (`qso: QsoDto` — no
      `entry_defaults` field) per design.md § DTOs
- [x] `commands.py` — implement `EditQsoCommand` (`repository:
      LoggingSessionRepository`): `execute(self, request: EditQsoRequest)
      -> EditQsoResult` calls `_require_current_session(self.repository)`,
      then `session.edit_qso(request.index, call=request.call,
      qso_date=request.qso_date, time_on=request.time_on,
      mode=request.mode, rst_sent=request.rst_sent,
      rst_rcvd=request.rst_rcvd, freq=request.freq)` (propagating
      `FrequencyFormatError`/`FrequencyOutOfBandError`), then
      `self.repository.save(session)`, returning
      `EditQsoResult(qso=_to_qso_dto(qso))` — reusing the existing
      `_to_qso_dto` helper already defined in this file, per design.md §
      Commands and § DTOs
- [x] `dto.py` — implement `DeleteQsoRequest` (`index: int`) — no other
      fields per design.md § DTOs (Stories 6-7 amendment)
- [x] `commands.py` — implement `DeleteQsoCommand` (`repository:
      LoggingSessionRepository`): `execute(self, request:
      DeleteQsoRequest) -> None` calls
      `_require_current_session(self.repository)`, then
      `session.delete_qso(request.index)` (propagating the built-in
      `IndexError` for a caller bug — not a domain exception, and not
      caught here), then `self.repository.save(session)`, returning
      `None` — deliberately no `DeleteQsoResult`/return value, since there
      is nothing to hand back per design.md § Commands and § DTOs (Stories
      6-7 amendment)

## Infrastructure Layer

No tasks. Per design.md § Infrastructure, `LoggingSessionRepository.save()`
and `FileLoggingSessionRepository`/`_qso_to_dict`/`_qso_from_dict` need no
change — they already persist/round-trip whatever `session.qsos` currently
holds, whether it grew, had an entry replaced, or (per the Stories 6-7
amendment) had one removed.

## API Layer

`src/radio_pota_logging/api/` (PyQt desktop presentation layer)

- [x] `qso_table_delegates.py` — **new file**: implement
      `UppercaseCallDelegate(QStyledItemDelegate)`: `createEditor` returns
      a `QLineEdit` passed through the existing
      `uppercase_field.uppercase_as_typed()` helper; `setEditorData` sets
      the editor's text from `index.data()`; `setModelData` writes
      `editor.text()` back via `model.setData(index, ...,
      Qt.ItemDataRole.EditRole)` per design.md § Components (CALL column)
- [x] `qso_table_delegates.py` — implement
      `QsoDateDelegate(QStyledItemDelegate)`: `createEditor` returns a
      `QDateEdit` with `.setCalendarPopup(True)`; `setEditorData` parses
      `index.data()` via `date.fromisoformat(...)` into a `QDate` and sets
      it; `setModelData` reads the editor's `QDate`, converts it to a
      `datetime.date`, and writes `.isoformat()` back via `model.setData`
      per design.md § Components (QSO_DATE column)
- [x] `qso_table_delegates.py` — implement
      `TimeOnDelegate(QStyledItemDelegate)`: `createEditor` returns a
      `QTimeEdit` with `.setDisplayFormat("HH:mm")`; `setEditorData` parses
      `index.data()` via `time.fromisoformat(...)` into a `QTime` and sets
      it; `setModelData` reads the editor's `QTime`, forces the seconds
      component to `0`, and writes `time(hour, minute,
      0).isoformat()` back via `model.setData` per design.md § Components
      (TIME_ON column) and § Testing Strategy (zero-seconds convention
      enforced at the delegate too)
- [x] `qso_table_delegates.py` — implement
      `ModeDelegate(QStyledItemDelegate)`: `createEditor` returns a
      non-editable `QComboBox` populated via `.addItems(MODE_OPTIONS)`
      (imported from `application/logging_session/dto.py`);
      `setEditorData` sets `editor.setCurrentText(index.data())`;
      `setModelData` writes `editor.currentText()` back via
      `model.setData` per design.md § Components (MODE column)
- [x] `qso_list_widget.py` — **modify** `QsoListWidget`: add module-level
      column-index constants derived from `_COLUMNS.index(...)` for
      `"CALL"`, `"QSO_DATE"`, `"TIME_ON"`, `"FREQ"`, `"MODE"` and use them
      both for delegate registration below and inside `_on_cell_changed`
      per design.md § Components
- [x] `qso_list_widget.py` — **modify** `QsoListWidget.__init__`: change
      `self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)` to
      `QTableWidget.EditTrigger.DoubleClicked`; register
      `UppercaseCallDelegate`, `QsoDateDelegate`, `TimeOnDelegate`, and
      `ModeDelegate` on their respective columns via
      `self.setItemDelegateForColumn(column, delegate)` (RST_RCVD,
      RST_SENT, FREQ register no delegate, per design.md § Components);
      add `self._qsos: list[QsoDto] = []`; add a new signal `edited =
      pyqtSignal(int, EditQsoRequest)` at class scope; connect
      `self.cellChanged.connect(self._on_cell_changed)` per design.md §
      Components ("QsoListWidget's edit-commit mechanism" points 1–3)
- [x] `qso_list_widget.py` — **modify**: extract a private `_write_row(self,
      row: int, qso: QsoDto) -> None` from `append_qso`'s existing
      `values`/`setItem` loop, wrapping the 7 `setItem` calls in
      `self.blockSignals(True)` / `self.blockSignals(False)` so writing a
      row's cells never itself fires `cellChanged`; `append_qso` now
      appends `qso` to `self._qsos` and calls `_write_row(row, qso)` per
      design.md § Components point 1
- [x] `qso_list_widget.py` — implement `_on_cell_changed(self, row: int,
      column: int) -> None`: reads `self.item(row, column).text()`, parses
      it to the right type for that column (`date.fromisoformat`/
      `time.fromisoformat` for QSO_DATE/TIME_ON, a plain string
      otherwise), builds an `EditQsoRequest` combining that new value with
      the other 6 fields read from `self._qsos[row]` (the still-unedited
      cached `QsoDto`), and emits `self.edited.emit(row, request)` per
      design.md § Components point 4
- [x] `qso_list_widget.py` — implement `apply_edit(self, row: int, qso:
      QsoDto) -> None`: sets `self._qsos[row] = qso` then calls
      `self._write_row(row, qso)` per design.md § Components
- [x] `qso_list_widget.py` — implement `revert_edit(self, row: int) ->
      None`: calls `self._write_row(row, self._qsos[row])` (re-rendering
      the row from its unchanged, pre-edit cache entry) per design.md §
      Components
- [x] `qso_entry_controller.py` — **modify**
      `QsoEntryController.__init__`: add an `edit_command: EditQsoCommand`
      parameter, store it as `self._edit_command`, and connect
      `qso_list.edited.connect(self._on_qso_edited)` per design.md §
      Components
- [x] `qso_entry_controller.py` — implement `_on_qso_edited(self, row:
      int, request: EditQsoRequest) -> None`: calls
      `self._edit_command.execute(request)` inside a `try`; on
      `FrequencyFormatError`/`FrequencyOutOfBandError`, calls
      `self._form.show_error(str(exc))` then
      `self._qso_list.revert_edit(row)` and returns; on success, calls
      `self._form.clear_error()` then `self._qso_list.apply_edit(row,
      result.qso)` per design.md § Components (code block under "API
      Layer" / `QsoEntryController._on_qso_edited`)
- [x] `main_window.py` — **modify** `MainWindow.__init__`: add an
      `edit_qso: EditQsoCommand` parameter and pass it as
      `edit_command=edit_qso` into the `QsoEntryController(...)`
      construction, alongside the existing `submit_command`/
      `generate_adif_command`/`suggest_adif_filename_command` per
      design.md § Components
- [x] `composition_root.py` — **modify** `main()`: construct
      `EditQsoCommand(repository)` alongside the existing
      `SubmitQsoCommand(repository)` and pass it as `edit_qso=` into the
      `MainWindow(...)` construction per design.md § Components

### Stories 6-7 (right-click-to-delete)

- [ ] `qso_list_widget.py` — **modify** `QsoListWidget.__init__`: add
      `self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)`
      and
      `self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)`;
      add `self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)`
      and connect
      `self.customContextMenuRequested.connect(self._on_context_menu_requested)`;
      add a new signal `delete_requested = pyqtSignal(int)` at class scope
      per design.md § Components ("right-click-to-delete mechanism" points
      1-2)
- [ ] `qso_list_widget.py` — implement `_on_context_menu_requested(self,
      pos: QPoint) -> None`: computes `row = self.rowAt(pos.y())`; returns
      immediately if `row < 0`; otherwise calls `self.selectRow(row)`,
      builds a `QMenu(self)` with one `"Delete"` action, calls
      `menu.exec(self.viewport().mapToGlobal(pos))`, and — if the chosen
      action is the `"Delete"` one — emits `self.delete_requested.emit(row)`
      per design.md § Components point 3
- [ ] `qso_list_widget.py` — implement `remove_row(self, row: int) ->
      None`: `del self._qsos[row]` then `self.removeRow(row)` — no
      `blockSignals` guard needed, since `removeRow` emits `rowsRemoved`,
      not `cellChanged` per design.md § Components point 4
- [ ] `qso_entry_controller.py` — **modify**
      `QsoEntryController.__init__`: add a `delete_command:
      DeleteQsoCommand` parameter, store it as `self._delete_command`, and
      connect `qso_list.delete_requested.connect(self._on_delete_requested)`
      per design.md § Components
- [ ] `qso_entry_controller.py` — implement `_on_delete_requested(self,
      row: int) -> None`: shows
      `QMessageBox.question(self._dialog_parent, "Delete QSO", "Delete
      this QSO?", QMessageBox.StandardButton.Yes |
      QMessageBox.StandardButton.No)`; returns immediately if the answer
      isn't `Yes`; otherwise calls
      `self._delete_command.execute(DeleteQsoRequest(index=row))` then
      `self._qso_list.remove_row(row)` — no `try/except`, since an
      `IndexError` here is a caller bug, not a recoverable business
      failure per design.md § Components (code block
      `QsoEntryController._on_delete_requested`)
- [ ] `main_window.py` — **modify** `MainWindow.__init__`: add a
      `delete_qso: DeleteQsoCommand` parameter and pass it as
      `delete_command=delete_qso` into the `QsoEntryController(...)`
      construction, alongside the existing `submit_command`/
      `edit_command`/`generate_adif_command`/`suggest_adif_filename_command`
      per design.md § Components
- [ ] `composition_root.py` — **modify** `main()`: construct
      `DeleteQsoCommand(repository)` alongside the existing
      `SubmitQsoCommand(repository)`/`EditQsoCommand(repository)` and pass
      it as `delete_qso=` into the `MainWindow(...)` construction per
      design.md § Components

## Frontend

N/A — this project has no `frontend/src`; see design.md § API Layer.

## Tests

`tests/` mirrors `src/radio_pota_logging/`.

- [x] `tests/domain/logging_session/test_entities.py` — **add** tests for
      `LoggingSession.edit_qso`: editing `call` on a two-QSO session
      replaces only `qsos[0].call` (uppercased, per `Qso.__post_init__`)
      and leaves `qsos[1]` and `next_entry_defaults` unchanged (the direct
      regression test for requirements.md Story 5); editing `freq` updates
      `qsos[index].band` to match the new frequency; editing `time_on`
      updates `qsos[index].time_off` (the derived property) to match; an
      invalid `freq` (`FrequencyFormatError` for unparsable text,
      `FrequencyOutOfBandError` for a value outside every band-plan row)
      raised from `edit_qso` leaves `session.qsos` completely unchanged at
      that index per design.md § Testing Strategy
- [x] `tests/application/logging_session/test_commands.py` — **add** tests
      for `EditQsoCommand`: executing a valid `EditQsoRequest` against a
      fake repository seeded with one QSO returns an `EditQsoResult` whose
      `.qso` reflects the edit, calls the fake repository's `save()`
      exactly once, and leaves the fake session's `next_entry_defaults`
      object identity unchanged; a `FrequencyFormatError` from an invalid
      `freq` propagates out of `execute()` without `save()` being called
      per design.md § Testing Strategy
- [x] `tests/infrastructure/repositories/test_file_logging_session_repository.py`
      — **add** a test: saving a session after calling `edit_qso` and
      reloading it via `find_unfinished()` round-trips the edited QSO's
      values correctly per design.md § Testing Strategy
- [x] `tests/api/test_qso_table_delegates.py` — **new file**: unit tests
      for `UppercaseCallDelegate`, `QsoDateDelegate`, `TimeOnDelegate`, and
      `ModeDelegate`: each delegate's `createEditor` returns the expected
      widget type (and, for `ModeDelegate`, that the `QComboBox` offers
      exactly `["CW", "SSB"]` and is not editable); `setEditorData` given a
      model index whose text is e.g. `"2026-09-07"` sets the `QDateEdit`'s
      date to the matching `QDate`; `setModelData` given an edited
      `QTimeEdit` showing `14:12` writes back `"14:12:00"` per design.md §
      Testing Strategy
- [x] `tests/api/test_qso_list_widget.py` — **add** tests: constructing
      `QsoListWidget` and reading `.editTriggers()` includes
      `QTableWidget.EditTrigger.DoubleClicked`; calling `append_qso` twice
      never emits `edited` (the regression test for the `blockSignals`
      guard in `_write_row`); opening the CALL column's editor via
      `widget.edit(widget.model().index(row, 0))`, typing lowercase text,
      and committing it results in the cell displaying uppercase and
      `edited` firing with an uppercase `EditQsoRequest.call` (via
      `qtbot.waitSignal(widget.edited)`); the same sequence on the MODE
      column's editor only ever offers `["CW", "SSB"]`; committing a
      TIME_ON edit results in the emitted `EditQsoRequest.time_on` having
      `.second == 0`; `apply_edit(0, a_qso_dto)` rewrites row 0's 7 cells
      to match `a_qso_dto` and updates `widget._qsos[0]`; mutating row 0's
      displayed text directly and then calling `revert_edit(0)` restores
      the original text (proving revert reads from the pre-edit cache, not
      from whatever's currently displayed) per design.md § Testing
      Strategy
- [x] `tests/api/test_qso_entry_controller.py` — **add**: a
      `FakeEditQsoCommand` test double (mirroring the existing
      `FakeSubmitQsoCommand` in this file, with an `executed_with`
      attribute and an optional `raises` exception); extend
      `_make_controller` to accept and pass through an `edit_command`
      parameter (defaulting to a `FakeEditQsoCommand()`); a test asserting
      that emitting `qso_list.edited` with a valid `EditQsoRequest` calls
      `qso_list.apply_edit(row, result.qso)` and clears
      `form._error_label`; a test asserting that a `FakeEditQsoCommand`
      raising `FrequencyOutOfBandError` results in
      `form._error_label.isVisible()` and the row being reverted (assert
      the cell text equals its pre-edit value) per design.md § Testing
      Strategy
- [x] `tests/api/test_main_window.py` — **modify**: add a
      `FakeEditQsoCommand` test double (mirroring
      `FakeSubmitQsoCommand`/`FakeGenerateAdifCommand` in this file) and
      pass `edit_qso=FakeEditQsoCommand()` into each of the three existing
      `MainWindow(...)` construction call sites
      (`test_main_window_renders_the_given_session_start_result`,
      `test_main_window_renders_an_empty_qso_list_for_a_brand_new_session`,
      `test_main_window_sizes_itself_to_half_width_and_three_quarters_height`)
      — mechanical fallout of `MainWindow.__init__`'s new required
      parameter, not a design deviation

### Stories 6-7 (right-click-to-delete)

- [x] `tests/domain/logging_session/test_entities.py` — **add** tests for
      `LoggingSession.delete_qso`: deleting index 0 on a two-QSO session
      removes `qsos[0]` and leaves the former `qsos[1]` as the new
      `qsos[0]` (order preserved, not just count reduced);
      `next_entry_defaults` object identity is unchanged (the Story 7
      regression test); deleting the only remaining QSO leaves
      `session.qsos == ()`; an out-of-range index raises `IndexError` and
      leaves `session.qsos` unchanged per design.md § Testing Strategy
      ("Stories 6-7 additions")
- [x] `tests/application/logging_session/test_commands.py` — **add** tests
      for `DeleteQsoCommand`: executing `DeleteQsoRequest(index=0)` against
      a fake repository seeded with two QSOs removes the first, calls the
      fake repository's `save()` exactly once, and returns `None`; the
      fake session's `next_entry_defaults` object identity is unchanged
      per design.md § Testing Strategy
- [ ] `tests/api/test_qso_list_widget.py` — **add** tests:
      `widget.selectionBehavior() == QTableWidget.SelectionBehavior.SelectRows`
      and `widget.selectionMode() ==
      QTableWidget.SelectionMode.SingleSelection`;
      `widget.contextMenuPolicy() == Qt.ContextMenuPolicy.CustomContextMenu`;
      calling `_on_context_menu_requested` with a point inside row 0
      selects row 0 and emits `delete_requested` with `0` (simulating the
      menu's "Delete" action being chosen, e.g. by monkeypatching
      `QMenu.exec`); calling it with a point below the last row emits
      nothing and leaves the selection unchanged; `remove_row(0)` on a
      two-row table drops row 0, leaves the former row 1's values as the
      new row 0's, and shrinks `widget._qsos` to length 1 per design.md §
      Testing Strategy
- [ ] `tests/api/test_qso_entry_controller.py` — **add**: a
      `FakeDeleteQsoCommand` test double (mirroring `FakeEditQsoCommand`
      in this file, with an `executed_with` attribute); extend
      `_make_controller` to accept and pass through a `delete_command`
      parameter (defaulting to a `FakeDeleteQsoCommand()`); with
      `QMessageBox.question` monkeypatched to return
      `QMessageBox.StandardButton.Yes`, a test asserting that emitting
      `qso_list.delete_requested` with a row number calls the fake
      command with a matching `DeleteQsoRequest` and calls
      `qso_list.remove_row` with that row (via `monkeypatch.setattr` on
      the widget instance or an equivalent call-recording double); with it
      monkeypatched to return `QMessageBox.StandardButton.No`, a test
      asserting that emitting the same signal calls neither the fake
      command nor `remove_row` per design.md § Testing Strategy
- [ ] `tests/api/test_main_window.py` — **modify**: add a
      `FakeDeleteQsoCommand` test double (mirroring `FakeEditQsoCommand`/
      `FakeSubmitQsoCommand` in this file) and pass
      `delete_qso=FakeDeleteQsoCommand()` into each of the three existing
      `MainWindow(...)` construction call sites — mechanical fallout of
      `MainWindow.__init__`'s new required parameter, not a design
      deviation

## Task Dependencies

- Domain Layer's `edit_qso` task has no dependency on any other Domain
  Layer file — it only calls existing `Frequency`/`QsoTimestamp`/`Qso`
  constructors already implemented by qso-entering.
- Application Layer tasks depend on the Domain Layer task (`EditQsoCommand`
  calls `LoggingSession.edit_qso`); `dto.py`'s `EditQsoRequest`/
  `EditQsoResult` before `commands.py`'s `EditQsoCommand` (which returns/
  consumes them).
- API Layer tasks depend on the Application Layer's `EditQsoCommand`/
  `EditQsoRequest`/`EditQsoResult`. Within API Layer: `qso_table_delegates.py`
  (leaf module, no dependency on the other API changes) and the
  `qso_list_widget.py` column-index-constants/`__init__` tasks before the
  `qso_list_widget.py` `_write_row`/`_on_cell_changed`/`apply_edit`/
  `revert_edit` tasks (which the `__init__` changes wire up); all
  `qso_list_widget.py` tasks before `qso_entry_controller.py` (connects to
  `QsoListWidget.edited`); `qso_entry_controller.py` before
  `main_window.py` (passes the new `edit_command` through); `main_window.py`
  before `composition_root.py` (constructs and passes `EditQsoCommand` into
  `MainWindow`).
- Each test task depends on the implementation task(s) it covers, per the
  file each test task names above.

### Stories 6-7 (right-click-to-delete)

- Domain Layer's `delete_qso` task has no dependency on `edit_qso` or any
  other Domain Layer file — it only operates on `self.qsos`.
- Application Layer's `DeleteQsoRequest` (`dto.py`) before `DeleteQsoCommand`
  (`commands.py`), same ordering reason as `EditQsoRequest`/`EditQsoCommand`;
  `DeleteQsoCommand` depends on the Domain Layer's `delete_qso` task.
- API Layer: the `qso_list_widget.py` `__init__` task (selection
  mode/context menu policy/`delete_requested` signal) before
  `_on_context_menu_requested` and `remove_row` (which it wires up); all
  three `qso_list_widget.py` tasks before `qso_entry_controller.py`'s two
  tasks (connects to `QsoListWidget.delete_requested`, calls
  `remove_row`); `qso_entry_controller.py` before `main_window.py` (passes
  the new `delete_command` through); `main_window.py` before
  `composition_root.py` (constructs and passes `DeleteQsoCommand` into
  `MainWindow`). These tasks have no ordering dependency on the Stories 1-5
  API tasks beyond both needing `qso_list_widget.py`/`qso_entry_controller.py`
  to already exist (which they do).
- Each Stories 6-7 test task depends on the implementation task(s) it
  covers, per the file each test task names above.
