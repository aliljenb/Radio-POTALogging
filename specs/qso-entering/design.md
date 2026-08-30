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

**Amendment (Story 5, added after initial implementation)**: CALL is
always uppercase. This is enforced in exactly two places — the `Qso`
value object itself (so every `Qso`, however constructed, has an
uppercase `call`: freshly submitted, or loaded back from a resumed
session file that predates this change) and the entry form's CALL field
(so the operator sees uppercase as they type, before submission even
happens). Because the value object itself enforces it, neither
`FileLoggingSessionRepository` nor `AdifFileExporter` need any change —
by the time either sees a `Qso`, its `call` is already normalized.

**Amendment (Story 6, added after initial implementation)**: before any
clean session begins — a first-ever launch with no previous session file,
or "Start Clean" chosen after the resume prompt — a new
`SessionSetupDialog` collects the POTA park reference, date, and start
time from the operator, with "OK" (only once a park reference is typed)
and "Quit" (exits the whole application) actions. This requires
extracting "decide how the session starts, and whether to start the app
at all" out of `MainWindow` (which today runs that logic in its own
constructor) into a new `session_bootstrap.bootstrap_session()` step that
runs *before* `MainWindow` is constructed — so "Quit" can exit cleanly
without ever building or flashing a half-initialized main window.
`MainWindow` now just renders a `SessionStartResult` it's handed; it no
longer knows about the resume prompt, the setup dialog, or any of the
three startup commands/query directly.

**Amendment (Story 6 extension, added after Story 6 was implemented)**:
`SessionSetupDialog` gains a fourth field, "Frequency", required
(non-empty) exactly like the park reference — "OK" is disabled until both
are filled in. It is **not** format/band-validated in the dialog; it
flows straight through to `StartNewSessionCommand` and becomes the new
session's FREQ pre-fill, using the same decimal-MHz-string convention
FREQ has always used. This mirrors the park-reference wiring exactly: one
more field threaded through `SessionSetupResult` →
`StartNewSessionCommand.execute()` → `LoggingSession.start()` →
`EntryDefaults.seed()`.

**Amendment (Story 7, added after Story 6 was implemented)**: MY_SIG_INFO
is always uppercase, extending Story 5's CALL pattern to a second field.
Enforced in three places, one more than CALL needed:

1. `Qso.__post_init__` gains the same `.upper()` normalization for
   `my_sig_info` it already applies to `call`.
2. `EntryDefaults` gets its **own** `__post_init__` doing the same thing —
   this is the one non-obvious part. `LoggingSession.record_qso` builds
   `next_entry_defaults` from the *raw* `my_sig_info` parameter it was
   called with, not from `qso.my_sig_info` (the normalized one) — so
   `Qso`'s normalization alone would not guarantee the *carried-forward*
   value on the next form is uppercase. Giving `EntryDefaults` the same
   defensive `__post_init__` closes that gap without having to touch
   `record_qso`'s carry-forward logic at all, and also covers
   `EntryDefaults.seed()` (the first-entry case) the same way.
3. A new small shared helper, `api/uppercase_field.py`'s
   `uppercase_as_typed(line_edit)`, gives a `QLineEdit` the
   live-uppercase-while-typing behavior — connecting `textEdited`,
   preserving cursor position. `QsoEntryFormWidget` applies it to both
   CALL and MY_SIG_INFO; `SessionSetupDialog` applies it to the park
   reference field. This is a small refactor of Story 5's original
   `QsoEntryFormWidget._uppercase_call` (now removed) into a shared,
   three-times-reused utility — the identical logic was about to appear a
   third time, past the point where a private per-widget method still
   made sense.

**Amendment (Story 8, added after Story 7 was implemented)**: OPERATOR is
always uppercase — the exact same three-place pattern as Story 7's
MY_SIG_INFO, since OPERATOR is carried forward between entries the same
way: `Qso.__post_init__` and `EntryDefaults.__post_init__` both gain the
same `.upper()` normalization for `operator`, and `QsoEntryFormWidget`
applies `uppercase_as_typed()` to the OPERATOR field. No new questions —
this is mechanical repetition of an already-implemented pattern.

