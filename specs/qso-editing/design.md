# Design: qso-editing

## Status

- [x] Draft
- [x] In Review
- [x] Approved

_Everything below through "Reusing `record_qso`'s construction path..." (the
double-click-to-edit design, Stories 1-5) was previously approved and is
already implemented. The Story 6/7 amendment (right-click-to-delete) is
appended below and to the relevant tables throughout; approved 2026-09-14.
Ready for a `/spec-tasks qso-editing` follow-up pass._

## Overview

`LoggingSession` (the same aggregate qso-entering introduced) gains one new
operation, `edit_qso(index, ...)`, that reconstructs the `Qso` at a given
position exactly the way `record_qso` already builds a new one — same
`Frequency.parse`/`.band` validation, same `Qso.__post_init__` uppercase
normalization, same derived `time_off`/`band` properties — and replaces it
in place in the `qsos` tuple, leaving `next_entry_defaults` untouched. Reusing
`record_qso`'s construction path means BAND and TIME_OFF recomputation
(requirements Story 2, Story 3) fall out for free: they are properties
derived from `freq`/`timestamp`, never stored fields, so a freshly
constructed `Qso` can't hold a stale one. On the UI side, `QsoListWidget`
becomes an editable `QTableWidget`: double-clicking a cell opens a
column-appropriate Qt editor (a plain line edit for CALL/RST_RCVD/RST_SENT,
a decimal-checked line edit for FREQ, a `QComboBox` for MODE, a `QDateEdit`
for QSO_DATE, a `QTimeEdit` for TIME_ON — all reusing the exact widget types
and helpers `QsoEntryFormWidget` already established for the same fields),
and a new `EditQsoCommand` carries the committed value through to the
aggregate the same way `SubmitQsoCommand` already does for a new QSO.

**Amendment (Stories 6-7, added after Stories 1-5 were implemented)**:
`LoggingSession` gains a second new operation, `delete_qso(index)`, that
removes the QSO at a given position outright rather than replacing it —
the direct converse of `edit_qso`, and the second (and last) way `qsos` can
now change besides `record_qso`'s append. On the UI side, `QsoListWidget`
gains a right-click context menu with a single "Delete" action: right-clicking
a row selects it (and only it — the table now restricts selection to one
whole row at a time) and offers "Delete"; choosing it asks the operator to
confirm via a plain `QMessageBox`, and only on confirmation does a new
`DeleteQsoCommand` remove the QSO and the table drop the row. The
confirmation prompt is shown by `QsoEntryController`, the same place
`generate_adif()` already shows a native `QFileDialog` — showing a dialog
before deciding whether to call a command is already this class's job, so
deletion's confirm-then-call shape needs no new component, just one more
`if`-gated command call alongside the existing one.

## Domain Model

> Pure business logic. Zero framework/infra imports. Lives under
> `src/radio_pota_logging/domain/logging_session/` (the same module
> qso-entering introduced — no new bounded context or aggregate).

- Bounded context: **QSO Logging** (see `docs/domain/bounded-contexts.md`;
  unchanged from qso-entering).
- New/changed aggregates: `LoggingSession` (changed — gains `edit_qso` and,
  per the Stories 6-7 amendment, `delete_qso`).
- New domain events: none — same reasoning as qso-entering: no other part
  of the system needs to react asynchronously to a QSO being corrected
  (`.claude/rules/domain-driven-design.md`: don't introduce events without
  a driving need).
- Repository interface changes: none. `LoggingSessionRepository.save()`
  already persists whatever `session.qsos` currently holds, with no
  assumption baked in about whether an entry was appended or replaced in
  place.

### Aggregates

- **LoggingSession** — root: `LoggingSession` entity (unchanged from
  qso-entering). The consistency boundary now also covers "correcting an
  already-recorded QSO must revalidate it the same way recording it did,
  and must never touch `next_entry_defaults`" — still one aggregate, one
  transaction per edit. The Stories 6-7 amendment extends this the same
  way for deletion: removing a QSO is one transaction, and it too must
  never touch `next_entry_defaults`.

