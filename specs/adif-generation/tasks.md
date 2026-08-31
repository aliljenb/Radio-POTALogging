# Tasks: adif-generation

## Status

- [x] Draft
- [x] In Review
- [x] Approved

## How to use this file

Each task must name the exact file(s) and function/class/method it creates
or changes, and cite the design.md section it implements. Vague tasks
("wire up the backend") are not allowed — split them until each one is a
single, independently completable unit of work with a clear file target.

## Note on this feature's structure

Most of adif-generation already exists (`AdifFileExporter`,
`GenerateAdifCommand`, the "Generate ADIF" button, the 14-field ADIF
record format) — those are marked `[x]` below as already done, verified
against design.md during the design phase, with no further work. The
unchecked tasks are the one gap design.md identifies: the filename
suggestion, which needs a new `SessionStart` value object threaded through
`LoggingSession` → `FileLoggingSessionRepository` →
`SuggestAdifFilenameQuery` → `QsoEntryController`.

## Domain Layer

- [x] `src/radio_pota_logging/domain/logging_session/value_objects.py` —
      add `SessionStart` frozen dataclass (`qso_date: date`,
      `my_sig_info: str`) per design.md § Value Objects; uppercase
      `my_sig_info` in `__post_init__` via `object.__setattr__`, matching
      `EntryDefaults`'s existing normalization pattern in the same file.
- [x] `src/radio_pota_logging/domain/logging_session/entities.py` —
      add `session_start: SessionStart` field to the `LoggingSession`
      dataclass per design.md § Entities; set it in `LoggingSession.start()`
      from that method's existing `now`/`my_sig_info` arguments
      (`SessionStart(qso_date=now.qso_date, my_sig_info=my_sig_info)`);
      do **not** reassign it anywhere in `record_qso()`.

## Application Layer

- [x] `src/radio_pota_logging/application/logging_session/queries.py` —
      add `SuggestAdifFilenameQuery` (frozen dataclass holding
      `repository: LoggingSessionRepository`, same shape as the existing
      `CheckForResumableSessionQuery` in this file) per design.md §
      Queries: `.execute() -> str` reads the current session via
      `repository.find_unfinished()` (raise `RuntimeError` if `None`, same
      message style as `commands.py`'s `_require_current_session`), then
      returns
      `f"{session.session_start.qso_date:%Y%m%d}-{session.session_start.my_sig_info}.adi"`.

No changes to `commands.py` or `dto.py` — `GenerateAdifCommand` is
unchanged per design.md, and no new DTO is introduced.

## Infrastructure Layer

- [x] `src/radio_pota_logging/infrastructure/repositories/file_logging_session_repository.py`
      — per design.md § Persistence: add `_session_start_to_dict`/
      `_session_start_from_dict` helper functions (same pattern as the
      existing `_qso_timestamp_to_dict`/`_qso_timestamp_from_dict` pair in
      this file); call them from `_session_to_dict`/`_session_from_dict`
      to read/write a new top-level `"session_start"` JSON key
      (`{"qso_date": ..., "my_sig_info": ...}`) alongside the existing
      `"session_id"`, `"qsos"`, and `"next_entry_defaults"` keys. No
      migration/fallback for a missing `"session_start"` key (design.md's
      accepted Open Questions / Risks item — let it raise `KeyError`).

## API Layer

- [x] `src/radio_pota_logging/api/composition_root.py` — construct
      `SuggestAdifFilenameQuery(repository)` alongside the existing
      `generate_adif=GenerateAdifCommand(...)` wiring, and pass it into
      `MainWindow`'s constructor, per design.md § Entry points.
- [x] `src/radio_pota_logging/api/main_window.py` — add a
      `suggest_adif_filename: SuggestAdifFilenameQuery` parameter to
      `MainWindow.__init__`, and forward it to `QsoEntryController`'s
      constructor alongside the existing `submit_qso`/`generate_adif`
      arguments, per design.md § Components.
- [x] `src/radio_pota_logging/api/qso_entry_controller.py` — add a
      `suggest_adif_filename_command: SuggestAdifFilenameQuery` parameter
      to `QsoEntryController.__init__`, stored the same way as
      `self._generate_adif_command`; in `generate_adif()`, call
      `self._suggest_adif_filename_command.execute()` first and pass its
      result as the third positional argument to
      `QFileDialog.getSaveFileName(...)` (replacing the current `""`), per
      design.md § Entry points / Components.

## Tests

Mirror `src/` under `tests/`, per `.claude/rules/structure.md`.

- [x] `tests/domain/logging_session/test_value_objects.py` — add a test
      case asserting `SessionStart("K-1234"...)`-style construction with a
      lowercase `my_sig_info` stores it uppercased, per design.md §
      Testing Strategy.
- [x] `tests/domain/logging_session/test_entities.py` — add test cases:
      `LoggingSession.start(...)` sets `session_start` from its
      `qso_date`/`my_sig_info` args; `record_qso()` leaves `session_start`
      unchanged after one QSO and after a QSO whose `TIME_ON` rolls past
      midnight (proving `QSO_DATE` drift in `next_entry_defaults` doesn't
      leak into `session_start`), per design.md § Testing Strategy.
- [x] `tests/infrastructure/repositories/test_file_logging_session_repository.py`
      — add a test case: `save()` then `find_unfinished()` on the same
      repository preserves `session_start` (`qso_date` and `my_sig_info`
      both round-trip), per design.md § Testing Strategy.
- [x] `tests/application/logging_session/test_queries.py` — add a test
      case: `SuggestAdifFilenameQuery.execute()` against a fake repository
      whose session has `session_start=SessionStart(date(2026, 8, 31),
      "K-1234")` returns `"20260831-K-1234.adi"`, per design.md § Testing
      Strategy.
- [x] `tests/api/test_qso_entry_controller.py` — add a
      `FakeSuggestAdifFilenameQuery` (same style as the existing
      `FakeGenerateAdifCommand`/`FakeSubmitQsoCommand` in this file);
      extend `_make_controller`/the existing `QFileDialog.getSaveFileName`
      monkeypatch to capture its arguments; add a test case asserting
      `generate_adif()` passes the fake query's return value as the
      default-filename argument, per design.md § Testing Strategy.

No changes needed to `tests/infrastructure/adif/test_adif_file_exporter.py`
or `tests/application/logging_session/test_commands.py` — per design.md,
`AdifFileExporter` and `GenerateAdifCommand` are unaffected by this
feature.

## Task Dependencies

- `value_objects.py` (`SessionStart`) has no dependency on any other task
  in this list and should be done first.
- `entities.py` (`LoggingSession.session_start`) depends on
  `value_objects.py`'s `SessionStart` existing.
- `file_logging_session_repository.py` depends on `entities.py` (needs
  `LoggingSession.session_start` to exist to serialize/deserialize it).
- `queries.py` (`SuggestAdifFilenameQuery`) depends on `entities.py`
  (reads `session.session_start`); it does not depend on the repository
  change being done first to compile, but does need it to work correctly
  against a session loaded from disk (as opposed to one only ever kept
  in-memory within a single test).
- `composition_root.py`, `main_window.py`, and `qso_entry_controller.py`
  depend on `queries.py`'s `SuggestAdifFilenameQuery` existing, and on
  each other in that order (composition root constructs it → main window
  forwards it → controller uses it) — implement in that order.
- Each test task depends only on its corresponding implementation task
  above being done first.
