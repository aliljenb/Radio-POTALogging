# Design: qso-entering

## Status

- [x] Draft
- [x] In Review
- [x] Approved

## Overview

A single-operator PyQt desktop application built around one aggregate,
`LoggingSession`: an ordered, append-only sequence of QSOs recorded during
one POTA activation, plus the "next entry defaults" used to pre-fill the
form. Submitting a QSO is one transaction against this aggregate (validate
FREQ, derive BAND, set TIME_OFF, append, recompute next-entry defaults);
the aggregate is persisted to a JSON file in the launch directory after
every submission so a crash or restart never loses a QSO. "Generate ADIF"
is a separate, idempotent read of the current session's QSOs through an
`AdifExporter` port, independent of whether an entry is in progress.

## Domain Model

> Pure business logic. Zero framework/infra imports. Lives under
> `src/radio_pota_logging/domain/logging_session/`.

- Bounded context: **QSO Logging** (see `docs/domain/bounded-contexts.md`)
- New/changed aggregates: `LoggingSession` (new)
- New domain events: none — no other part of the system needs to react
  asynchronously to a QSO being logged; the aggregate's own state change is
  sufficient (see `.claude/rules/domain-driven-design.md`: don't introduce
  events without a driving need).
- Repository interface changes: new `LoggingSessionRepository` and
  `AdifExporter` ports.

### Aggregates

- **LoggingSession** — root: `LoggingSession` entity. Consistency boundary:
  every QSO append must (a) validate against the current session's state,
  (b) update the carried-forward entry defaults, and (c) be persisted
  atomically — so no QSO is ever accepted without also updating what the
  next form will show.

### Entities