### Entities

| Entity | Identity | Key attributes | Invariants |
|--------|----------|-----------------|------------|
| `LoggingSession` | `SessionId` (unchanged) | `qsos: tuple[Qso, ...]`, `next_entry_defaults: EntryDefaults` (unchanged) | Every contained `Qso.time_off == Qso.time_on`; every `Qso.freq` maps to a `Band` (both unchanged — `edit_qso` reconstructs a `Qso` through the identical validated path `record_qso` uses, so these hold after an edit too); **`qsos` grows via `record_qso`, has exactly one existing element replaced in place via `edit_qso`, or has exactly one existing element removed via `delete_qso` (Stories 6-7) — it is still never reordered and never has an element inserted anywhere but the end; the remaining elements' relative order is always preserved after a removal** (this relaxes qso-entering's original "never edited or removed at all" invariant, which requirements.md's Story 1/Story 6 out-of-scope lists explicitly retract for this feature, one operation at a time) |

### Value Objects

No new value object. qso-editing reuses `Frequency`, `Band`, `QsoTimestamp`,
`MODE_OPTIONS`, and `Qso` exactly as qso-entering defined them — the whole
point of routing `edit_qso` through the same construction path as
`record_qso` is that every existing normalization/validation rule
(`Qso.__post_init__`'s CALL uppercasing, `QsoTimestamp.__post_init__`'s
zero-seconds normalization, `Frequency.parse`/`.band`) applies to an edited
value with zero new code.

### Domain Events

None. (Same rationale as qso-entering — see Aggregates above.)

### Domain Exceptions

| Exception | Raised when |
|-----------|-------------|
| `FrequencyFormatError` (reused, unchanged) | An edited FREQ text cannot be parsed as a decimal MHz value |
| `FrequencyOutOfBandError` (reused, unchanged) | An edited FREQ parses fine but doesn't fall inside any row of the band-plan table |

No new exception type for an out-of-range `index`: every caller of
`edit_qso` (ultimately `QsoListWidget`, via the row the operator
double-clicked) can only ever pass an index that corresponds to a row
already rendered from `session.qsos`, so an out-of-range index would be a
programming error, not something a user action can trigger — the same
reasoning qso-entering's design already used to justify no domain exception
for an invalid MODE value reaching `record_qso`. `self.qsos[index]` simply
raises Python's built-in `IndexError` in that case. `delete_qso` (Stories
6-7) is deliberately implemented via a `list(self.qsos)` copy and `del
qsos[index]` rather than slice arithmetic (`(*qsos[:index],
*qsos[index+1:])`) specifically so that an out-of-range `index` still
raises `IndexError` the same way — Python slicing silently clips
out-of-range bounds instead of raising, which would have made `delete_qso`
the one operation in this aggregate that swallows a programming error
instead of surfacing it.

### Repository Interfaces (ports)

No changes. `LoggingSessionRepository.save(session)` (unchanged) is called
after a successful edit exactly as it already is after a successful
submission — persistence doesn't distinguish "a QSO was appended" from "a
QSO was replaced in place," since it just serializes whatever `session.qsos`
currently is.

## Application Layer (Use Cases)

> Orchestrates domain objects. No framework code. Lives under
> `src/radio_pota_logging/application/logging_session/` (unchanged module).

- Use cases: correct one field of an already-submitted QSO; remove an
  already-submitted QSO entirely (Stories 6-7).

### Commands (write use cases)

| Command | Input DTO | Domain objects touched | Output |
|---------|-----------|--------------------------|--------|
| `EditQsoCommand` | `EditQsoRequest` | `LoggingSession.edit_qso(...)` (constructs a `Frequency`/`QsoTimestamp`/`Qso` exactly like `record_qso`; may raise `FrequencyFormatError`/`FrequencyOutOfBandError`), then `LoggingSessionRepository.save()` | `EditQsoResult` (the edited QSO, as `QsoDto` — **no `entry_defaults`**, unlike `SubmitQsoResult`) |
| `DeleteQsoCommand` | `DeleteQsoRequest` | `LoggingSession.delete_qso(index)` (may raise `IndexError` for a caller bug — see § Domain Exceptions; never raises for anything a user action can trigger), then `LoggingSessionRepository.save()` | `None` — there is nothing to hand back: the row simply stops existing, and `QsoListWidget` already knows which row it asked to delete, unlike an edit (which needs the *re-derived* `QsoDto` back) |

