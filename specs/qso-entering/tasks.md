# Tasks: qso-entering

## Status

- [x] Draft
- [x] In Review
- [x] Approved

## How to use this file

Each task must name the exact file(s) and function/class/method it creates
or changes, and cite the design.md section it implements. Vague tasks
("wire up the backend") are not allowed — split them until each one is a
single, independently completable unit of work with a clear file target.

## Domain Layer

`src/radio_pota_logging/domain/logging_session/`

- [x] `exceptions.py` — implement `FrequencyFormatError` and
      `FrequencyOutOfBandError` per design.md § Domain Exceptions
- [x] `value_objects.py` — implement `SessionId` (wraps a UUID) per
      design.md § Value Objects
- [x] `value_objects.py` — implement `Band` (the 10 fixed designators
      `160M`…`6M`) per design.md § Value Objects
- [x] `value_objects.py` — implement `Frequency` (parses a decimal-MHz
      string, raises `FrequencyFormatError`; `.band` property derives
      `Band` via the adif-generation feature's requirements Story 1
      band-plan table, raising `FrequencyOutOfBandError` on no match) per
      design.md § Value Objects
- [x] `value_objects.py` — implement `QsoTimestamp` (`qso_date`, `time_on`;
      `.plus_two_minutes()` using `datetime` arithmetic for midnight
      rollover) per design.md § Value Objects
- [x] `value_objects.py` — implement `StationDefaults` (fixed constants:
      operator `SM6Y`, mode `CW`, my_sig `POTA`, rst_sent/rst_rcvd `599`,
      my_rig `Elecraft KX2`, tx_pwr `5`) per design.md § Value Objects
- [x] `value_objects.py` — implement `EntryDefaults`, including
      `EntryDefaults.seed(station_defaults, now)` per design.md § Value
      Objects
- [x] `value_objects.py` — **modify** `EntryDefaults.seed`: add a
      `my_sig_info: str = ""` parameter and use it (instead of the
      hardcoded `""`) as the constructed `EntryDefaults.my_sig_info` per
      design.md § Value Objects, Story 6 amendment.
- [x] `value_objects.py` — **modify** `EntryDefaults.seed`: add a
      `freq: str = ""` parameter and use it (instead of the hardcoded
      `""`) as the constructed `EntryDefaults.freq` per design.md § Value
      Objects, Story 6 Frequency extension.
- [x] `value_objects.py` — **modify** `EntryDefaults`: add a new
      `__post_init__` that normalizes `my_sig_info` to uppercase
      (`object.__setattr__(self, "my_sig_info",
      self.my_sig_info.upper())`, since the dataclass is frozen) per
      design.md § Value Objects, Story 7 amendment. This is a genuinely
      new method — `EntryDefaults` had no `__post_init__` before — needed
      because `LoggingSession.record_qso` carries `next_entry_defaults`
      forward from the raw `my_sig_info` parameter, not from
      `qso.my_sig_info`, so `Qso`'s own normalization doesn't cover it.
- [x] `value_objects.py` — **modify** `EntryDefaults.__post_init__`: also
      normalize `operator` to uppercase (`object.__setattr__(self,
      "operator", self.operator.upper())`, alongside the existing
      `my_sig_info` normalization) per design.md § Value Objects, Story 8
      amendment.
- [x] `value_objects.py` — implement `Qso` (immutable; `time_off` reads as
      `timestamp.time_on`; `band` reads as `freq.band`) per design.md §
      Value Objects
- [x] `value_objects.py` — **modify** `Qso`: add `__post_init__` that
      normalizes `call` to uppercase (`object.__setattr__(self, "call",
      self.call.upper())`, since the dataclass is frozen) per design.md §
      Value Objects, Story 5 amendment. Runs for every `Qso`, including
      ones deserialized from a persisted session file.
- [x] `value_objects.py` — **modify** `Qso.__post_init__`: also normalize
      `my_sig_info` to uppercase (`object.__setattr__(self, "my_sig_info",
      self.my_sig_info.upper())`, alongside the existing `call`
      normalization) per design.md § Value Objects, Story 7 amendment.
      Runs for every `Qso`, including ones deserialized from a persisted
      session file.
- [x] `value_objects.py` — **modify** `Qso.__post_init__`: also normalize
      `operator` to uppercase (`object.__setattr__(self, "operator",
      self.operator.upper())`, alongside the existing `call`/`my_sig_info`
      normalization) per design.md § Value Objects, Story 8 amendment.
      Runs for every `Qso`, including ones deserialized from a persisted
      session file.
- [x] `value_objects.py` — **new**: add a module-level constant
      `MODE_OPTIONS: tuple[str, str] = ("CW", "SSB")` per design.md §
      Value Objects, Story 9 amendment — the single source of truth for
      which MODE values exist.
- [x] `entities.py` — implement `LoggingSession` entity: `LoggingSession.start(station_defaults,
      now)` classmethod (seeds `next_entry_defaults`, empty `qsos`) and
      `record_qso(...)` method (constructs `Frequency`/`QsoTimestamp`,
      appends the new `Qso`, recomputes `next_entry_defaults` carrying
      every field forward except CALL) per design.md § Entities
- [x] `entities.py` — **modify** `LoggingSession.start`: add a
      `my_sig_info: str = ""` parameter and pass it through to
      `EntryDefaults.seed(station_defaults, now, my_sig_info=my_sig_info)`
      per design.md § Commands (`StartNewSessionCommand` row), Story 6
      amendment.
- [x] `entities.py` — **modify** `LoggingSession.start`: add a
      `freq: str = ""` parameter and pass it through to
      `EntryDefaults.seed(station_defaults, now, my_sig_info=my_sig_info,
      freq=freq)` per design.md § Commands (`StartNewSessionCommand` row),
      Story 6 Frequency extension.
- [x] `entities.py` — **modify** `LoggingSession.record_qso`: in the
      `next_entry_defaults = EntryDefaults(...)` construction, change
      `rst_sent=rst_sent, rst_rcvd=rst_rcvd` to
      `rst_sent=StationDefaults.rst_sent, rst_rcvd=StationDefaults.rst_rcvd`
      — the same class-level-constant pattern already used for `my_sig` on
      the `Qso` construction two lines above — per design.md § Overview
      (Story 2 RST reset amendment) and § Value Objects (`EntryDefaults`
      row). The `Qso` construction itself is unchanged; only the carried-
      forward defaults stop reusing the submitted `rst_sent`/`rst_rcvd`
      values.
- [x] `repository.py` — define `LoggingSessionRepository` protocol:
      `find_unfinished() -> LoggingSession | None`, `save(session) ->
      None`, `archive(session) -> None` per design.md § Repository
      Interfaces (ports)
- [x] `exporter.py` — define `AdifExporter` protocol: `export(qsos:
      Sequence[Qso]) -> str` per design.md § Repository Interfaces (ports)
