# Design: adif-generation

## Status

- [x] Draft
- [x] In Review
- [x] Approved

## Overview

Most of this feature already exists: `LoggingSession.qsos` are formatted
into ADIF 3.x text by `AdifFileExporter` (an adapter for the domain's
`AdifExporter` port) and written to a path the operator picks via a native
save-file dialog, wired through `GenerateAdifCommand`. This design adds
the one missing piece from requirements.md: a suggested filename
(`<QSO_DATE>-<MY_SIG_INFO>.adi`) pre-filled into that dialog. Since the
suggestion needs the session's *original* start date and park reference —
fixed for the session's lifetime, unlike `next_entry_defaults` which
mutates after every submitted QSO — the `LoggingSession` aggregate (owned
by the qso-entering feature; see `docs/domain/bounded-contexts.md`) gains
a new `SessionStart` value object, persisted alongside the rest of the
session, and a new `SuggestAdifFilenameQuery` reads it to compute the
suggestion. No changes to `AdifExporter`/`AdifFileExporter` or the ADIF
record format — those are already correct per requirements Story 1.

## Domain Model

> Pure business logic. Zero framework/infra imports. Lives under
> `src/radio_pota_logging/domain/logging_session/`.

- Bounded context: **QSO Logging** (see `docs/domain/bounded-contexts.md`)
  — this feature extends the existing `LoggingSession` aggregate rather
  than introducing a new one.
- New/changed aggregates: `LoggingSession` gains one new field,
  `session_start: SessionStart`.
- New domain events: none — same rationale as qso-entering's design.md
  (no other part of the system needs to react asynchronously).
- Repository interface changes: none. `LoggingSessionRepository` and
  `AdifExporter` are unchanged; only what a `LoggingSession` carries (and
  therefore what `FileLoggingSessionRepository` serializes) changes.

### Aggregates