### Queries (read use cases)

None new.

### DTOs

- `EditQsoRequest` — the 7 values the table lets the operator edit, plus
  which row: `index: int, call: str, qso_date: date, time_on: time, mode:
  str, rst_sent: str, rst_rcvd: str, freq: str`. Deliberately excludes
  `my_sig_info`, `operator`, `my_rig`, and `tx_pwr` — those aren't columns
  the table exposes (requirements.md's "Field scope" clarification), and
  `LoggingSession.edit_qso` carries them forward from the existing `Qso` at
  that index rather than taking them as input, so there's nothing for this
  DTO to hold for them in the first place.
- `EditQsoResult` — `qso: QsoDto`. Its shape (no `entry_defaults` field, in
  contrast to `SubmitQsoResult`) is what structurally guarantees
  requirements.md's "no carry-forward sync to the in-progress entry form"
  criterion (Story 5): there is nothing in this result for
  `QsoEntryController` to even apply to the entry form, so that guarantee
  doesn't depend on the controller remembering not to.

`EditQsoCommand.execute` raises `FrequencyFormatError`/`FrequencyOutOfBandError`
rather than returning a boolean/error-flag DTO, and only calls
`LoggingSessionRepository.save()` after `LoggingSession.edit_qso(...)`
succeeds — the identical pattern `SubmitQsoCommand` already uses, so the
presentation layer's existing `try/except` handling style extends to edits
with no new failure-handling shape to learn. The existing `_to_qso_dto(qso)`
helper in `commands.py` (already used by `SubmitQsoCommand`/`ResumeSessionCommand`)
is reused as-is for `EditQsoResult.qso` — no duplicate mapping code.

**`DeleteQsoRequest`** (Stories 6-7) — `index: int`, the row to remove; no
other fields, since there is nothing else for the operator to specify about
a deletion. There is deliberately **no `DeleteQsoResult`** — every other
command in this file returns a DTO because its caller needs data back
(the next form's defaults, the re-derived edited QSO, an export's path and
count); `DeleteQsoCommand` has nothing analogous to hand back, so adding an
empty result class purely for API symmetry with the other commands would be
a DTO with no data crossing the boundary, which is worse than no DTO at
all. `DeleteQsoCommand.execute` calls `LoggingSessionRepository.save()`
unconditionally after `LoggingSession.delete_qso(...)` — unlike
`EditQsoCommand`/`SubmitQsoCommand`, there is no domain exception a caller
is expected to catch (an `IndexError` here is a caller bug, not a
recoverable business failure), so no `try/except` shape needs documenting
for this command.

## Infrastructure

> Everything that talks to the outside world. Lives under
> `src/radio_pota_logging/infrastructure/` (unchanged).

### Persistence

No change. The session file's shape (`session_id`, `qsos`,
`next_entry_defaults`, `session_start`) is unaffected — `qsos` is still just
a JSON array of QSO records; an edit changes one array entry's contents,
and a deletion (Stories 6-7) removes one, both of which
`json.dumps`/`_session_to_dict` already handle generically — a shorter list
serializes exactly as readily as a same-length or longer one, with no
awareness of "append" vs. "replace" vs. "remove" needed anywhere in this
layer.

### Repository Implementations (adapters)

No change to `FileLoggingSessionRepository` — `_qso_to_dict`/`_qso_from_dict`
round-trip an edited `Qso` exactly like a freshly submitted one, since both
are just `Qso` instances with the same fields; a deletion needs no
per-`Qso` round-trip at all, since there's simply one fewer of them in the
list `_session_to_dict` iterates over.