| Entity | Identity | Key attributes | Invariants |
|--------|----------|-----------------|------------|
| `LoggingSession` | `SessionId` (UUID, assigned at creation, stable across resume) | `qsos: tuple[Qso, ...]` (append-only, ordered), `next_entry_defaults: EntryDefaults` | Every contained `Qso.time_off == Qso.time_on`; every `Qso.freq` maps to a `Band`; `qsos` only ever grows, never reorders or removes (matches requirements' "no edit/delete" out-of-scope item) |

### Value Objects

| Value Object | Attributes | Validation rules |
|--------------|------------|-------------------|
| `SessionId` | wraps a UUID | generated once at session creation; opaque, immutable |
| `Frequency` | decimal MHz value | parsed from a string like `"14.062"`; raises `FrequencyFormatError` if not a valid decimal; `.band` property raises `FrequencyOutOfBandError` if no table row matches |
| `Band` | one of `160M, 80M, 40M, 30M, 20M, 17M, 15M, 12M, 10M, 6M` | constructed only via `Frequency.band`; never built directly from user input |
| `QsoTimestamp` | `qso_date: date`, `time_on: time` (both UTC, no tz conversion) | `.plus_two_minutes()` returns a new `QsoTimestamp`, using `datetime` arithmetic so a midnight rollover advances `qso_date` for free |
| `StationDefaults` | `operator, mode, my_sig, rst_sent, rst_rcvd, my_rig, tx_pwr` | fixed application constants (`SM6Y`, `CW`, `POTA`, `599`, `599`, `Elecraft KX2`, `5`); immutable, defined once in the domain layer |
| `EntryDefaults` | `operator, mode, my_sig_info, rst_sent, rst_rcvd, freq, my_rig, tx_pwr, timestamp: QsoTimestamp` (everything a future form pre-fills **except CALL**) | Two ways to obtain one: `EntryDefaults.seed(StationDefaults, now)` (QSO_DATE/TIME_ON = now, MY_SIG_INFO/FREQ empty) for a brand-new session, or `LoggingSession.record_qso(...)` derives the next one by carrying every field forward from the just-submitted QSO and advancing the timestamp by 2 minutes |
| `Qso` | `call, timestamp: QsoTimestamp, mode, my_sig, my_sig_info, rst_sent, rst_rcvd, freq: Frequency, operator, my_rig, tx_pwr` | Immutable once created via `LoggingSession.record_qso`; `time_off` is always read as equal to `timestamp.time_on` (no separate stored field, so the invariant can't drift); `band` is a derived property (`freq.band`), never stored redundantly |

### Domain Events

None. (See rationale under Aggregates/above.)

### Domain Exceptions

| Exception | Raised when |
|-----------|-------------|
| `FrequencyFormatError` | FREQ text cannot be parsed as a decimal MHz value |
| `FrequencyOutOfBandError` | FREQ parses fine but doesn't fall inside any row of the band-plan table |

### Repository Interfaces (ports)

- `LoggingSessionRepository` (`domain/logging_session/repository.py`):
  - `find_unfinished() -> LoggingSession | None` — the session left behind
    by a previous run, if any.
  - `save(session: LoggingSession) -> None` — persist after every submitted
    QSO.
  - `archive(session: LoggingSession) -> None` — set aside an unfinished
    session's persisted data (without deleting it) when the operator
    chooses to start clean.
- `AdifExporter` (`domain/logging_session/exporter.py`) — an outbound port
  for the one piece of "external data" the aggregate's QSOs need to become:
  - `export(qsos: Sequence[Qso]) -> str` — returns ADIF-formatted text for
    the given QSOs, in the fixed 14-field record shape from requirements
    Story 4. Writing that text to a filesystem path is an infrastructure
    concern (see below), not part of this port.

## Application Layer (Use Cases)

> Orchestrates domain objects. No framework code. Lives under
> `src/radio_pota_logging/application/logging_session/`.

- Use cases: check for a resumable session at startup, resume it or start
  a new one, submit a QSO, generate an ADIF export at any time.

### Commands (write use cases)

| Command | Input DTO | Domain objects touched | Output |
|---------|-----------|--------------------------|--------|
| `ResumeSessionCommand` | none | `LoggingSessionRepository.find_unfinished()` | `SessionStartResult` (existing `EntryDefaults` + all `Qso`s so far) |
| `StartNewSessionCommand` | none | `LoggingSessionRepository.archive()` (if an unfinished session exists), then a fresh `LoggingSession.start(StationDefaults, now)` | `SessionStartResult` (seeded `EntryDefaults`, empty QSO list) |
| `SubmitQsoCommand` | `SubmitQsoRequest` | `LoggingSession.record_qso(...)` (constructs `Frequency`/`QsoTimestamp`, may raise `FrequencyFormatError`/`FrequencyOutOfBandError`), then `LoggingSessionRepository.save()` | `SubmitQsoResult` (the new `EntryDefaults` for the next form + the just-submitted QSO, as `QsoDto`) |
| `GenerateAdifCommand` | `destination: Path` | `LoggingSessionRepository` (read current session), `AdifExporter.export()` | `AdifExportResult` (path written, QSO count) |

### Queries (read use cases)

| Query | Input | Output DTO |
|-------|-------|------------|
| `CheckForResumableSessionQuery` | none | `bool` — whether `LoggingSessionRepository.find_unfinished()` found anything, used to decide whether the startup prompt (Story 3) is shown at all |

No other standalone queries are introduced: the QSO list and entry defaults
needed to populate the UI are already returned as part of
`SessionStartResult`/`SubmitQsoResult` above, so a separate read-model
would just duplicate that data.

### DTOs

- `SubmitQsoRequest` — raw field values as typed/edited on the form: `call,
  qso_date, time_on, mode, my_sig_info, rst_sent, rst_rcvd, freq, operator,
  my_rig, tx_pwr` (all strings; parsed into domain value objects inside the
  command).
- `EntryDefaultsDto` — the fields to pre-fill on the next form (everything
  in `EntryDefaults`, flattened to primitives for the presentation layer).
- `QsoDto` — one row for the QSO list / ADIF export, including the derived
  `band`.
- `SessionStartResult` — `entry_defaults: EntryDefaultsDto`, `qsos:
  list[QsoDto]`.
- `SubmitQsoResult` — `entry_defaults: EntryDefaultsDto`, `submitted:
  QsoDto`.
- `AdifExportResult` — `path: Path`, `qso_count: int`.

`SubmitQsoCommand` raises the domain exceptions above rather than
returning a boolean/error-flag DTO, so the presentation layer handles
failure with a normal `try/except` and leaves the operator's in-progress
edits on screen (assumption — not specified in requirements, but the only
sane default: a rejected QSO must not force retyping).

## Infrastructure

> Everything that talks to the outside world. Lives under
> `src/radio_pota_logging/infrastructure/`.

### Persistence

No ORM/database is used, so `structure.md` no longer lists an
`infrastructure/db/` folder for this project (2026-08-30 update; the
still-empty `src/radio_pota_logging/infrastructure/db/__init__.py`
scaffold itself is removed as a `/spec-tasks qso-entering` cleanup task,
since Design phase may not touch `src/`). The session is a single JSON
file, `.qso_session.json`, in the directory the
application is launched from (per requirements Story 3). On "start clean",
the existing file is renamed to
`.qso_session.<started-at-UTC-timestamp>.json` before a new one is written,
satisfying "without discarding the previous session's persisted file."

### Repository Implementations (adapters)

- `FileLoggingSessionRepository` (`infrastructure/repositories/`) —
  implements `LoggingSessionRepository` by reading/writing the JSON file
  above.
- `AdifFileExporter` (`infrastructure/adif/`) — implements `AdifExporter`
  by formatting an ADIF 3.x record per QSO (14 fields from requirements
  Story 4) and returning the joined text; a thin
  `write_text(path, content)` call (used by `GenerateAdifCommand`'s
  caller) is the only actual file I/O, kept out of the exporter itself so
  `AdifExporter.export()` stays a pure string transform and is trivially
  unit-testable.

## API Layer

> This project has no browser frontend or HTTP API. Per
> `.claude/rules/structure.md`'s 2026-08-30 decision, the presentation
> layer is PyQt, and it lives under `src/radio_pota_logging/api/` (the
> "API Layer" below stands in for the template's Frontend Design section
> too — there's nothing to add there for this feature).

### Entry points

| UI entry point | Command/Query used | Notes |
|-----------------|---------------------|-------|
| App startup | `CheckForResumableSessionQuery`, then `ResumeSessionCommand` or `StartNewSessionCommand` | Shows `SessionResumePromptDialog` only if the query returns `True` |
| QSO form "Submit" button | `SubmitQsoCommand` | On `FrequencyFormatError`/`FrequencyOutOfBandError`, shows an inline error and leaves the form as typed |
| "Generate ADIF" button | `GenerateAdifCommand` | Available from a persistent toolbar/button, not tied to form state; destination path comes from a native "Save File" dialog, defaulting to a filename derived from the session's start date |

### Components (PyQt, under `api/`)

| Component | Responsibility | Consumes |
|-----------|-----------------|------------------------|
| `MainWindow` | Host the form, the QSO list, and the "Generate ADIF" action; run the startup resume/start-clean flow | `CheckForResumableSessionQuery`, `ResumeSessionCommand`, `StartNewSessionCommand` |
| `SessionResumePromptDialog` | Ask the operator, once at startup, to resume or start clean | none (pure dialog; the choice drives which command `MainWindow` calls) |
| `QsoEntryFormWidget` | Render the 11 entry fields and emit the submitted values; apply a new `EntryDefaultsDto` to pre-fill itself and focus CALL | emits `SubmitQsoRequest` via a Qt signal |
| `QsoListWidget` | Display submitted QSOs, in order, read-only | renders `QsoDto` rows appended to it |
| `QsoEntryController` | Wire widget signals to application commands/queries and route results/errors back to the widgets | `SubmitQsoCommand`, `GenerateAdifCommand` |
| `composition_root.py` (`main`) | Construct the concrete adapters (`FileLoggingSessionRepository`, `AdifFileExporter`) and wire them into the commands/`MainWindow` at startup | — |

### State management

All state lives in the `LoggingSession` aggregate, held by the repository
in memory for the process lifetime and flushed to disk on every `save()`.
Widgets hold no state of their own beyond what's currently rendered —
`QsoEntryController` is the only place that talks to the application
layer, so widgets stay passive/testable in isolation.

## Single Responsibility Check

| Module/Class | Single responsibility |
|---------------|-------------------------|
| `LoggingSession` | Own the invariants of one activation's QSO sequence and its next-entry defaults |
| `Frequency` | Parse and validate a MHz value and derive its `Band` |
| `QsoTimestamp` | Represent a UTC QSO date+time and compute "2 minutes later" |
| `EntryDefaults` | Represent the pre-fill template for the next entry form |
| `StationDefaults` | Hold the fixed application constants used to seed a brand-new session |
| `Qso` | Represent one immutable, submitted contact |
| `LoggingSessionRepository` | Persist/retrieve the one `LoggingSession` aggregate |
| `AdifExporter` | Turn a list of QSOs into ADIF-formatted text |
| `ResumeSessionCommand` / `StartNewSessionCommand` / `SubmitQsoCommand` / `GenerateAdifCommand` | Each: orchestrate exactly one use case against the aggregate/ports |
| `FileLoggingSessionRepository` | Read/write/archive the session JSON file |
| `AdifFileExporter` | Implement `AdifExporter` against the ADIF text format |
| `MainWindow` | Host the feature's widgets and run the startup flow |
| `SessionResumePromptDialog` | Ask one yes/no-shaped question at startup |
| `QsoEntryFormWidget` | Render/collect the entry form's fields |
| `QsoListWidget` | Render the submitted-QSO list |
| `QsoEntryController` | Mediate between UI signals and application commands |
| `composition_root` | Assemble the object graph at startup |

## Testing Strategy

Mirrors `src/` under `tests/`.

- **Domain** (`tests/domain/logging_session/`): no mocks/infra. Table-driven
  tests for `Frequency` (every band-plan row's boundaries + values outside
  all rows), `QsoTimestamp.plus_two_minutes()` (including a midnight
  rollover case), and `LoggingSession.record_qso` (TIME_OFF==TIME_ON,
  defaults carried forward correctly except CALL, first-entry seeding from
  `StationDefaults`).
- **Application** (`tests/application/logging_session/`): each command/query
  tested against fake `LoggingSessionRepository`/`AdifExporter` doubles —
  no real file I/O.
- **Infrastructure** (`tests/infrastructure/`): `FileLoggingSessionRepository`
  round-trips (save → find_unfinished, archive renames without deleting)
  against a temp directory; `AdifFileExporter` output checked against a
  golden ADIF sample for a couple of representative QSOs (including a
  band-boundary frequency).
- **GUI** (`tests/api/`): widget-level tests using **pytest-qt** (approved
  exception to `.claude/rules/testing.md`'s Playwright rule for this
  feature — Playwright cannot drive a PyQt window; recorded in
  `.claude/rules/tech.md`'s decision log). Cover: form pre-fill on
  `EntryDefaultsDto` application, focus-on-CALL after submit, the
  resume/start-clean dialog choice invoking the right command, and an
  inline error appearing (form preserved) when `SubmitQsoCommand` raises.

## Open Questions / Risks

None currently outstanding. All four raised during design review are
resolved:

- **Testing**: `pytest-qt` approved as an exception to
  `.claude/rules/testing.md`'s Playwright rule (Playwright can't drive a
  PyQt window). Added to `.claude/rules/tech.md`'s Testing section and
  decision log (2026-08-30).
- **`infrastructure/db/`**: removed from `.claude/rules/structure.md`'s
  documented layout (2026-08-30) — no ORM/database exists in this project.
  The matching empty `src/radio_pota_logging/infrastructure/db/__init__.py`
  scaffold is still on disk; deleting it is a `/spec-tasks qso-entering`
  cleanup task, since Design phase doesn't modify `src/`
  (`.claude/rules/sdd-workflow.md`).
- **PyQt version**: pinned to major version 6 (PyQt6); recorded in
  `.claude/rules/tech.md`.
- **Session file JSON shape**: intentionally left unspecified — the
  operator confirmed the exact shape doesn't matter, so it's a free
  implementation choice in `tasks.md`.