- [x] `value_objects.py` — **modify** `QsoTimestamp`: add `__post_init__`
      that normalizes `time_on` to zero seconds/microseconds
      unconditionally (`object.__setattr__(self, "time_on",
      self.time_on.replace(second=0, microsecond=0))`, since the dataclass
      is frozen) per design.md § Value Objects, Story 14 amendment. Runs
      for every `QsoTimestamp`, including ones deserialized from a
      persisted session file, produced by `.plus_two_minutes()`, or built
      from `datetime.now()`.
- [x] `value_objects.py` — **new**: add a module-level function
      `default_rst_for_mode(mode: str) -> str` (`{"CW": "599", "SSB":
      "59"}[mode]`), defined next to `MODE_OPTIONS` per design.md § Value
      Objects, Story 13 amendment — the single source of truth for the
      MODE-dependent RST default.
- [x] `value_objects.py` — **modify** `StationDefaults`: remove the
      `rst_sent: str = "599"` and `rst_rcvd: str = "599"` fields — RST is
      no longer a fixed constant per design.md § Value Objects, Story 13
      amendment.
- [x] `value_objects.py` — **modify** `EntryDefaults.seed`: change
      `rst_sent=station_defaults.rst_sent,
      rst_rcvd=station_defaults.rst_rcvd` to
      `rst_sent=default_rst_for_mode(station_defaults.mode),
      rst_rcvd=default_rst_for_mode(station_defaults.mode)` per design.md
      § Value Objects, Story 13 amendment.
- [x] `entities.py` — **modify** `LoggingSession.record_qso`: in the
      `next_entry_defaults = EntryDefaults(...)` construction, change
      `rst_sent=StationDefaults.rst_sent,
      rst_rcvd=StationDefaults.rst_rcvd` to
      `rst_sent=default_rst_for_mode(mode), rst_rcvd=default_rst_for_mode(mode)`
      (the `mode` parameter `record_qso` was called with — the
      just-submitted QSO's MODE, already carried forward verbatim) per
      design.md § Overview (Story 13 amendment) and § Value Objects.

## Application Layer

`src/radio_pota_logging/application/logging_session/`

- [x] `dto.py` — implement `SubmitQsoRequest` per design.md § DTOs
- [x] `dto.py` — implement `EntryDefaultsDto` per design.md § DTOs
- [x] `dto.py` — implement `QsoDto` per design.md § DTOs
- [x] `dto.py` — implement `SessionStartResult` per design.md § DTOs
- [x] `dto.py` — implement `SubmitQsoResult` per design.md § DTOs
- [x] `dto.py` — implement `AdifExportResult` per design.md § DTOs
- [x] `queries.py` — implement `CheckForResumableSessionQuery` (calls
      `LoggingSessionRepository.find_unfinished()`, returns `bool`) per
      design.md § Queries
- [x] `commands.py` — implement `ResumeSessionCommand` per design.md §
      Commands
- [x] `commands.py` — implement `StartNewSessionCommand` (archives any
      unfinished session first) per design.md § Commands
- [x] `commands.py` — **modify** `StartNewSessionCommand.execute`: add a
      required keyword-only `park_reference: str` parameter and pass it to
      `LoggingSession.start(StationDefaults(), QsoTimestamp(qso_date,
      time_on), my_sig_info=park_reference)` per design.md § Commands,
      Story 6 amendment.
- [x] `commands.py` — **modify** `StartNewSessionCommand.execute`: add a
      required keyword-only `freq: str` parameter and pass it to
      `LoggingSession.start(StationDefaults(), QsoTimestamp(qso_date,
      time_on), my_sig_info=park_reference, freq=freq)` per design.md §
      Commands, Story 6 Frequency extension.
- [x] `commands.py` — implement `SubmitQsoCommand` (calls
      `LoggingSession.record_qso`, saves via repository; propagates
      `FrequencyFormatError`/`FrequencyOutOfBandError`) per design.md §
      Commands
- [x] `commands.py` — implement `GenerateAdifCommand` (reads current
      session, calls `AdifExporter.export()`, writes the result to the
      given `destination` path, returns `AdifExportResult`) per design.md
      § Commands and § Infrastructure › Repository Implementations
      (adapters)
- [x] `dto.py` — **modify**: re-export `default_rst_for_mode` from
      `domain/logging_session/value_objects.py`, alongside the existing
      `MODE_OPTIONS` re-export, per design.md § DTOs, Story 13 amendment.

## Infrastructure Layer

`src/radio_pota_logging/infrastructure/`

- [x] Remove the obsolete `db/` scaffold: delete
      `infrastructure/db/__init__.py` and the now-empty `db/` directory —
      no ORM/database is used by this project (design.md § Open
      Questions/Risks, `.claude/rules/structure.md` 2026-08-30 update)
- [x] `repositories/file_logging_session_repository.py` — implement
      `FileLoggingSessionRepository` (implements `LoggingSessionRepository`):
      reads/writes `.qso_session.json` in the launch directory;
      `archive()` renames it to
      `.qso_session.<started-at-UTC-timestamp>.json` per design.md §
      Persistence and § Repository Implementations (adapters)
- [x] `adif/adif_file_exporter.py` — implement `AdifFileExporter`
      (implements `AdifExporter`): formats one ADIF record per `Qso` using
      exactly the 14 fields from the adif-generation feature's requirements
      Story 1, as a pure string transform per design.md § Repository
      Implementations (adapters)

## API Layer

`src/radio_pota_logging/api/` (PyQt desktop presentation layer — see
design.md § API Layer for why this stands in for the template's separate
Frontend Design section; this project has no `frontend/src`)

- [x] `qso_entry_form_widget.py` — implement `QsoEntryFormWidget`: renders
      the 11 entry fields, applies an `EntryDefaultsDto` to pre-fill
      itself and focus CALL, emits a `SubmitQsoRequest` via Qt signal on
      submit per design.md § Components
- [x] `qso_entry_form_widget.py` — **modify** `QsoEntryFormWidget`: connect
      the CALL field's `textEdited` signal to a handler that uppercases
      the text in place, preserving cursor position, per design.md §
      Components, Story 5 amendment.
- [x] `uppercase_field.py` — **new file**: implement
      `uppercase_as_typed(line_edit: QLineEdit) -> None`: connects the
      line edit's `textEdited` signal to a handler that uppercases the
      text in place, preserving cursor position — the same logic
      `QsoEntryFormWidget._uppercase_call` already has, extracted so it
      can be reused per design.md § Overview (Story 7 amendment) and §
      Components.
- [x] `qso_entry_form_widget.py` — **modify** `QsoEntryFormWidget`: remove
      the private `_uppercase_call` method and its `textEdited` connection;
      call `uppercase_as_typed(self._call)` and
      `uppercase_as_typed(self._my_sig_info)` instead, during `__init__`
      per design.md § Components, Story 7 amendment.
- [x] `session_setup_dialog.py` — **modify** `SessionSetupDialog`: call
      `uppercase_as_typed(self._park_reference)` during `__init__` per
      design.md § Components, Story 7 amendment.
- [x] `qso_entry_form_widget.py` — **modify** `QsoEntryFormWidget`: call
      `uppercase_as_typed(self._operator)` during `__init__` per design.md
      § Components, Story 8 amendment.
- [x] `qso_entry_form_widget.py` — **modify** `QsoEntryFormWidget`: replace
      `self._mode = QLineEdit()` with a non-editable `self._mode =
      QComboBox()` populated from `MODE_OPTIONS` (imported from
      `application/logging_session/dto.py`, which re-exports it from
      `domain/logging_session/value_objects.py` — `api/` never imports
      `domain/` directly, per `.claude/rules/domain-driven-design.md`),
      defaulting to `"CW"`; update `apply_defaults()` to call
      `self._mode.setCurrentText(...)` instead of `.setText(...)`; update
      `_on_submit_clicked()` to read `self._mode.currentText()` instead of
      `.text()` per design.md § Overview (Story 9 amendment) and §
      Components.
- [x] `qso_list_widget.py` — implement `QsoListWidget`: read-only, ordered
      display of appended `QsoDto` rows per design.md § Components
- [x] `session_resume_prompt_dialog.py` — implement
      `SessionResumePromptDialog`: asks the operator once at startup to
      resume or start clean per design.md § Components
- [x] `session_setup_dialog.py` — **new file**: implement
      `SessionSetupResult` (frozen dataclass: `park_reference: str,
      qso_date: date, time_on: time`) and `SessionSetupDialog` (QDialog):
      three fields (park reference `QLineEdit`; date `QDateEdit`
      pre-filled with the current date; time `QTimeEdit` pre-filled with
      the current UTC time), "OK" and "Quit" actions, "OK" disabled while
      the park reference field is empty, `.setup_result:
      SessionSetupResult | None` set on "OK" and left `None` on "Quit" per
      design.md § Components, Story 6 amendment. (Named `setup_result`,
      not `result` as design.md literally says — `QDialog` already has a
      built-in `result()` method, and shadowing it with an instance
      attribute of the same name is a latent-bug risk; `SessionResumePromptDialog`
      avoids the identical collision by using `choice` instead of `result`
      for the same reason.)
- [x] `session_setup_dialog.py` — **modify** `SessionSetupResult` and
      `SessionSetupDialog`: add a fourth field, `freq: str` on
      `SessionSetupResult` and a "Frequency" `QLineEdit` on the dialog
      (left empty initially, like the park reference field); "OK" stays
      disabled unless **both** the park reference and Frequency fields are
      non-empty per design.md § Overview (Story 6 extension amendment) and
      § Components.
- [x] `session_bootstrap.py` — **new file**: implement
      `bootstrap_session(check_for_resumable_session,
      resume_session, start_new_session) -> SessionStartResult | None`:
      if `check_for_resumable_session.execute()` is `True`, show
      `SessionResumePromptDialog`; if "Resume" is chosen, return
      `resume_session.execute()`. Otherwise (no resumable session, or
      "Start Clean" chosen), show `SessionSetupDialog`; if its
      `.setup_result` is `None` ("Quit"), return `None`; otherwise return
      `start_new_session.execute(qso_date=result.qso_date,
      time_on=result.time_on, park_reference=result.park_reference)` per
      design.md § Entry points and § Components, Story 6 amendment.
- [x] `session_bootstrap.py` — **modify** `bootstrap_session`: pass
      `freq=setup_dialog.setup_result.freq` as an additional keyword
      argument to `start_new_session.execute(...)` per design.md § Entry
      points and § Components, Story 6 Frequency extension.
- [x] `qso_entry_controller.py` — implement `QsoEntryController`: wires
      `QsoEntryFormWidget`'s submit signal to `SubmitQsoCommand` (on
      `FrequencyFormatError`/`FrequencyOutOfBandError`, shows an inline
      error and leaves the form as typed) and the "Generate ADIF" action
      to `GenerateAdifCommand` (destination path from a native Save File
      dialog) per design.md § Entry points and § Components