## API Layer

> This project has no browser frontend or HTTP API — see qso-entering's
> design.md for why "API Layer" stands in for the template's Frontend
> Design section here too.

### Entry points

| UI entry point | Command/Query used | Notes |
|-----------------|---------------------|-------|
| Double-clicking a cell in one of `QsoListWidget`'s 7 columns, then committing the edit (Enter or focus-out) | `EditQsoCommand` | On success, the row's 7 cells are rewritten from the returned `QsoDto` (so e.g. a re-derived FREQ display always matches what's stored) and any previously shown error is cleared. On `FrequencyFormatError`/`FrequencyOutOfBandError`, the row is rewritten back to its pre-edit values and an error is shown — reusing `QsoEntryFormWidget.show_error()`/`.clear_error()` (the same inline error label the entry form already uses for its own FREQ errors) rather than adding a second error-display mechanism just for the table. **Assumption** (not specified in requirements — the "no prescribed error UI" is the only sane default): this reuse means an edit error appears near the entry form, not next to the table row that caused it; there's no acceptance criterion this violates, and it avoids adding new layout/widgets to `MainWindow` for a single error label. |
| Pressing Escape while a table cell is being edited | none | Native Qt behavior: `QAbstractItemView`'s built-in edit-cancel handling discards the in-progress editor without ever calling the delegate's `setModelData`, so the cell's stored text is untouched and no command runs — satisfying requirements.md Story 1's Escape criterion with no application-layer code at all. |
| Right-clicking a row, choosing "Delete" from the context menu, then confirming | `DeleteQsoCommand` | Right-clicking selects the row (and only it) and shows a context menu with one "Delete" action (Story 6). Choosing it shows a `QMessageBox.question` confirmation; on "No"/dismiss, nothing happens — no command runs, no row changes. On "Yes", `DeleteQsoCommand` runs and, only once it returns successfully, the row is removed from the table. |

### Components (PyQt, under `api/`)

| Component | Responsibility | Consumes |
|-----------|-----------------|------------------------|
| `QsoListWidget` (changed) | Render the submitted-QSO table and capture the operator's in-place cell edits and row-deletion requests for the controller to validate and apply | Emits `edited: pyqtSignal(int, EditQsoRequest)` and a new `delete_requested: pyqtSignal(int)`; gains `apply_edit(row, qso: QsoDto)`, `revert_edit(row)` (both unchanged from Stories 1-5), and a new `remove_row(row)` (drop the row from both the table and its internal cache once a deletion is confirmed) |
| `qso_table_delegates.py` (new module) | Map each of the table's 4 non-default-editable columns to its Qt editor widget | `UppercaseCallDelegate` (CALL — plain `QLineEdit`, wired through the existing `uppercase_field.uppercase_as_typed()` helper, matching requirements Story 2's "same as the entry form's CALL field"); `QsoDateDelegate` (QSO_DATE — `QDateEdit` with `.setCalendarPopup(True)`, always producing a valid calendar date, matching Story 4's "any valid calendar date, no further validation"); `TimeOnDelegate` (TIME_ON — `QTimeEdit` with `.setDisplayFormat("HH:mm")`, the identical format string `QsoEntryFormWidget`/`SessionSetupDialog` already use for TIME_ON, hiding seconds entry per Story 3); `ModeDelegate` (MODE — non-editable `QComboBox` populated via `.addItems(MODE_OPTIONS)`, matching Story 2's "same restriction as the entry form's MODE dropdown"). RST_RCVD, RST_SENT, and FREQ register no delegate and fall back to Qt's own default cell editor (a plain `QLineEdit`), since none of them need anything beyond free-text entry at the widget level (Story 2's FREQ format check and Story 4's "no restriction" for the RST fields are both enforced downstream, in `LoggingSession.edit_qso`, not in the editor) |
| `QsoEntryController` (changed) | Wire widget signals (submit, edit, delete, generate ADIF) to their application commands and route results/errors back to the widgets | Gains an `edit_command: EditQsoCommand` constructor parameter (Stories 1-5) and a new `delete_command: DeleteQsoCommand` parameter (Stories 6-7); connects `qso_list.edited` to `_on_qso_edited(row, request)` and `qso_list.delete_requested` to a new `_on_delete_requested(row)` method |
| `MainWindow` (changed) | Host the form, the QSO list, and the "Generate ADIF" action (responsibility unchanged) | Passes newly constructed `EditQsoCommand` and `DeleteQsoCommand` instances through to `QsoEntryController`, alongside the existing `submit_qso`/`generate_adif`/`suggest_adif_filename` |
| `composition_root.py` (`main`, changed) | Construct the concrete adapters and commands, run `bootstrap_session()`, then run the app (responsibility unchanged) | Constructs `EditQsoCommand(repository)` and `DeleteQsoCommand(repository)` alongside the existing `SubmitQsoCommand(repository)` and passes both into `MainWindow` |

