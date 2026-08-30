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
      `Band` via the requirements Story 4 band-plan table, raising
      `FrequencyOutOfBandError` on no match) per design.md § Value Objects
- [x] `value_objects.py` — implement `QsoTimestamp` (`qso_date`, `time_on`;
      `.plus_two_minutes()` using `datetime` arithmetic for midnight
      rollover) per design.md § Value Objects
- [x] `value_objects.py` — implement `StationDefaults` (fixed constants:
      operator `SM6Y`, mode `CW`, my_sig `POTA`, rst_sent/rst_rcvd `599`,
      my_rig `Elecraft KX2`, tx_pwr `5`) per design.md § Value Objects
- [x] `value_objects.py` — implement `EntryDefaults`, including
      `EntryDefaults.seed(station_defaults, now)` per design.md § Value
      Objects
- [x] `value_objects.py` — implement `Qso` (immutable; `time_off` reads as
      `timestamp.time_on`; `band` reads as `freq.band`) per design.md §
      Value Objects
- [x] `entities.py` — implement `LoggingSession` entity: `LoggingSession.start(station_defaults,
      now)` classmethod (seeds `next_entry_defaults`, empty `qsos`) and
      `record_qso(...)` method (constructs `Frequency`/`QsoTimestamp`,
      appends the new `Qso`, recomputes `next_entry_defaults` carrying
      every field forward except CALL) per design.md § Entities
- [x] `repository.py` — define `LoggingSessionRepository` protocol:
      `find_unfinished() -> LoggingSession | None`, `save(session) ->
      None`, `archive(session) -> None` per design.md § Repository
      Interfaces (ports)
- [x] `exporter.py` — define `AdifExporter` protocol: `export(qsos:
      Sequence[Qso]) -> str` per design.md § Repository Interfaces (ports)

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
- [x] `commands.py` — implement `SubmitQsoCommand` (calls
      `LoggingSession.record_qso`, saves via repository; propagates
      `FrequencyFormatError`/`FrequencyOutOfBandError`) per design.md §
      Commands
- [x] `commands.py` — implement `GenerateAdifCommand` (reads current
      session, calls `AdifExporter.export()`, writes the result to the
      given `destination` path, returns `AdifExportResult`) per design.md
      § Commands and § Infrastructure › Repository Implementations
      (adapters)

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
      exactly the 14 fields from requirements Story 4, as a pure string
      transform per design.md § Repository Implementations (adapters)

## API Layer

`src/radio_pota_logging/api/` (PyQt desktop presentation layer — see
design.md § API Layer for why this stands in for the template's separate
Frontend Design section; this project has no `frontend/src`)

- [x] `qso_entry_form_widget.py` — implement `QsoEntryFormWidget`: renders
      the 11 entry fields, applies an `EntryDefaultsDto` to pre-fill
      itself and focus CALL, emits a `SubmitQsoRequest` via Qt signal on
      submit per design.md § Components
- [x] `qso_list_widget.py` — implement `QsoListWidget`: read-only, ordered
      display of appended `QsoDto` rows per design.md § Components
- [x] `session_resume_prompt_dialog.py` — implement
      `SessionResumePromptDialog`: asks the operator once at startup to
      resume or start clean per design.md § Components
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
- [x] `composition_root.py` — implement `main()`: construct
      `FileLoggingSessionRepository` and `AdifFileExporter`, wire them
      into the commands/queries, construct `MainWindow`, and run the Qt
      event loop per design.md § Components

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
- [x] `tests/domain/logging_session/test_entities.py` — unit tests for
      `LoggingSession.record_qso` (TIME_OFF==TIME_ON, `next_entry_defaults`
      carried forward correctly except CALL, first-entry seeding from
      `StationDefaults` via `LoggingSession.start`, append-only QSO
      ordering) per design.md § Testing Strategy
- [x] `tests/application/logging_session/test_commands.py` — unit tests
      for `ResumeSessionCommand`, `StartNewSessionCommand`,
      `SubmitQsoCommand`, and `GenerateAdifCommand` against fake
      `LoggingSessionRepository`/`AdifExporter` doubles (no real file I/O)
      per design.md § Testing Strategy
- [x] `tests/application/logging_session/test_queries.py` — unit tests for
      `CheckForResumableSessionQuery` against a fake
      `LoggingSessionRepository` per design.md § Testing Strategy
- [x] `tests/infrastructure/repositories/test_file_logging_session_repository.py`
      — integration tests for `FileLoggingSessionRepository` round-trips
      (`save` → `find_unfinished`, `archive` renames without deleting)
      against a temp directory per design.md § Testing Strategy
- [x] `tests/infrastructure/adif/test_adif_file_exporter.py` — tests for
      `AdifFileExporter.export()` against a golden ADIF sample for a
      couple of representative QSOs, including a band-boundary frequency,
      per design.md § Testing Strategy
- [x] `tests/api/test_qso_entry_form_widget.py` — pytest-qt tests for
      `QsoEntryFormWidget`: pre-fill from an `EntryDefaultsDto`, CALL
      receives focus, submit emits the expected `SubmitQsoRequest` per
      design.md § Testing Strategy
- [x] `tests/api/test_qso_list_widget.py` — pytest-qt tests for
      `QsoListWidget` rendering appended `QsoDto` rows in order per
      design.md § Testing Strategy
- [x] `tests/api/test_session_resume_prompt_dialog.py` — pytest-qt tests
      for `SessionResumePromptDialog`'s resume/start-clean choice per
      design.md § Testing Strategy
- [x] `tests/api/test_qso_entry_controller.py` — pytest-qt tests for
      `QsoEntryController`: a `SubmitQsoCommand` failure shows an inline
      error and preserves the form's typed values; "Generate ADIF" invokes
      `GenerateAdifCommand` with the chosen destination per design.md §
      Testing Strategy
- [x] `tests/api/test_main_window.py` — pytest-qt tests for `MainWindow`'s
      startup flow: the resume/start-clean prompt is shown only when
      `CheckForResumableSessionQuery` returns `True`, and each choice
      invokes the correct command per design.md § Testing Strategy

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