- [x] `main_window.py` — implement `MainWindow`: hosts the form, QSO list,
      and "Generate ADIF" action; on startup runs
      `CheckForResumableSessionQuery` and shows
      `SessionResumePromptDialog` only if it returns `True`, then calls
      `ResumeSessionCommand` or `StartNewSessionCommand` accordingly per
      design.md § Entry points and § Components
- [x] `main_window.py` — **modify** `MainWindow`: change `__init__` to
      take `initial_result: SessionStartResult, submit_qso: SubmitQsoCommand,
      generate_adif: GenerateAdifCommand` (dropping
      `check_for_resumable_session`, `resume_session`,
      `start_new_session`); remove `_run_startup_flow` and
      `_start_fresh_session`; call `self._apply_session_start_result(initial_result)`
      directly instead per design.md § Components, Story 6 amendment.
- [x] `main_window.py` — **modify** `MainWindow.__init__`: after building
      and setting the central layout, read
      `QApplication.primaryScreen()`; if not `None`, call
      `self.resize(geometry.width() // 2, geometry.height() // 2)` using
      `.availableGeometry()`'s width/height; if `None`, skip the resize
      per design.md § Overview (Story 10 amendment) and § Components.
- [x] `qso_entry_form_widget.py` — **modify** `QsoEntryFormWidget`: collect
      all 11 field widgets (`self._call, self._qso_date, self._time_on,
      self._mode, self._my_sig_info, self._rst_sent, self._rst_rcvd,
      self._freq, self._operator, self._my_rig, self._tx_pwr`) into a list
      and call `.installEventFilter(self)` on each during `__init__`;
      implement `eventFilter(self, obj: QObject, event: QEvent) -> bool`:
      on a `QEvent.Type.KeyPress` whose `event.key()` is
      `Qt.Key.Key_Return` or `Qt.Key.Key_Enter`, call
      `self._on_enter_pressed()` and return `True`; otherwise return
      `super().eventFilter(obj, event)`; implement
      `_on_enter_pressed(self) -> None`: call `self._on_submit_clicked()`
      only `if self._call.text():`, otherwise do nothing — leave
      `_on_submit_clicked()` itself unmodified per design.md § Overview
      (Story 11 amendment) and § Components.
- [x] `main_window.py` — **modify** `MainWindow.__init__`: change the
      resize call's height term from `geometry.height() // 2` to
      `geometry.height() * 3 // 4`; the width term
      (`geometry.width() // 2`) is unchanged per design.md § Overview
      (Story 10 height fraction amendment).
- [x] `qso_entry_form_widget.py` — **modify** `QsoEntryFormWidget.__init__`:
      reorder the 11 field-construction statements and the matching
      `form.addRow(...)` calls to CALL, RST_RCVD, RST_SENT, TIME_ON, FREQ,
      MY_SIG_INFO, QSO_DATE, MODE, OPERATOR, MY_RIG, TX_PWR; store the
      `QFormLayout` as `self._form` instead of a local `form` variable;
      after the layout is built, add an explicit
      `QWidget.setTabOrder(...)` chain across all 11 fields in that same
      order (`setTabOrder(self._call, self._rst_rcvd)`,
      `setTabOrder(self._rst_rcvd, self._rst_sent)`, … through
      `self._tx_pwr`) per design.md § Overview (Story 12 amendment) and §
      Components.