- **LoggingSession** — root: `LoggingSession` entity (unchanged
  ownership/boundary from qso-entering's design.md). This feature adds one
  more fact the aggregate must hold, not a new consistency boundary.

### Entities

| Entity | Identity | Key attributes | Invariants |
|--------|----------|-----------------|------------|
| `LoggingSession` | `SessionId` (unchanged) | adds `session_start: SessionStart` alongside the existing `qsos` and `next_entry_defaults` | `session_start` is set once, in `LoggingSession.start()`, and never reassigned by `record_qso()` — it must stay equal to the values the session began with, regardless of how many QSOs are submitted or edited afterward (requirements' "fixed for the whole session" criterion) |

### Value Objects

| Value Object | Attributes | Validation rules |
|--------------|------------|-------------------|
| `SessionStart` (new) | `qso_date: date`, `my_sig_info: str` — the QSO_DATE and park reference the operator entered in the session-setup dialog (qso-entering Story 6), captured once | `my_sig_info` is uppercased in `__post_init__`, the same normalization `EntryDefaults`/`Qso` already apply to their own `my_sig_info` — defensive, since `LoggingSession.start()` is a domain entry point that should not depend on the UI having already uppercased it |

No changes to `SessionId`, `Frequency`, `Band`, `QsoTimestamp`,
`StationDefaults`, `EntryDefaults`, `Qso`, or `MODE_OPTIONS` (all
unchanged from qso-entering's design.md).

### Domain Events

None. (Same rationale as qso-entering's design.md.)

### Domain Exceptions

None new. `FrequencyFormatError`/`FrequencyOutOfBandError` are unchanged
and unrelated to this feature's addition.

### Repository Interfaces (ports)

Unchanged — `LoggingSessionRepository` (`find_unfinished`/`save`/
`archive`) and `AdifExporter` (`export`) keep their existing signatures.
`SessionStart` travels as part of the `LoggingSession` object those
methods already take/return; no new port method is needed.

## Application Layer (Use Cases)

> Orchestrates domain objects. No framework code. Lives under
> `src/radio_pota_logging/application/logging_session/`.

- Use cases: generate an ADIF export at any time (existing;
  `GenerateAdifCommand`), suggest a default filename for that export
  (new; `SuggestAdifFilenameQuery`).

### Commands (write use cases)

| Command | Input DTO | Domain objects touched | Output |
|---------|-----------|--------------------------|--------|
| `GenerateAdifCommand` (existing, unchanged) | `destination: Path` | `LoggingSessionRepository` (read current session), `AdifExporter.export()` | `AdifExportResult` (path written, QSO count) |

`StartNewSessionCommand` (owned by qso-entering) changes internally: its
call to `LoggingSession.start(...)` now also populates `session_start`
from the same `qso_date`/`park_reference` arguments it already receives —
no new parameters, no DTO change, no change to its own tests' inputs or
outputs.

### Queries (read use cases)

| Query | Input | Output DTO |
|-------|-------|------------|
| `SuggestAdifFilenameQuery` (new) | none | `str` — `f"{session.session_start.qso_date:%Y%m%d}-{session.session_start.my_sig_info}.adi"` for the current session, following the same "no formal input DTO" precedent as `CheckForResumableSessionQuery` |

Filename formatting lives here, in the application layer, rather than as
a method on `SessionStart` — this mirrors how `AdifFileExporter` (an
infrastructure adapter, not domain) owns ADIF's own string formatting;
`SessionStart` stays plain data, like `QsoTimestamp`/`StationDefaults`.
Raises the same `RuntimeError` as `GenerateAdifCommand`/`ResumeSessionCommand`
if no current session exists (`repository.find_unfinished() is None`) —
in practice unreachable from the UI, since "Generate ADIF" is only
reachable once `MainWindow` exists, which requires a session to already
be running.

### DTOs

No new DTOs. `SuggestAdifFilenameQuery` returns a plain `str`, matching
`CheckForResumableSessionQuery`'s plain `bool` — introducing a
one-field wrapper DTO for a single string would be pure ceremony.

## Infrastructure

> Everything that talks to the outside world. Lives under
> `src/radio_pota_logging/infrastructure/`.

### Persistence

`FileLoggingSessionRepository`'s `.qso_session.json` schema gains one new
top-level key, `"session_start"`, alongside the existing `"session_id"`,
`"qsos"`, and `"next_entry_defaults"`:

```json
{
  "session_start": {"qso_date": "2026-08-31", "my_sig_info": "K-1234"},
  "session_id": "...",
  "qsos": [...],
  "next_entry_defaults": {...}
}
```

`_session_to_dict`/`_session_from_dict` gain matching
`_session_start_to_dict`/`_session_start_from_dict` helpers, following the
exact pattern already used for `QsoTimestamp`/`EntryDefaults`. No
migration path for a `.qso_session.json` file written before this change
(missing `"session_start"` would `KeyError` on load) — accepted as a
non-issue per § Open Questions / Risks below, not handled with a
compatibility shim.

### Repository Implementations (adapters)

No changes to which classes exist. `FileLoggingSessionRepository` and
`AdifFileExporter` both keep their current responsibilities; only
`FileLoggingSessionRepository`'s serialized shape changes, as above.

## API Layer

> This project has no browser frontend or HTTP API — the presentation
> layer is PyQt under `src/radio_pota_logging/api/`, per
> `.claude/rules/structure.md`'s 2026-08-30 decision (same note as
> qso-entering's design.md).

### Entry points

| UI entry point | Command/Query used | Notes |
|-----------------|---------------------|-------|
| "Generate ADIF" button (existing widget, changed behavior) | `SuggestAdifFilenameQuery` (new — called first), then the existing `GenerateAdifCommand` | The save dialog's default filename argument, currently `""`, becomes the query's result; the operator can still edit or fully replace it before saving (requirements: "pre-filled default, not an enforced value") |

### Components (PyQt, under `api/`)

| Component | Responsibility | Consumes |
|-----------|-----------------|------------------------|
| `QsoEntryController.generate_adif()` (changed) | Before opening the save dialog, call the new query and pass its result as `QFileDialog.getSaveFileName`'s default-filename argument; behavior after the dialog closes (calling `GenerateAdifCommand`) is unchanged | `SuggestAdifFilenameQuery`, `GenerateAdifCommand` (constructor gains one new parameter) |
| `MainWindow.__init__` (changed) | Accept and forward the new query to `QsoEntryController`, alongside the existing `submit_qso`/`generate_adif` commands | `SuggestAdifFilenameQuery` (new constructor parameter) |
| `composition_root.main()` (changed) | Construct `SuggestAdifFilenameQuery(repository)` alongside the existing command/query wiring, and pass it through to `MainWindow` | — |

No other component changes. `QsoEntryFormWidget`, `QsoListWidget`,
`SessionResumePromptDialog`, `SessionSetupDialog`, `session_bootstrap`,
and `uppercase_field` are all untouched by this feature.

### State management

Unchanged from qso-entering's design.md — all state lives in the
`LoggingSession` aggregate; widgets/controller stay passive.

## Single Responsibility Check

| Module/Class | Single responsibility |
|---------------|-------------------------|
| `SessionStart` (new, `domain/logging_session/value_objects.py`) | Hold the two facts about a session that are fixed at its start and never change afterward |
| `SuggestAdifFilenameQuery` (new, `application/logging_session/queries.py`) | Compute a suggested export filename for the current session |
| `QsoEntryController.generate_adif()` (changed) | Still exactly one responsibility — drive the "Generate ADIF" flow — now with one more piece of data (a suggested filename) feeding the same dialog it already opened |

All other classes touched by this feature (`LoggingSession`,
`FileLoggingSessionRepository`, `MainWindow`, `composition_root.main`)
keep their existing single responsibility, unchanged from qso-entering's
design.md — this feature only adds one new fact for them to carry
through, not a new reason for any of them to change.

## Testing Strategy

Mirrors `src/` under `tests/`, matching the project's existing layout.

- `tests/domain/logging_session/test_value_objects.py` (existing file,
  new cases): `SessionStart` uppercases `my_sig_info` in `__post_init__`,
  same as `EntryDefaults`.
- `tests/domain/logging_session/test_entities.py` (existing file, new
  cases): `LoggingSession.start()` sets `session_start` from its
  `qso_date`/`my_sig_info` arguments; `record_qso()` leaves
  `session_start` unchanged before and after submitting one or more QSOs
  (including across a midnight `TIME_ON` rollover, to prove `QSO_DATE`
  drift in `next_entry_defaults` never leaks into `session_start`).
- `tests/infrastructure/repositories/test_file_logging_session_repository.py`
  (existing file, new case): round-tripping a session through
  `save()`/`find_unfinished()` preserves `session_start`.
- `tests/application/logging_session/test_queries.py` (existing file, new
  case): `SuggestAdifFilenameQuery.execute()` returns
  `"20260831-K-1234.adi"` for a session whose `session_start` is
  `SessionStart(date(2026, 8, 31), "K-1234")`, regardless of what
  `next_entry_defaults`/`qsos` currently hold.
- `tests/api/test_qso_entry_controller.py` (existing file, new case):
  `generate_adif()` passes the fake `SuggestAdifFilenameQuery`'s result as
  `QFileDialog.getSaveFileName`'s default-filename argument (the existing
  tests already fake `QFileDialog` via monkeypatching — extend the same
  fake to capture that argument).
- No new/changed tests for `AdifFileExporter`
  (`tests/infrastructure/adif/test_adif_file_exporter.py`) — the ADIF
  record format itself is unchanged by this feature.

## Open Questions / Risks

- **No migration for pre-existing `.qso_session.json` files**: a session
  file written before this change has no `"session_start"` key, so
  `_session_from_dict` will raise `KeyError` on load. Accepted as a
  non-issue: this is a single-developer, single-machine desktop tool (the
  app-launcher feature's design.md describes the same assumption — a
  fixed `.venv` on one machine, no multi-user/multi-install deployment
  story) where an in-progress activation session realistically won't
  outlive a code deployment by more than a few days; if it ever did, the
  operator would see a crash on next launch and would need to delete the
  stale `.qso_session.json` and start a new session, losing that one
  session's QSOs. No compatibility shim is added for this — matches this
  project's guidance against handling scenarios that can't practically
  occur.