**`QsoListWidget`'s edit-commit mechanism**, confined entirely to that
class:

1. **A guarded write helper, `_write_row(row, qso: QsoDto)`**, replaces the
   inline `setItem(...)` loop currently in `append_qso`. It wraps its 7
   `setItem` calls in `self.blockSignals(True)` / `self.blockSignals(False)`
   so that writing a row's cells — whether from `append_qso` (a brand-new
   row) or from `apply_edit`/`revert_edit` (rewriting an existing one) —
   never itself fires `cellChanged`. This is the one non-obvious mechanism
   the whole feature depends on: without it, `append_qso`'s own 7 `setItem`
   calls per row would be indistinguishable from a genuine operator edit.
2. **A per-row cache, `self._qsos: list[QsoDto]`**, mirrors what's
   currently rendered, index-aligned with both the table's rows and
   `LoggingSession.qsos` (which requirements.md's "Carry-forward sync"
   clarification and the domain invariant above both confirm never
   reorders or removes an entry — a stable row index is a safe stand-in for
   identity here, so `Qso` gains no new identity concept just for this
   feature). `append_qso` appends to it; `apply_edit`/`revert_edit` read
   and update it.
3. **`self.cellChanged.connect(self._on_cell_changed)`**, connected once in
   `__init__`, right after `setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)`
   replaces the current `NoEditTriggers`. Because of point 1,
   `cellChanged` now only ever fires for a genuine operator-committed edit.