- [x] `qso_entry_form_widget.py` — **modify** `QsoEntryFormWidget.__init__`:
      replace the single `self._form` `QFormLayout` with three
      `QFormLayout` instances — `self._column_1` (CALL, RST_RCVD,
      RST_SENT, TIME_ON), `self._column_2` (FREQ, MY_SIG_INFO, QSO_DATE,
      MODE), `self._column_3` (OPERATOR, MY_RIG, TX_PWR) — each populated
      via its own `addRow(label, widget)` calls in that order, using the
      already-constructed field widgets (no change to widget construction
      itself); wrap the three in a new `QHBoxLayout` and replace
      `layout.addLayout(self._form)` with
      `layout.addLayout(columns_layout)` in the outer `QVBoxLayout`. Do
      **not** change `self._fields`, the `installEventFilter` loop, or the
      `QWidget.setTabOrder(...)` chain — per design.md § Overview (Story 12
      column layout amendment) and § Components, those stay exactly as
      Story 12's original amendment left them.
- [x] `composition_root.py` — **modify** `main()`: after constructing
      `QApplication`, call
      `session_bootstrap.bootstrap_session(check_for_resumable_session=CheckForResumableSessionQuery(repository),
      resume_session=ResumeSessionCommand(repository),
      start_new_session=StartNewSessionCommand(repository))`; if it
      returns `None`, `return 0` without constructing `MainWindow`;
      otherwise construct `MainWindow(initial_result=..., submit_qso=...,
      generate_adif=...)`, `.show()` it, and run the event loop as before
      per design.md § Entry points and § Components, Story 6 amendment.

- [x] `qso_entry_form_widget.py` — **modify** `QsoEntryFormWidget.__init__`:
      add `self._rst_sent_default: str | None = None` and
      `self._rst_rcvd_default: str | None = None`; set both whenever
      `apply_defaults()` runs (assign from the applied
      `EntryDefaultsDto.rst_sent`/`.rst_rcvd`); connect
      `self._mode.currentTextChanged` to a new `_on_mode_changed(self,
      mode: str) -> None` handler per design.md § Overview (Story 13
      amendment) and § Components.
- [x] `qso_entry_form_widget.py` — **new method** `_on_mode_changed(self,
      mode: str) -> None`: guard with `if self._rst_sent_default is None:
      return` (no-op if fired before the first `apply_defaults()` call);
      compute `new_default = default_rst_for_mode(mode)` (imported from
      `application/logging_session/dto.py`); if
      `self._rst_sent.text() == self._rst_sent_default`, call
      `self._rst_sent.setText(new_default)`; if `self._rst_rcvd.text() ==
      self._rst_rcvd_default`, call `self._rst_rcvd.setText(new_default)`;
      then set both `self._rst_sent_default`/`self._rst_rcvd_default` to
      `new_default` per design.md § Overview (Story 13 amendment).
- [x] `qso_entry_form_widget.py` — **modify** `QsoEntryFormWidget.__init__`:
      call `self._time_on.setDisplayFormat("HH:mm")` right after
      constructing `self._time_on = QTimeEdit()`, hiding the seconds
      spinner section per design.md § Overview (Story 14 amendment) and §
      Components.
- [x] `session_setup_dialog.py` — **modify** `SessionSetupDialog.__init__`:
      call `self._time_on.setDisplayFormat("HH:mm")` right after
      constructing `self._time_on = QTimeEdit()`, hiding the seconds
      spinner section per design.md § Overview (Story 14 amendment) and §
      Components.

## Frontend

N/A — this project has no `frontend/src`; see design.md § API Layer.

## Tests

`tests/` mirrors `src/radio_pota_logging/`.

- [x] `tests/domain/logging_session/test_value_objects.py` — unit tests
      for `Frequency` (every band-plan row's boundaries, plus values
      outside all rows raising `FrequencyOutOfBandError`, plus unparsable
      strings raising `FrequencyFormatError`), `QsoTimestamp.plus_two_minutes()`
      (including a midnight-rollover case), and `EntryDefaults.seed()` per
      design.md § Testing Strategy
- [x] `tests/domain/logging_session/test_value_objects.py` — **add** tests
      for `Qso` CALL normalization (Story 5): lowercase and mixed-case
      `call` input is uppercased (e.g. `Qso(call="w1aw/p", ...).call ==
      "W1AW/P"`); digits and `/` are unaffected; per design.md § Testing
      Strategy.
- [x] `tests/domain/logging_session/test_value_objects.py` — **add** tests
      for `Qso` MY_SIG_INFO normalization (Story 7): lowercase and
      mixed-case `my_sig_info` input is uppercased (e.g.
      `Qso(my_sig_info="k-1234", ...).my_sig_info == "K-1234"`); digits and
      `-` are unaffected; per design.md § Testing Strategy.
- [x] `tests/domain/logging_session/test_value_objects.py` — **add** a
      test (Story 6): `EntryDefaults.seed(StationDefaults(), now,
      my_sig_info="K-1234").my_sig_info == "K-1234"`, and confirm the
      existing seed test (no `my_sig_info` argument) still passes with the
      default `""` per design.md § Testing Strategy.
- [x] `tests/domain/logging_session/test_value_objects.py` — **add** a
      test (Story 6 Frequency extension):
      `EntryDefaults.seed(StationDefaults(), now,
      freq="14.062").freq == "14.062"` per design.md § Testing Strategy.
- [x] `tests/domain/logging_session/test_value_objects.py` — **add** a
      test (Story 7): `EntryDefaults.seed(StationDefaults(), now,
      my_sig_info="k-1234").my_sig_info == "K-1234"` per design.md §
      Testing Strategy.
- [x] `tests/domain/logging_session/test_value_objects.py` — **add** tests
      for `Qso` OPERATOR normalization (Story 8): lowercase and
      mixed-case `operator` input is uppercased (e.g.
      `Qso(operator="sm6y", ...).operator == "SM6Y"`); per design.md §
      Testing Strategy.
- [x] `tests/domain/logging_session/test_value_objects.py` — **add** a
      test (Story 8): `EntryDefaults.seed(StationDefaults(operator="sm6y"),
      now).operator == "SM6Y"` per design.md § Testing Strategy.
- [x] `tests/domain/logging_session/test_value_objects.py` — **add** a
      test (Story 9): `MODE_OPTIONS == ("CW", "SSB")` per design.md §
      Testing Strategy.
- [x] `tests/domain/logging_session/test_value_objects.py` — **add** tests
      (Story 13): `default_rst_for_mode("CW") == "599"` and
      `default_rst_for_mode("SSB") == "59"`, table-driven, per design.md §
      Testing Strategy.
- [x] `tests/domain/logging_session/test_value_objects.py` — **add** a test
      (Story 13): `EntryDefaults.seed(StationDefaults(mode="SSB"),
      now).rst_sent == "59"` and `.rst_rcvd == "59"` — proves the
      first-entry RST default follows `StationDefaults.mode`, not a fixed
      constant, per design.md § Testing Strategy.