**Amendment (Story 9, added after Story 7 was implemented)**: MODE
becomes a fixed two-option dropdown ("CW"/"SSB", defaulting to "CW")
instead of free text. Unlike Stories 5/7/8, this isn't a normalization
problem — it's a UI-control-type change enforced entirely by using a
non-editable `QComboBox` instead of a `QLineEdit`; the only reason
anything other than "CW"/"SSB" could ever have reached MODE was that it
was free text, so removing the free-text entry point closes the gap
completely, no domain-level validation/exception needed (unlike FREQ,
MODE drives no further domain computation such as BAND derivation). The
allowed values live in one place — a new `MODE_OPTIONS` constant in the
domain layer, since "these are the two supported modes" is a business
fact of this application, not a UI whim — and the widget populates its
`QComboBox` from it, so UI and domain can't drift apart. `api/` never
imports `domain/` directly anywhere else in this codebase (per
`.claude/rules/domain-driven-design.md`'s `api → application → domain`
layering), so `MODE_OPTIONS` is re-exported from
`application/logging_session/dto.py` (which already imports it from
`domain/` — application depending on domain is fine) and the widget
imports it from there instead. MODE was already carried forward as a
plain string with no normalization gap (Story 2's existing carry-forward
already copies the operator's dropdown selection
verbatim), so no `EntryDefaults`/`Qso` changes are needed here at all.

**Amendment (Story 10, added after Story 9 was implemented)**: `MainWindow`
sizes itself to half the primary display's width and height at
construction, instead of relying on Qt's default "fit to content" size.
This is UI-only — no domain/application change. `MainWindow.__init__`
reads `QApplication.primaryScreen().availableGeometry()` (the screen
`QApplication` considers primary at the moment the window is built — the
same screen `composition_root.main()`'s already-running `QApplication`
instance is attached to) and calls `self.resize(width // 2, height // 2)`
once, after building its layout. If `primaryScreen()` returns `None` (no
screen attached — not expected outside of unusual headless setups), the
resize is skipped and Qt's default size stands rather than raising; this
is a defensive fallback, not a behavior the requirements describe, so it's
not covered by an acceptance criterion. `SessionSetupDialog` is
unaffected (requirements explicitly scope this to the main window only).