4. **`_on_cell_changed(row, column)`** reads the just-committed cell's new
   text (`self.item(row, column).text()`), parses it to the right type for
   that column (`date.fromisoformat`/`time.fromisoformat` for
   QSO_DATE/TIME_ON, a plain string otherwise), and builds an
   `EditQsoRequest` combining that one new value with the other 6 fields
   read from `self._qsos[row]` (still the pre-edit snapshot at this point —
   `apply_edit`/`revert_edit` haven't run yet) — then emits
   `self.edited.emit(row, request)`.

`QsoEntryController._on_qso_edited(row, request)` mirrors `_on_submit`'s
existing shape:

```
try:
    result = self._edit_command.execute(request)
except (FrequencyFormatError, FrequencyOutOfBandError) as exc:
    self._form.show_error(str(exc))
    self._qso_list.revert_edit(row)
    return
self._form.clear_error()
self._qso_list.apply_edit(row, result.qso)
```

**`QsoListWidget`'s right-click-to-delete mechanism** (Stories 6-7), confined
entirely to that class:

1. **Row-only, single-row selection.** `__init__` gains
   `self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)`
   and `self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)`
   — clicking anywhere in a row selects the whole row (requirements Story
   6's "select that row"), and only one row can be selected at a time
   (requirements' confirmed "single row only" scope), so there is no
   multi-row state for the context menu to ever have to consider.
2. **A custom context menu**, the standard Qt mechanism for "right-click
   shows a menu I build myself" rather than a widget-supplied default one:
   `__init__` also calls
   `self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)` and
   connects `self.customContextMenuRequested` to a new
   `_on_context_menu_requested(pos: QPoint)` method.
3. **`_on_context_menu_requested(pos)`** computes `row =
   self.rowAt(pos.y())`; if `row < 0` (the right-click landed below the
   last row, on empty space), it returns immediately — no menu, no
   selection change, matching the fact that there is no QSO to act on.
   Otherwise it calls `self.selectRow(row)` (making the right-clicked row
   the one-and-only selection regardless of whatever was selected before —
   the standard "right-click also selects" behavior most table UIs use),
   builds a `QMenu(self)` with one `"Delete"` action, and calls
   `menu.exec(self.viewport().mapToGlobal(pos))`. If the returned action is
   the `"Delete"` one, it emits `self.delete_requested.emit(row)` — the
   menu itself makes no decision about confirming or actually deleting;
   that's `QsoEntryController`'s job, the same division of labor
   `_on_cell_changed` already has with `EditQsoCommand`.
4. **`remove_row(row)`** — called by the controller only after a deletion
   is confirmed *and* `DeleteQsoCommand` has already succeeded — does `del
   self._qsos[row]` then `self.removeRow(row)`. `QTableWidget.removeRow`
   is a structural change (it emits `rowsRemoved`, not `cellChanged`), so
   this needs no `blockSignals` guard: `_on_cell_changed` (Stories 1-5)
   simply never fires for it.

`QsoEntryController._on_delete_requested(row)`:

```
confirmed = (
    QMessageBox.question(
        self._dialog_parent,
        "Delete QSO",
        "Delete this QSO?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    == QMessageBox.StandardButton.Yes
)
if not confirmed:
    return
self._delete_command.execute(DeleteQsoRequest(index=row))
self._qso_list.remove_row(row)
```

No `try/except` here, mirroring `DeleteQsoCommand`'s own "no recoverable
business failure" shape from § DTOs above — the only way this call fails is
a caller bug (`IndexError`), which is not something a confirmation dialog
or an inline error label is the right tool to handle.

### State management

Unchanged in spirit from qso-entering: all durable state still lives in the
`LoggingSession` aggregate; `QsoEntryController` remains the only place that
talks to the application layer. `QsoListWidget.self._qsos` is new widget
state, but it holds nothing the aggregate doesn't also hold — it exists
solely so the widget can answer "what are this row's other 6 values" and
"what did this row look like before the rejected edit" without re-deriving
them from displayed cell text (which would mean parsing ISO-formatted
strings back apart, redundant with `EditQsoRequest`'s already-typed fields)
or without reaching back into the application layer for a read model that
doesn't otherwise exist. Deletion (Stories 6-7) needs nothing further from
this cache beyond `remove_row`'s `del self._qsos[row]` — there is no
pre-delete state to remember, unlike a rejected edit.

## Single Responsibility Check

| Module/Class | Single responsibility |
|---------------|-------------------------|
| `LoggingSession.edit_qso` (method, not a new class) | Same responsibility as the rest of `LoggingSession` — own the invariants of one activation's QSO sequence — extended to cover replacing an entry in place, not just appending one |
| `LoggingSession.delete_qso` (method, not a new class) | Same responsibility as the rest of `LoggingSession` — extended to cover removing an entry, not just appending or replacing one |
| `EditQsoCommand` | Orchestrate the "correct an already-submitted QSO" use case against the aggregate/ports |
| `DeleteQsoCommand` | Orchestrate the "remove an already-submitted QSO" use case against the aggregate/ports |
| `UppercaseCallDelegate` | Present and commit CALL edits through an uppercase-as-typed line edit |
| `QsoDateDelegate` | Present and commit QSO_DATE edits through a calendar date picker |
| `TimeOnDelegate` | Present and commit TIME_ON edits through a seconds-free time picker |
| `ModeDelegate` | Present and commit MODE edits through the fixed CW/SSB dropdown |
| `QsoListWidget` (updated) | Render the submitted-QSO table and capture the operator's in-place cell edits and row-deletion requests for the controller to validate and apply |
| `QsoEntryController` (updated) | Mediate between widget signals (submit, edit, delete, generate ADIF) and application commands |

## Testing Strategy

Mirrors `src/` under `tests/`, extending qso-entering's existing suites
rather than starting new ones except where noted.

- **Domain** (`tests/domain/logging_session/test_entities.py`, existing
  file, new cases): `LoggingSession.edit_qso(0, call="w1aw", ...)` replaces
  only `qsos[0]` and normalizes it uppercase, exactly like `record_qso`
  does for a fresh QSO, while every other index and `next_entry_defaults`
  stay byte-for-byte unchanged (the direct regression test for
  requirements.md Story 5, at the layer that actually enforces it); editing
  FREQ updates `.band` on the same index without any special-cased "band"
  parameter; editing TIME_ON updates `.time_off` (the derived property) to
  match; an invalid FREQ (`FrequencyFormatError`/`FrequencyOutOfBandError`)
  raised from `edit_qso` leaves `session.qsos` completely unchanged at that
  index — the same "no state change on invalid FREQ" guarantee
  `record_qso` already has, asserted the same way its existing test is.
- **Application** (`tests/application/logging_session/test_commands.py`,
  existing file, new cases): `EditQsoCommand(...).execute(EditQsoRequest(index=0,
  ...))` against a fake repository seeded with one QSO returns an
  `EditQsoResult` whose `.qso` reflects the edit, calls `.save()` once, and
  — importantly — the fake session's `next_entry_defaults` object identity
  is unchanged (proving Story 5 holds at the application layer too, not
  just inside the aggregate); a `FrequencyFormatError` from an invalid FREQ
  edit propagates without `.save()` being called, mirroring
  `SubmitQsoCommand`'s existing failure-path test.
- **Infrastructure**
  (`tests/infrastructure/repositories/test_file_logging_session_repository.py`,
  existing file, one new case): saving a session after `edit_qso` and
  reloading it via `find_unfinished()` round-trips the edited QSO's values
  correctly — confirming no infrastructure change was actually needed, not
  just asserting it in this document.
- **GUI** (`tests/api/test_qso_list_widget.py`, existing file, new cases;
  plus a new `tests/api/test_qso_table_delegates.py`): constructing
  `QsoListWidget` and reading `.editTriggers()` includes `DoubleClicked`;
  appending a QSO via `append_qso` never emits `edited` (the direct
  regression test for the `blockSignals` guard in `_write_row` — the
  easiest part of this design to accidentally break); simulating a
  double-click-edit-commit sequence on a CALL cell with lowercase text
  results in the cell displaying uppercase and `edited` firing with an
  uppercase `EditQsoRequest.call`; the same sequence on a MODE cell only
  ever offers `["CW", "SSB"]` and is not editable, matching the entry
  form's existing MODE assertions; a TIME_ON edit's committed cell text
  always ends `:00` in the underlying stored time (no seconds surfaced);
  `apply_edit(0, a_qso_dto)` rewrites row 0's 7 cells to match `a_qso_dto`
  and updates `self._qsos[0]`; `revert_edit(0)` after mutating row 0's
  displayed text directly restores the original text and leaves
  `self._qsos[0]` untouched (proving revert reads from the pre-edit cache,
  not from whatever's currently displayed). `test_qso_table_delegates.py`
  covers each of the 4 delegate classes directly: `createEditor` returns
  the expected widget type; `setEditorData` given a model index whose text
  is e.g. `"2026-09-07"` sets the `QDateEdit`'s date to the matching
  `QDate`; `setModelData` given an edited `QTimeEdit` showing `14:12`
  writes back `"14:12:00"` (proving the zero-seconds convention is
  enforced at the delegate too, defense-in-depth alongside
  `QsoTimestamp.__post_init__`'s own normalization).
- **GUI** (`tests/api/test_qso_entry_controller.py`, existing file, new
  cases): a stub `EditQsoCommand` returning a successful `EditQsoResult`
  causes `_on_qso_edited` to call `qso_list.apply_edit(row, result.qso)`
  and `form.clear_error()`; a stub raising `FrequencyFormatError` causes it
  to call `qso_list.revert_edit(row)` and `form.show_error(str(exc))`
  instead — the same fake-command-double pattern
  `test_qso_entry_controller.py` already uses for `SubmitQsoCommand`.

**Stories 6-7 additions:**

- **Domain** (`tests/domain/logging_session/test_entities.py`, existing
  file, new cases): `LoggingSession.delete_qso(0)` on a two-QSO session
  removes `qsos[0]` and leaves the former `qsos[1]` as the new `qsos[0]`
  (proving order is preserved, not just count); `next_entry_defaults`
  object identity is unchanged (the Story 7 regression test, mirroring
  Story 5's for `edit_qso`); `delete_qso` on the only remaining QSO leaves
  `session.qsos == ()`; `delete_qso` with an out-of-range index raises
  `IndexError` and leaves `session.qsos` unchanged.
- **Application** (`tests/application/logging_session/test_commands.py`,
  existing file, new cases): `DeleteQsoCommand(...).execute(DeleteQsoRequest(index=0))`
  against a fake repository seeded with two QSOs removes the first, calls
  `.save()` once, and returns `None`; the fake session's
  `next_entry_defaults` object identity is unchanged.
- **GUI** (`tests/api/test_qso_list_widget.py`, existing file, new cases):
  `widget.selectionBehavior() == QTableWidget.SelectionBehavior.SelectRows`
  and `widget.selectionMode() == QTableWidget.SelectionMode.SingleSelection`;
  `widget.contextMenuPolicy() == Qt.ContextMenuPolicy.CustomContextMenu`;
  triggering `_on_context_menu_requested` at a point inside row 0 selects
  row 0 (`widget.selectedRanges()` / `currentRow()` reflects it) and emits
  `delete_requested` with `0` when the (monkeypatched or directly invoked)
  menu's chosen action is "Delete"; triggering it at a point below the last
  row emits nothing and changes no selection; `remove_row(0)` on a two-row
  table drops row 0, leaves the former row 1's values as the new row 0's,
  and shrinks `widget._qsos` to length 1.
- **GUI** (`tests/api/test_qso_entry_controller.py`, existing file, new
  cases): with `QMessageBox.question` monkeypatched to return `Yes`,
  emitting `qso_list.delete_requested(0)` calls a stub `DeleteQsoCommand`
  with `DeleteQsoRequest(index=0)` and then `qso_list.remove_row(0)`; with
  it monkeypatched to return `No`, emitting the same signal calls neither
  the command nor `remove_row` — the same "assert on the fake command's
  `executed_with`" pattern already used for `SubmitQsoCommand`/`EditQsoCommand`,
  plus a `remove_row` call-count/argument assertion on a small test double
  for `QsoListWidget` (or the real widget, pre-seeded with one row via
  `append_qso`).

## Open Questions / Risks

None blocking for Stories 1-5. One documented assumption, called out
inline under API Layer → Entry points above rather than repeated here: an
edit-time `FrequencyFormatError`/`FrequencyOutOfBandError` is shown via the
entry form's existing error label rather than a new, table-adjacent one,
since requirements.md only specifies that an error must be shown, not
where — reusing the existing mechanism is the smallest change that
satisfies the requirement, and nothing in the acceptance criteria depends
on the error's exact location on screen.

None blocking for Stories 6-7 either. The one genuine decision — where the
deletion confirmation dialog lives — has one reasonable shape given this
codebase's existing precedent: `QsoEntryController.generate_adif()` already
shows a native Qt dialog (`QFileDialog`) directly, inline, before deciding
whether to call a command, so `QMessageBox.question` before
`DeleteQsoCommand` in `_on_delete_requested` is the same pattern applied to
a second command, not a new architectural decision. Requirements.md's Story
6 deliberately leaves the confirmation prompt's exact wording/styling
unspecified (see its "Out of scope" list), so `"Delete this QSO?"` with the
default Yes/No buttons is a free implementation choice, not a requirement
this design needs to justify further.