- [x] `tests/domain/logging_session/test_value_objects.py` — **add** tests
      (Story 14): `QsoTimestamp(date(2026, 8, 30), time(14, 12,
      47)).time_on == time(14, 12, 0)` — table-driven across a few
      nonzero-second/microsecond inputs, proving seconds/microseconds are
      always dropped regardless of what was passed in, per design.md §
      Testing Strategy.
- [x] `tests/domain/logging_session/test_value_objects.py` — **add** a test
      (Story 14): a nonzero-seconds input to
      `QsoTimestamp(...).plus_two_minutes()` still returns a
      `QsoTimestamp` with zero seconds, alongside the existing
      midnight-rollover case, per design.md § Testing Strategy.
- [x] `tests/domain/logging_session/test_entities.py` — unit tests for
      `LoggingSession.record_qso` (TIME_OFF==TIME_ON, `next_entry_defaults`
      carried forward correctly except CALL, first-entry seeding from
      `StationDefaults` via `LoggingSession.start`, append-only QSO
      ordering) per design.md § Testing Strategy
- [x] `tests/domain/logging_session/test_entities.py` — **add** a test
      (Story 6): `LoggingSession.start(StationDefaults(), now,
      my_sig_info="K-1234").next_entry_defaults.my_sig_info ==
      "K-1234"` per design.md § Testing Strategy.
- [x] `tests/domain/logging_session/test_entities.py` — **add** a test
      (Story 6 Frequency extension):
      `LoggingSession.start(StationDefaults(), now,
      freq="14.062").next_entry_defaults.freq == "14.062"` per design.md §
      Testing Strategy.
- [x] `tests/domain/logging_session/test_entities.py` — **add** a
      regression test (Story 7): `LoggingSession.record_qso(...,
      my_sig_info="k-1234", ...).next_entry_defaults.my_sig_info ==
      "K-1234"` — proves the carried-forward value is normalized even
      though `record_qso` builds `next_entry_defaults` from the raw
      `my_sig_info` parameter, not `qso.my_sig_info`, per design.md §
      Testing Strategy (see the Story 7 amendment note under Overview).
- [x] `tests/domain/logging_session/test_entities.py` — **add** a
      regression test (Story 8): `LoggingSession.record_qso(...,
      operator="sm6y", ...).next_entry_defaults.operator == "SM6Y"` —
      same shape as the Story 7 regression test, for `operator` per
      design.md § Testing Strategy.
- [x] `tests/domain/logging_session/test_entities.py` — **add** a test
      (Story 2 RST reset): `LoggingSession.record_qso(..., rst_sent="579",
      rst_rcvd="588", ...)` then assert
      `next_entry_defaults.rst_sent == "599"` and
      `next_entry_defaults.rst_rcvd == "599"` — proves an edited
      RST_SENT/RST_RCVD does not carry forward, unlike every other field
      per design.md § Testing Strategy.
- [x] `tests/domain/logging_session/test_entities.py` — **add** a test
      (Story 13): `LoggingSession.record_qso(..., mode="SSB",
      rst_sent="599", rst_rcvd="599", ...)` then assert
      `next_entry_defaults.rst_sent == "59"` and
      `next_entry_defaults.rst_rcvd == "59"` — proves the next entry's RST
      default follows the just-submitted QSO's MODE, not a fixed constant;
      the existing
      `test_record_qso_resets_rst_sent_and_rst_rcvd_instead_of_carrying_them_forward`
      test (which submits `mode="CW"`) keeps passing unchanged, per
      design.md § Testing Strategy.
- [x] `tests/application/logging_session/test_commands.py` — unit tests
      for `ResumeSessionCommand`, `StartNewSessionCommand`,
      `SubmitQsoCommand`, and `GenerateAdifCommand` against fake
      `LoggingSessionRepository`/`AdifExporter` doubles (no real file I/O)
      per design.md § Testing Strategy
- [x] `tests/application/logging_session/test_commands.py` — **modify**
      the two existing `StartNewSessionCommand` tests
      (`test_start_new_session_seeds_defaults_and_saves`,
      `test_start_new_session_archives_existing_unfinished_session`) to
      pass the now-required `park_reference=` keyword argument, and
      **add** a test (Story 6) asserting `park_reference` flows through:
      `StartNewSessionCommand(repository).execute(qso_date=..., time_on=...,
      park_reference="K-1234").entry_defaults.my_sig_info == "K-1234"` per
      design.md § Testing Strategy.
- [x] `tests/application/logging_session/test_commands.py` — **modify**
      the two existing `StartNewSessionCommand` tests to also pass
      `freq="14.062"`, and **add** a test (Story 6 Frequency extension)
      asserting it flows through:
      `StartNewSessionCommand(repository).execute(qso_date=..., time_on=...,
      park_reference="K-1234",
      freq="14.062").entry_defaults.freq == "14.062"` per design.md §
      Testing Strategy.
- [x] `tests/application/logging_session/test_queries.py` — unit tests for
      `CheckForResumableSessionQuery` against a fake
      `LoggingSessionRepository` per design.md § Testing Strategy
- [x] `tests/infrastructure/repositories/test_file_logging_session_repository.py`
      — integration tests for `FileLoggingSessionRepository` round-trips
      (`save` → `find_unfinished`, `archive` renames without deleting)
      against a temp directory per design.md § Testing Strategy
- [x] `tests/infrastructure/repositories/test_file_logging_session_repository.py`
      — **add** a test (Story 5): write a session JSON file with a
      lowercase-stored `call` (simulating data saved before this change),
      then assert `find_unfinished()` returns a `Qso` whose `call` is
      uppercase, since normalization happens in `Qso.__post_init__` on
      construction regardless of where the value came from; per design.md
      § Testing Strategy.
- [x] `tests/infrastructure/repositories/test_file_logging_session_repository.py`
      — **add** a test (Story 7): same as the Story 5 test above, but for
      a lowercase-stored `my_sig_info` — asserts it comes back uppercase
      per design.md § Testing Strategy.
- [x] `tests/infrastructure/repositories/test_file_logging_session_repository.py`
      — **add** a test (Story 8): same as the Story 5/7 tests above, but
      for a lowercase-stored `operator` — asserts it comes back uppercase
      per design.md § Testing Strategy.
- [x] `tests/infrastructure/repositories/test_file_logging_session_repository.py`
      — **add** a test (Story 14): write a session JSON file with a
      nonzero-seconds `time_on` (e.g. `"14:12:47"`, simulating data saved
      before this change), then assert `find_unfinished()` returns a `Qso`
      whose `timestamp.time_on.second == 0`, since normalization happens
      in `QsoTimestamp.__post_init__` on construction regardless of where
      the value came from, per design.md § Testing Strategy.
- [x] `tests/infrastructure/adif/test_adif_file_exporter.py` — tests for
      `AdifFileExporter.export()` against a golden ADIF sample for a
      couple of representative QSOs, including a band-boundary frequency,
      per design.md § Testing Strategy