**Amendment (Story 11, added after Story 9 was implemented)**: pressing
Enter/Return while any of the 11 entry-form fields has focus submits the
QSO, the same as clicking "Submit" — but only when CALL is non-empty;
otherwise it's a no-op. A single `QLineEdit.returnPressed` signal doesn't
cover this, because three of the eleven fields aren't `QLineEdit`s
(`QComboBox` for MODE, `QDateEdit`/`QTimeEdit` for QSO_DATE/TIME_ON) and
none of those emit `returnPressed`. Instead, `QsoEntryFormWidget` installs
itself as an event filter (`installEventFilter(self)`) on all 11 field
widgets and implements `eventFilter(obj, event)`: on a `QEvent.Type.KeyPress`
whose key is `Qt.Key.Key_Return` or `Qt.Key.Key_Enter`, it calls a new
`_on_enter_pressed()` method and returns `True` (consuming the event, so a
date/time spinbox's own Enter handling never fires) — for any other event
it returns `super().eventFilter(obj, event)` unchanged. `_on_enter_pressed()`
calls the existing `_on_submit_clicked()` only `if self._call.text():`,
otherwise does nothing — this empty-CALL guard is new and Enter-specific;
per requirements Story 11's third criterion, the Submit *button*'s
behavior is deliberately left unchanged (it still has no empty-CALL check,
same as today), so `_on_submit_clicked()` itself is not modified — the
guard lives only in `_on_enter_pressed()`, the new method that calls it.

**Amendment (Story 2 RST reset, added after Story 11 was implemented)**:
RST_SENT and RST_RCVD stop being carried forward. `LoggingSession.record_qso`
already builds `next_entry_defaults` by hand rather than deriving it from
the just-recorded `Qso` — the fix is entirely local to that construction
call: use `StationDefaults.rst_sent`/`StationDefaults.rst_rcvd` (the fixed
`"599"` constants) instead of the `rst_sent`/`rst_rcvd` parameters
`record_qso` was called with. This is the exact same pattern already used
one line above for `my_sig` (`my_sig=StationDefaults.my_sig` on the `Qso`
construction) — a class-level default accessed directly off the frozen
dataclass, no instance needed. The just-submitted `Qso` itself is
unaffected: it still stores whatever RST_SENT/RST_RCVD the operator
actually typed (including an edited, non-"599" value) — only the *next
form's* pre-fill reverts to "599". No API-layer change is needed: the
widget already renders whatever `EntryDefaultsDto.rst_sent`/`.rst_rcvd`
it's given.

**Amendment (Story 10 height fraction, added after Story 11 was
implemented)**: the already-implemented `MainWindow.__init__` resize
changes from half-height to three-quarters-height. One-line change:
`geometry.height() // 2` becomes `geometry.height() * 3 // 4` (integer
division on the scaled value, same style as the existing width
calculation, which is unaffected — width stays `geometry.width() // 2`).

**Amendment (Story 12, added after Story 11 was implemented)**: the 11
entry fields are reordered, both visually and in Tab order, to CALL,
RST_RCVD, RST_SENT, TIME_ON, FREQ, MY_SIG_INFO, QSO_DATE, MODE, OPERATOR,
MY_RIG, TX_PWR. Two changes to `QsoEntryFormWidget.__init__`:

1. The widget-construction statements and the `form.addRow(...)` calls are
   both reordered to read top-to-bottom in the new field order — one
   source of truth for "what order do these fields appear in the code",
   matching what the operator sees.
2. An explicit `QWidget.setTabOrder(...)` chain is added right after the
   layout is built, chaining all 11 fields in the same new order. This is
   the one non-obvious part: Qt's *default* Tab order for a `QFormLayout`
   is derived from child widget insertion order, which in practice already
   tends to follow `addRow()` call order — but that's an implicit
   Qt-internal behavior, not a guarantee this design wants to depend on.
   An explicit `setTabOrder()` chain makes the Tab order a directly-stated
   fact of the code, immune to any future refactor of how/when widgets get
   added to the layout.

No domain/application change — this is a pure API-layer reordering, like
Story 9's control-type swap. The `QFormLayout` instance, previously a
local variable inside `__init__`, is kept as `self._form` so a test can
walk its rows and assert the display order directly — the same
"reach into a private attribute" pattern the existing tests already use
for `widget._call`, `widget._mode`, etc.

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
| `EntryDefaults` | `operator, mode, my_sig_info, rst_sent, rst_rcvd, freq, my_rig, tx_pwr, timestamp: QsoTimestamp` (everything a future form pre-fills **except CALL**) | Two ways to obtain one: `EntryDefaults.seed(StationDefaults, now, my_sig_info="", freq="")` (QSO_DATE/TIME_ON = now; `my_sig_info`/`freq` each default to `""` but are passed as the operator's park reference and starting frequency for a brand-new session — Story 6) for a brand-new session, or `LoggingSession.record_qso(...)` derives the next one by carrying every field forward from the just-submitted QSO **except `rst_sent`/`rst_rcvd`, which are always reset to `StationDefaults.rst_sent`/`.rst_rcvd` ("599") instead of being carried forward (Story 2 RST reset amendment)** and advancing the timestamp by 2 minutes; **`my_sig_info` and `operator` are each normalized to uppercase in its own `__post_init__`** (same `object.__setattr__` pattern as `Qso`), independent of `Qso`'s normalization — see the Story 7 amendment note under Overview for why both are needed (Story 8 repeats it for `operator`) |
| `Qso` | `call, timestamp: QsoTimestamp, mode, my_sig, my_sig_info, rst_sent, rst_rcvd, freq: Frequency, operator, my_rig, tx_pwr` | Immutable once created via `LoggingSession.record_qso`; `time_off` is always read as equal to `timestamp.time_on` (no separate stored field, so the invariant can't drift); `band` is a derived property (`freq.band`), never stored redundantly; **`call`, `my_sig_info`, and `operator` are each normalized to uppercase in `__post_init__`** (`object.__setattr__`, since the dataclass is frozen) — non-letter characters (digits, `/`, `-`) pass through unchanged because `str.upper()` only affects cased characters; this runs for every `Qso`, including ones deserialized from a persisted session file (requirements Story 5 for `call`, Story 7 for `my_sig_info`, Story 8 for `operator`) |
| `MODE_OPTIONS` | module-level constant, `("CW", "SSB")` | not a class — a fixed tuple defined once in `value_objects.py`; the single source of truth for which MODE values exist, populating the entry form's dropdown (Story 9); `StationDefaults.mode` (`"CW"`) is always one of these values; re-exported from `application/logging_session/dto.py` since `api/` never imports `domain/` directly (see the Story 9 amendment note under Overview) |

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
| `StartNewSessionCommand` | `park_reference: str`, `freq: str` (plus existing `qso_date`/`time_on` keyword args — no formal DTO, same as before) | `LoggingSessionRepository.archive()` (if an unfinished session exists), then a fresh `LoggingSession.start(StationDefaults, now, my_sig_info=park_reference, freq=freq)` | `SessionStartResult` (seeded `EntryDefaults`, empty QSO list) |
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
- `MODE_OPTIONS` — not a DTO, but re-exported here from `domain/logging_session/value_objects.py`
  (Story 9) so `api/` can populate the MODE dropdown without importing
  `domain/` directly.

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
| App startup (`composition_root.main()`, before `MainWindow` exists) | `session_bootstrap.bootstrap_session()`: `CheckForResumableSessionQuery`, then `ResumeSessionCommand` or `StartNewSessionCommand` | Shows `SessionResumePromptDialog` only if the query returns `True`; always shows `SessionSetupDialog` before `StartNewSessionCommand` (Story 6). If the operator clicks "Quit" on the setup dialog, `bootstrap_session()` returns `None` and `main()` exits without constructing `MainWindow` |
| QSO form "Submit" button | `SubmitQsoCommand` | On `FrequencyFormatError`/`FrequencyOutOfBandError`, shows an inline error and leaves the form as typed |
| "Generate ADIF" button | `GenerateAdifCommand` | Available from a persistent toolbar/button, not tied to form state; destination path comes from a native "Save File" dialog, defaulting to a filename derived from the session's start date |

### Components (PyQt, under `api/`)

| Component | Responsibility | Consumes |
|-----------|-----------------|------------------------|
| `MainWindow` | Host the form, the QSO list, and the "Generate ADIF" action, rendering the `SessionStartResult` it's given at construction; size itself to half the primary screen's width and three-quarters its height at construction (Story 10) | none of the startup commands/query directly — just the `SessionStartResult` passed in, plus `submit_qso`/`generate_adif` for `QsoEntryController` |
| `SessionResumePromptDialog` | Ask the operator, once at startup, to resume or start clean | none (pure dialog; the choice drives which branch `bootstrap_session()` takes) |
| `SessionSetupDialog` | Collect the park reference, date, start time, and starting frequency for a new session, or report that the operator chose to quit; disable "OK" while the park reference or frequency is empty; uppercase the park reference live as typed via `uppercase_as_typed()` (Story 7) (Story 6) | none (pure dialog; exposes `.setup_result: SessionSetupResult \| None` after `.exec()` — named to avoid shadowing `QDialog`'s own `.result()` method, the same reason `SessionResumePromptDialog` uses `.choice`) |
| `session_bootstrap.bootstrap_session()` | Run the startup sequence (resume prompt if applicable, then either resume or the setup dialog + `StartNewSessionCommand`) and decide whether the app should proceed at all | `CheckForResumableSessionQuery`, `ResumeSessionCommand`, `StartNewSessionCommand`; shows `SessionResumePromptDialog`/`SessionSetupDialog` |
| `uppercase_field.uppercase_as_typed(line_edit)` | Make one `QLineEdit` uppercase its text live as the operator types, preserving cursor position (Story 5/7) | none (pure Qt helper; called once per field during widget `__init__`) |
| `QsoEntryFormWidget` | Render the 11 entry fields, in the order CALL, RST_RCVD, RST_SENT, TIME_ON, FREQ, MY_SIG_INFO, QSO_DATE, MODE, OPERATOR, MY_RIG, TX_PWR, and emit the submitted values (Story 12); apply a new `EntryDefaultsDto` to pre-fill itself and focus CALL; uppercase CALL, MY_SIG_INFO, and OPERATOR live as the operator types, via `uppercase_as_typed()` (requirements Story 5, 7, 8); render MODE as a non-editable `QComboBox` populated from `MODE_OPTIONS`, defaulting to "CW" (Story 9); submit on Enter/Return from any field when CALL is non-empty, via an `eventFilter` installed on all 11 fields (Story 11); Tab through the 11 fields in the same fixed order via an explicit `setTabOrder()` chain (Story 12) | emits `SubmitQsoRequest` via a Qt signal |
| `QsoListWidget` | Display submitted QSOs, in order, read-only | renders `QsoDto` rows appended to it |
| `QsoEntryController` | Wire widget signals to application commands/queries and route results/errors back to the widgets | `SubmitQsoCommand`, `GenerateAdifCommand` |
| `composition_root.py` (`main`) | Construct the concrete adapters, run `bootstrap_session()`, and — only if it returns a result rather than `None` — construct/show `MainWindow` and run the Qt event loop | — |

`SessionSetupResult` (`park_reference: str, qso_date: date, time_on: time,
freq: str`) is a small frozen dataclass local to `session_setup_dialog.py`
— a UI-boundary carrier, not an application DTO, since nothing outside
`bootstrap_session()` needs to know about it; `bootstrap_session()` unpacks
it into `StartNewSessionCommand.execute()`'s plain keyword arguments.

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
| `MainWindow` | Host the feature's widgets, given an already-decided starting state |
| `SessionResumePromptDialog` | Ask one yes/no-shaped question at startup |
| `SessionSetupDialog` | Collect park reference/date/time/frequency for a new session, or report "quit" |
| `session_bootstrap.bootstrap_session()` | Decide how (or whether) the session starts, before any window exists |
| `uppercase_field.uppercase_as_typed()` | Make one `QLineEdit` uppercase itself live as typed |
| `QsoEntryFormWidget` | Render/collect the entry form's fields |
| `QsoListWidget` | Render the submitted-QSO list |
| `QsoEntryController` | Mediate between UI signals and application commands |
| `composition_root` | Assemble the object graph and run bootstrap, then the app, at startup |

## Testing Strategy

Mirrors `src/` under `tests/`.

- **Domain** (`tests/domain/logging_session/`): no mocks/infra. Table-driven
  tests for `Frequency` (every band-plan row's boundaries + values outside
  all rows), `QsoTimestamp.plus_two_minutes()` (including a midnight
  rollover case), and `LoggingSession.record_qso` (TIME_OFF==TIME_ON,
  defaults carried forward correctly except CALL, first-entry seeding from
  `StationDefaults`). Story 5: `Qso(call="w1aw/p", ...).call ==
  "W1AW/P"` — mixed case and lowercase input normalized, digits and `/`
  unaffected. Story 6: `EntryDefaults.seed(StationDefaults(), now,
  my_sig_info="K-1234", freq="14.062").my_sig_info == "K-1234"` and
  `.freq == "14.062"`, and `LoggingSession.start(StationDefaults(), now,
  my_sig_info="K-1234", freq="14.062").next_entry_defaults` matches both;
  existing seed/start tests without `my_sig_info`/`freq` arguments keep
  passing since each defaults to `""`. Story 7:
  `Qso(my_sig_info="k-1234", ...).my_sig_info == "K-1234"` (mixed
  case/lowercase normalized, digits/`-` unaffected — table-driven like the
  CALL case); `EntryDefaults.seed(StationDefaults(), now,
  my_sig_info="k-1234").my_sig_info == "K-1234"`; and
  `LoggingSession.record_qso(..., my_sig_info="k-1234",
  ...).next_entry_defaults.my_sig_info == "K-1234"` — this last one is the
  regression test for the "raw parameter vs. `qso.my_sig_info`" gap
  described in the Story 7 amendment note. Story 8: the identical set of
  three tests repeated for `operator` instead of `my_sig_info` (normalize
  on `Qso`, normalize on `EntryDefaults.seed`, and the `record_qso`
  carry-forward regression test). Story 9: `MODE_OPTIONS == ("CW",
  "SSB")` — a direct assertion on the fixed tuple's contents and order.
  Story 2 RST reset: `LoggingSession.record_qso(..., rst_sent="579",
  rst_rcvd="588", ...).next_entry_defaults.rst_sent == "599"` and
  `.rst_rcvd == "599"` — proves the *edited* values submitted on this QSO
  do **not** carry forward, unlike every other field; the existing
  `test_record_qso_carries_defaults_forward_except_call_and_advances_time_on`
  test (which submits `rst_sent="599", rst_rcvd="599"` already) is
  unaffected since it never exercised a non-default value.
- **Application** (`tests/application/logging_session/`): each command/query
  tested against fake `LoggingSessionRepository`/`AdifExporter` doubles —
  no real file I/O. Story 6: `StartNewSessionCommand(...).execute(...,
  park_reference="K-1234", freq="14.062")` — the returned
  `SessionStartResult`'s `entry_defaults.my_sig_info` is `"K-1234"` and
  `entry_defaults.freq` is `"14.062"`.
- **Infrastructure** (`tests/infrastructure/`): `FileLoggingSessionRepository`
  round-trips (save → find_unfinished, archive renames without deleting)
  against a temp directory; `AdifFileExporter` output checked against a
  golden ADIF sample for a couple of representative QSOs (including a
  band-boundary frequency). Story 5: a session JSON file with a
  lowercase-stored `call` (simulating data from before this change) is
  loaded via `find_unfinished()` and asserted to come back uppercase,
  since normalization happens in `Qso.__post_init__` on construction
  regardless of where the value came from. Story 7: the same test
  repeated for a lowercase-stored `my_sig_info`.
- **GUI** (`tests/api/`): widget-level tests using **pytest-qt** (approved
  exception to `.claude/rules/testing.md`'s Playwright rule for this
  feature — Playwright cannot drive a PyQt window; recorded in
  `.claude/rules/tech.md`'s decision log). Cover: form pre-fill on
  `EntryDefaultsDto` application, focus-on-CALL after submit, an inline
  error appearing (form preserved) when `SubmitQsoCommand` raises, and
  (Story 5) typing lowercase into CALL displays uppercase immediately.
  Story 7: a new `test_uppercase_field.py` covers `uppercase_as_typed()`
  directly against a bare `QLineEdit` (lowercase typed → displays
  uppercase; cursor position preserved after a mid-string edit); typing
  lowercase into MY_SIG_INFO on `QsoEntryFormWidget` and into the setup
  dialog's park reference field both display uppercase immediately, the
  same way CALL already does. Story 8: the same live-uppercase test
  repeated for the OPERATOR field. Story 9: the MODE `QComboBox` offers
  exactly `["CW", "SSB"]` as its items and is not editable;
  `apply_defaults()` with `mode="SSB"` sets the combo box's current text
  to `"SSB"`; clicking Submit with "SSB" selected includes `mode="SSB"`
  in the emitted `SubmitQsoRequest` — replacing the free-text assumption
  in the existing pre-fill/submit tests, which already assert `mode ==
  "CW"` (the always-present default) and keep passing unchanged.
  `test_main_window.py` is simplified to just constructing `MainWindow`
  with a `SessionStartResult` and asserting the widgets render it — the
  startup-flow tests it used to hold move to a new
  `test_session_bootstrap.py` (Story 6): no resumable session → the setup
  dialog is shown directly (not the resume prompt) and its values reach
  `StartNewSessionCommand`; a resumable session + "Resume" chosen → only
  `ResumeSessionCommand` runs, no setup dialog; a resumable session +
  "Start Clean" chosen → the setup dialog then runs
  `StartNewSessionCommand`; "Quit" clicked on the setup dialog (from
  either path) → `bootstrap_session()` returns `None`, no command runs. A
  new `test_session_setup_dialog.py` covers: "OK" starts disabled and
  becomes enabled once the park reference field is non-empty, clicking
  "OK" produces a `.setup_result` with the three entered values, and
  clicking "Quit" produces `.setup_result is None`. Story 6 extension: "OK"
  also requires the Frequency field to be non-empty — it stays disabled
  with a park reference but empty Frequency (and vice versa), and only
  enables once both are filled in; `.setup_result.freq` reflects the
  entered value. `test_session_bootstrap.py`'s fakes/assertions gain a
  `freq` value flowing from the setup dialog into `StartNewSessionCommand`.
  Story 10: constructing `MainWindow` and reading `.size()` back asserts
  its width equals half, and its height three-quarters, of
  `QApplication.primaryScreen().availableGeometry()`'s width/height at
  construction time (the `offscreen` QPA platform used for headless test
  runs still reports a concrete screen geometry, so this is deterministic
  in CI) — the existing test is **modified** in place to assert the new
  height fraction rather than adding a second test. Story 11: with the
  form pre-filled and CALL set non-empty, pressing Enter while focus is in
  a *non-CALL* field (e.g. MY_RIG) still emits `submitted` — proving the
  "any field" behavior, not just CALL's own key handling; pressing Enter
  while CALL is empty emits nothing (`qtbot.waitSignal(...,
  raising=False)` times out) and leaves the other fields' values
  unchanged; pressing Enter in CALL itself (now non-empty) also emits,
  matching the button-click test's existing assertions on the emitted
  `SubmitQsoRequest`. Story 12: reading `widget._form`'s 11 rows' label
  text, in order, equals `["CALL", "RST_RCVD", "RST_SENT", "TIME_ON",
  "FREQ", "MY_SIG_INFO", "QSO_DATE", "MODE", "OPERATOR", "MY_RIG",
  "TX_PWR"]`; separately, walking the Tab chain from `widget._call` via
  repeated `.nextInFocusChain()` calls visits the 11 field widgets
  (`widget._call, widget._rst_rcvd, ...`) in that same order — a
  black-box check of the `setTabOrder()` chain's actual effect, not just
  that the calls were made.

## Open Questions / Risks

None currently outstanding for the Story 2 RST reset, the Story 10 height
fraction change, or Story 12. All three open questions from
`requirements.md` are resolved by the amendment notes under Overview: the
RST reset is a one-line change to `record_qso`'s `next_entry_defaults`
construction, reusing the existing `StationDefaults.rst_sent`/`.rst_rcvd`
class-level constants the same way `my_sig` already does; the height
fraction is a one-token change (`// 2` → `* 3 // 4`) to the
already-implemented resize call; Story 12 combines a straightforward
reordering of existing code with an explicit `setTabOrder()` chain, chosen
specifically because it doesn't rely on Qt's implicit default Tab-order
behavior — there was no reasonable alternative once "don't depend on
undocumented Qt internals" was the guiding principle.

None currently outstanding for Story 10 or Story 11. Both open questions
from `requirements.md` are resolved by the amendment notes under Overview:
Story 10 uses `QApplication.primaryScreen().availableGeometry()`, read
once in `MainWindow.__init__` right after the layout is built; Story 11
uses an `eventFilter` installed on all 11 field widgets (not per-widget
`returnPressed` connections, since `QComboBox`/`QDateEdit`/`QTimeEdit`
don't have that signal), sharing the empty-CALL guard in a new
`_on_enter_pressed()` method that calls the existing
`_on_submit_clicked()` rather than duplicating its field-reading logic.

None currently outstanding for Story 8 or Story 9. Story 8 is a
mechanical repeat of Story 7's already-implemented pattern for a third
field. Story 9 is a genuinely different kind of change (a UI control
swap, not a normalization) but has exactly one reasonable shape: a
non-editable `QComboBox` sourced from a single domain-level constant, so
UI and domain can't drift apart — there is no real alternative design to
weigh.

None currently outstanding for Story 7. The one genuine subtlety —
`EntryDefaults` needing its own `__post_init__` rather than relying on
`Qso`'s — is fully explained in the Story 7 amendment note under Overview
and covered by a dedicated regression test in § Testing Strategy;
everything else is a direct repeat of Story 5's already-implemented
pattern (`__post_init__` normalization plus a live-uppercase widget
handler), now shared via `uppercase_field.uppercase_as_typed()` instead of
being copy-pasted a third time.

None currently outstanding for the Story 6 Frequency extension either —
it's a mechanical repeat of the park-reference wiring already implemented
(one more required field, threaded through the same four call sites), with
no new architectural decision to make.

None currently outstanding for Story 6 itself. This amendment is more invasive
than Story 5's — it changes `MainWindow`'s constructor signature and
splits its previous startup-flow responsibility into a new
`session_bootstrap.py` module — but the change is mechanical and has one
clear correct shape (see the Story 6 amendment note under Overview for
why: "Quit" must be able to exit before any window is shown, which rules
out keeping the flow inside `MainWindow.__init__`). No ambiguity remains
to resolve before implementation.

All four questions raised during the original design review are resolved:

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