- [x] `tests/infrastructure/adif/test_adif_file_exporter.py` — **add** a
      test (Story 14): export a QSO whose `QsoTimestamp` was constructed
      from a nonzero-seconds `time` value, and assert the resulting
      `TIME_ON`/`TIME_OFF` ADIF fields both end in `"00"` — proving
      `AdifFileExporter` needed no code change, since
      `QsoTimestamp.__post_init__` already guarantees zero seconds, per
      design.md § Testing Strategy.
- [x] `tests/api/test_qso_entry_form_widget.py` — pytest-qt tests for
      `QsoEntryFormWidget`: pre-fill from an `EntryDefaultsDto`, CALL
      receives focus, submit emits the expected `SubmitQsoRequest` per
      design.md § Testing Strategy
- [x] `tests/api/test_qso_entry_form_widget.py` — **add** a pytest-qt test
      (Story 5): typing lowercase text into CALL displays it uppercase
      immediately; per design.md § Testing Strategy.
- [x] `tests/api/test_uppercase_field.py` — **new file**: pytest-qt tests
      for `uppercase_as_typed()` directly against a bare `QLineEdit`
      (Story 7): typing lowercase text displays uppercase immediately;
      cursor position is preserved after a mid-string edit; per design.md
      § Testing Strategy.
- [x] `tests/api/test_qso_entry_form_widget.py` — **add** a pytest-qt test
      (Story 7): typing lowercase text into MY_SIG_INFO displays it
      uppercase immediately, the same way CALL already does; per
      design.md § Testing Strategy.
- [x] `tests/api/test_qso_entry_form_widget.py` — **add** a pytest-qt test
      (Story 8): typing lowercase text into OPERATOR displays it uppercase
      immediately, the same way CALL already does; per design.md §
      Testing Strategy.
- [x] `tests/api/test_qso_entry_form_widget.py` — **add** pytest-qt tests
      (Story 9): the MODE `QComboBox`'s items are exactly `["CW", "SSB"]`
      and it is not editable; `apply_defaults()` with `mode="SSB"` sets
      the combo box's current text to `"SSB"`; submitting with "SSB"
      selected includes `mode="SSB"` in the emitted `SubmitQsoRequest`
      per design.md § Testing Strategy.
- [x] `tests/api/test_qso_list_widget.py` — pytest-qt tests for
      `QsoListWidget` rendering appended `QsoDto` rows in order per
      design.md § Testing Strategy
- [x] `tests/api/test_session_resume_prompt_dialog.py` — pytest-qt tests
      for `SessionResumePromptDialog`'s resume/start-clean choice per
      design.md § Testing Strategy
- [x] `tests/api/test_session_setup_dialog.py` — **new file**: pytest-qt
      tests for `SessionSetupDialog` (Story 6): "OK" starts disabled and
      becomes enabled once the park reference field is non-empty; clicking
      "OK" sets `.setup_result` to a `SessionSetupResult` with the three
      entered values; clicking "Quit" leaves `.setup_result` as `None` per
      design.md § Testing Strategy.
- [x] `tests/api/test_session_setup_dialog.py` — **add** tests (Story 6
      Frequency extension): "OK" stays disabled with a park reference but
      empty Frequency (and vice versa), and only enables once both are
      non-empty; `.setup_result.freq` reflects the entered value per
      design.md § Testing Strategy.
- [x] `tests/api/test_session_setup_dialog.py` — **add** a pytest-qt test
      (Story 7): typing lowercase text into the park reference field
      displays it uppercase immediately per design.md § Testing Strategy.
- [x] `tests/api/test_session_bootstrap.py` — **new file**: pytest-qt
      tests for `bootstrap_session` (Story 6), against fake
      `CheckForResumableSessionQuery`/`ResumeSessionCommand`/`StartNewSessionCommand`:
      no resumable session → `SessionSetupDialog` is shown directly (not
      the resume prompt) and its values reach `StartNewSessionCommand`;
      resumable session + "Resume" chosen → only `ResumeSessionCommand`
      runs, no setup dialog shown; resumable session + "Start Clean"
      chosen → the setup dialog then runs `StartNewSessionCommand`;
      "Quit" clicked on the setup dialog (either path) →
      `bootstrap_session()` returns `None` and no command runs, per
      design.md § Testing Strategy.
- [x] `tests/api/test_session_bootstrap.py` — **modify**: fake setup-dialog
      results and `StartNewSessionCommand` assertions gain a `freq` value,
      confirming it flows from the setup dialog into
      `StartNewSessionCommand.execute(..., freq=...)` per design.md §
      Testing Strategy (Story 6 Frequency extension).
- [x] `tests/api/test_qso_entry_controller.py` — pytest-qt tests for
      `QsoEntryController`: a `SubmitQsoCommand` failure shows an inline
      error and preserves the form's typed values; "Generate ADIF" invokes
      `GenerateAdifCommand` with the chosen destination per design.md §
      Testing Strategy
- [x] `tests/api/test_main_window.py` — pytest-qt tests for `MainWindow`'s
      startup flow: the resume/start-clean prompt is shown only when
      `CheckForResumableSessionQuery` returns `True`, and each choice
      invokes the correct command per design.md § Testing Strategy
- [x] `tests/api/test_main_window.py` — **rewrite** (Story 6): drop the
      startup-flow tests (they move to `test_session_bootstrap.py`, since
      `MainWindow` no longer runs that flow); replace with tests that
      construct `MainWindow(initial_result=a_session_start_result,
      submit_qso=..., generate_adif=...)` directly and assert the form and
      QSO list render that `SessionStartResult` per design.md § Testing
      Strategy.
- [x] `tests/api/test_main_window.py` — **add** a pytest-qt test (Story
      10): construct `MainWindow` and assert `.size().width()` and
      `.size().height()` equal half of
      `QApplication.primaryScreen().availableGeometry()`'s width/height at
      construction time per design.md § Testing Strategy.
- [x] `tests/api/test_main_window.py` — **modify**
      `test_main_window_sizes_itself_to_half_the_primary_screen`: change
      the height assertion from `geometry.height() // 2` to
      `geometry.height() * 3 // 4` (width assertion unchanged); rename the
      test to `test_main_window_sizes_itself_to_half_width_and_three_quarters_height`
      per design.md § Testing Strategy (Story 10 height fraction
      amendment).
- [x] `tests/api/test_qso_entry_form_widget.py` — **add** pytest-qt tests
      (Story 11): with the form pre-filled and CALL set non-empty,
      pressing Enter/Return while focus is in a non-CALL field (e.g.
      MY_RIG) emits `submitted` with the expected `SubmitQsoRequest`;
      pressing Enter/Return while focus is in CALL itself (non-empty) also
      emits `submitted`; with CALL empty, pressing Enter/Return in CALL
      emits nothing (assert via `qtbot.waitSignal(widget.submitted,
      timeout=..., raising=False)` timing out) per design.md § Testing
      Strategy.
- [x] `tests/api/test_qso_entry_form_widget.py` — **add** a pytest-qt test
      (Story 12): read `widget._form`'s 11 rows' label text, in order
      (`QFormLayout.itemAt(i, QFormLayout.ItemRole.LabelRole).widget()
      .text()` for `i in range(11)`), and assert it equals `["CALL",
      "RST_RCVD", "RST_SENT", "TIME_ON", "FREQ", "MY_SIG_INFO",
      "QSO_DATE", "MODE", "OPERATOR", "MY_RIG", "TX_PWR"]` per design.md §
      Testing Strategy.
- [x] `tests/api/test_qso_entry_form_widget.py` — **modify** (Story 12
      column layout): replace the single-`widget._form` row-order test
      above with three assertions, one per column, using the same
      `QFormLayout.itemAt(i, QFormLayout.ItemRole.LabelRole).widget().text()`
      row-reading approach against `widget._column_1`, `widget._column_2`,
      `widget._column_3`: `["CALL", "RST_RCVD", "RST_SENT", "TIME_ON"]`,
      `["FREQ", "MY_SIG_INFO", "QSO_DATE", "MODE"]`, and `["OPERATOR",
      "MY_RIG", "TX_PWR"]` respectively, per design.md § Testing Strategy
      (Story 12 column layout amendment). Leave the Tab-chain
      `.nextInFocusChain()` test below unmodified — design.md states it
      needs no changes.
- [x] `tests/api/test_qso_entry_form_widget.py` — **add** a pytest-qt test
      (Story 12): starting from `widget._call`, call
      `.nextInFocusChain()` repeatedly and assert the resulting sequence
      of the 11 field widgets is `[widget._call, widget._rst_rcvd,
      widget._rst_sent, widget._time_on, widget._freq,
      widget._my_sig_info, widget._qso_date, widget._mode,
      widget._operator, widget._my_rig, widget._tx_pwr]` — a black-box
      check that the `setTabOrder()` chain actually took effect per
      design.md § Testing Strategy.
- [x] `tests/api/test_qso_entry_form_widget.py` — **add** pytest-qt tests
      (Story 13): with the form pre-filled at its "CW" default
      (RST_SENT/RST_RCVD both `"599"`), selecting "SSB" in the MODE combo
      box updates both fields to `"59"`; selecting "CW" again updates both
      back to `"599"`; after manually editing RST_SENT to `"579"` while
      MODE is "CW", selecting "SSB" updates only RST_RCVD to `"59"` and
      leaves RST_SENT at `"579"` per design.md § Testing Strategy.
- [x] `tests/api/test_qso_entry_form_widget.py` — **add** pytest-qt tests
      (Story 14): `widget._time_on.displayFormat() == "HH:mm"`; submitting
      the form and reading the emitted `SubmitQsoRequest.time_on` back
      always has `.second == 0` per design.md § Testing Strategy.
- [x] `tests/api/test_session_setup_dialog.py` — **add** a pytest-qt test
      (Story 14): `dialog._time_on.displayFormat() == "HH:mm"` per
      design.md § Testing Strategy.

## Task Dependencies

- Domain Layer tasks must land before any Application Layer task
  (commands/queries operate on `LoggingSession`, its value objects, and
  the `LoggingSessionRepository`/`AdifExporter` ports).
- Within Domain Layer: `exceptions.py` before `Frequency` (raises them);
  `Band` before `Frequency` (`.band` returns one); `QsoTimestamp` before
  `EntryDefaults`/`Qso` (both embed a timestamp); all value objects before
  `entities.py`'s `LoggingSession` (constructs/holds all of them);
  `repository.py`/`exporter.py` have no dependency on the others and can
  be done any time within this layer.
- Within Application Layer: `dto.py` tasks before `queries.py`/`commands.py`
  (both return DTOs); `queries.py` before `commands.py` is not required,
  but `CheckForResumableSessionQuery` and `ResumeSessionCommand`/
  `StartNewSessionCommand` share the same repository port and are
  naturally implemented together.
- Infrastructure Layer tasks depend on the Domain Layer ports
  (`LoggingSessionRepository`, `AdifExporter`) but not on the Application
  Layer; the `db/` cleanup task has no dependencies and can be done at any
  point.
- API Layer tasks depend on the Application Layer's commands/queries/DTOs.
  Within API Layer: `qso_entry_form_widget.py`, `qso_list_widget.py`, and
  `session_resume_prompt_dialog.py` (leaf widgets) before
  `qso_entry_controller.py` (wires the form/list to commands) and before
  `main_window.py` (hosts all widgets and owns the startup flow);
  `composition_root.py` last, since it wires the concrete Infrastructure
  adapters into `MainWindow`.
- Each test task depends on the implementation task(s) it covers, per the
  file each test task names above.

### Story 5 amendment (added after initial implementation)

- `value_objects.py`'s `Qso.__post_init__` modification has no dependency
  on anything new (it modifies an already-implemented class) and must
  land before its two test tasks: `test_value_objects.py`'s new CALL
  normalization tests, and
  `test_file_logging_session_repository.py`'s new legacy-data test (which
  relies on `Qso` construction normalizing `call` during deserialization).
- `qso_entry_form_widget.py`'s live-uppercase modification has no
  dependency on anything new and must land before its new
  `test_qso_entry_form_widget.py` test case.
- These two implementation tasks are independent of each other and may be
  done in either order.

### Story 6 amendment (added after initial implementation)

- Order: `value_objects.py`'s `EntryDefaults.seed` modification →
  `entities.py`'s `LoggingSession.start` modification (calls `seed`) →
  `commands.py`'s `StartNewSessionCommand.execute` modification (calls
  `start`). Each must land before its own test modifications/additions
  above.
- `session_setup_dialog.py` (new) has no dependency on anything new.
- `session_bootstrap.py` (new) depends on: `session_setup_dialog.py`,
  the existing `session_resume_prompt_dialog.py`, and the modified
  `commands.py` (`StartNewSessionCommand`'s new `park_reference`
  parameter). Must land before `test_session_bootstrap.py` and before
  `composition_root.py`'s modification.
- `main_window.py`'s modification has no dependency on `session_bootstrap.py`
  — they're independent siblings both used by `composition_root.py` — but
  must land before `test_main_window.py`'s rewrite.
- `composition_root.py`'s modification depends on both `session_bootstrap.py`
  and `main_window.py`'s modification, since it wires bootstrap's result
  into `MainWindow`'s new, simplified constructor. It is the last Story 6
  task.

### Story 6 Frequency extension (added after Story 6 was implemented)

- Same shape as the Story 6 amendment above, one field later: order is
  `value_objects.py`'s `EntryDefaults.seed` `freq` modification →
  `entities.py`'s `LoggingSession.start` `freq` modification →
  `commands.py`'s `StartNewSessionCommand.execute` `freq` modification.
  Each must land before its own test modifications/additions above.
- `session_setup_dialog.py`'s modification (add the Frequency field) has
  no dependency on anything new, and must land before its new
  `test_session_setup_dialog.py` test cases.
- `session_bootstrap.py`'s modification (pass `freq` through) depends on
  both `session_setup_dialog.py`'s modification and the modified
  `commands.py`, and must land before `test_session_bootstrap.py`'s
  modification. It is the last task in this extension — `main_window.py`
  and `composition_root.py` need no further changes, since FREQ already
  flows through `SessionStartResult`/`EntryDefaultsDto` unchanged.

### Story 7 amendment (added after Story 6 was implemented)

- `value_objects.py`'s `Qso.__post_init__` extension (normalize
  `my_sig_info` too) has no dependency on anything new and must land
  before its own test task.
- `value_objects.py`'s new `EntryDefaults.__post_init__` has no
  dependency on anything new and must land before its own test task and
  before `test_entities.py`'s new regression test (which relies on
  `record_qso`'s `EntryDefaults(...)` construction normalizing
  `my_sig_info`).
- `uppercase_field.py` (new) has no dependency on anything new, and must
  land before: `qso_entry_form_widget.py`'s refactor, `session_setup_dialog.py`'s
  modification, and `test_uppercase_field.py`.
- `qso_entry_form_widget.py`'s refactor depends on `uppercase_field.py`
  and must land before its own new MY_SIG_INFO test (and keep the
  existing CALL live-uppercase test passing, as a regression guard on the
  refactor).
- `session_setup_dialog.py`'s modification depends on `uppercase_field.py`
  and must land before its own new park-reference test.
- `test_file_logging_session_repository.py`'s new legacy-data test for
  `my_sig_info` depends on `Qso.__post_init__`'s extension.
- These implementation tasks (`Qso.__post_init__`, `EntryDefaults.__post_init__`,
  `uppercase_field.py`, `qso_entry_form_widget.py`, `session_setup_dialog.py`)
  have no dependency on each other beyond what's listed above, and may
  otherwise be done in any order.

### Story 8 amendment (added after Story 7 was implemented)

- `value_objects.py`'s `Qso.__post_init__` extension (normalize `operator`
  too) has no dependency on anything new and must land before its own
  test task.
- `value_objects.py`'s `EntryDefaults.__post_init__` extension (normalize
  `operator` too) has no dependency on anything new and must land before
  its own test task and before `test_entities.py`'s new regression test.
- `qso_entry_form_widget.py`'s `uppercase_as_typed(self._operator)`
  addition depends only on the already-implemented `uppercase_field.py`
  and must land before its own new OPERATOR test.
- `test_file_logging_session_repository.py`'s new legacy-data test for
  `operator` depends on `Qso.__post_init__`'s extension.
- These implementation tasks have no dependency on each other beyond what's
  listed above.

### Story 9 amendment (added after Story 7 was implemented)

- `value_objects.py`'s new `MODE_OPTIONS` constant has no dependency on
  anything new and must land before its own test task and before
  `qso_entry_form_widget.py`'s MODE-dropdown modification (which imports
  it).
- `qso_entry_form_widget.py`'s MODE-dropdown modification depends on
  `MODE_OPTIONS` and must land before its own new test cases.
- Independent of Story 8's tasks — may be done in either order relative
  to them.

### Story 10 amendment (added after Story 9 was implemented)

- `main_window.py`'s `__init__` modification has no dependency on
  anything new (uses the already-running `QApplication` instance) and
  must land before its own new `test_main_window.py` sizing test.
- Independent of Story 11's tasks — may be done in either order relative
  to them.

### Story 11 amendment (added after Story 9 was implemented)

- `qso_entry_form_widget.py`'s event-filter/`_on_enter_pressed`
  modification has no dependency on anything new and must land before its
  own new `test_qso_entry_form_widget.py` test cases.
- Independent of Story 10's tasks — may be done in either order relative
  to them.

### Story 2 RST reset amendment (added after Story 11 was implemented)

- `entities.py`'s `LoggingSession.record_qso` modification has no
  dependency on anything new and must land before its own new
  `test_entities.py` test.
- Independent of the Story 10 height-fraction and Story 12 amendments
  below — may be done in any order relative to them.

### Story 10 height fraction amendment (added after Story 11 was implemented)

- `main_window.py`'s `__init__` modification has no dependency on
  anything new and must land before `test_main_window.py`'s modified
  sizing test.
- Independent of the Story 2 RST reset and Story 12 amendments — may be
  done in any order relative to them.

### Story 12 amendment (added after Story 11 was implemented)

- `qso_entry_form_widget.py`'s field-reorder/`setTabOrder()` modification
  has no dependency on anything new — it touches the same file as Story
  11's event-filter modification (already implemented) but is otherwise
  independent of it — and must land before its own two new
  `test_qso_entry_form_widget.py` test cases.
- Independent of the Story 2 RST reset and Story 10 height-fraction
  amendments — may be done in any order relative to them.

### Story 12 column layout amendment (added after Story 12 was implemented)

- `qso_entry_form_widget.py`'s column-layout modification depends on
  Story 12's original field-reorder/`setTabOrder()` task already being
  landed (it replaces that task's `self._form`/`layout.addLayout(self._form)`
  lines, and relies on `self._fields` and the `setTabOrder()` chain
  staying untouched) and must land before its own modified
  `test_qso_entry_form_widget.py` row-order test.
- Independent of every other amendment in this file — touches only
  `qso_entry_form_widget.py`'s layout-construction lines.

### Story 13 amendment (added after Story 12 was implemented)

- `value_objects.py`'s new `default_rst_for_mode` function has no
  dependency on anything new and must land before: `value_objects.py`'s
  `StationDefaults` field removal, `EntryDefaults.seed`'s modification,
  `entities.py`'s `record_qso` modification, `dto.py`'s re-export, and its
  own new test task.
- `value_objects.py`'s `StationDefaults` field removal and
  `EntryDefaults.seed`'s modification must land together — `seed` stops
  reading `station_defaults.rst_sent`/`.rst_rcvd`, so landing the field
  removal without the `seed` change (or vice versa) leaves `seed`
  referencing removed fields.
- `entities.py`'s `record_qso` modification depends on
  `default_rst_for_mode` and must land before its own new
  `test_entities.py` test.
- `dto.py`'s re-export depends on `default_rst_for_mode` and must land
  before `qso_entry_form_widget.py`'s `_on_mode_changed`/tracked-default
  modification (which imports it).
- `qso_entry_form_widget.py`'s `_on_mode_changed`/tracked-default
  modification depends on `dto.py`'s re-export and must land before its
  own new test cases.
- Independent of the Story 14 tasks below — may be done in any order
  relative to them.

### Story 14 amendment (added after Story 12 was implemented)

- `value_objects.py`'s new `QsoTimestamp.__post_init__` has no dependency
  on anything new and must land before: its own new
  `test_value_objects.py` tests, `test_file_logging_session_repository.py`'s
  new legacy-data test, and `test_adif_file_exporter.py`'s new test — all
  three rely on `QsoTimestamp` construction normalizing seconds.
- `qso_entry_form_widget.py`'s `setDisplayFormat("HH:mm")` addition has no
  dependency on anything new and must land before its own new
  display-format/submitted-time test.
- `session_setup_dialog.py`'s `setDisplayFormat("HH:mm")` addition has no
  dependency on anything new and must land before its own new
  display-format test.
- Independent of the Story 13 tasks above — may be done in any order
  relative to them.
