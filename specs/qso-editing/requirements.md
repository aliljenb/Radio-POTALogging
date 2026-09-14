# Requirements: qso-editing

## Status

- [x] Draft
- [x] In Review
- [x] Approved

_Stories 1-5 (double-click-to-edit a submitted QSO's field) were previously
approved and implemented in full — see `design.md`/`tasks.md`. Story 6 and
Story 7 below (right-click a row to delete the whole QSO) approved
2026-09-14. Ready for a `/spec-design qso-editing` follow-up pass._

## Introduction

Today, once a QSO is submitted from the entry form it is appended to the
read-only QSO table and can never be changed — qso-entering's requirements
explicitly list "editing or deleting a QSO after it has been submitted" as
out of scope. In practice, an operator transcribing from a paper log in the
field sometimes notices a mistake (a mistyped callsign, a wrong RST, a
frequency read off the radio incorrectly, or an entire contact logged in
error) only after the QSO is already in the table, and today the only way
to correct it is to finish the session and hand-edit the generated ADIF
file. This feature lets the operator fix a mistake directly in the
submitted QSO table — by double-clicking a field and typing a new value, or
by right-clicking a whole row and deleting it — without leaving the
application.

## User stories

### Story 1: Edit a submitted QSO's field by double-clicking it

> As an **operator**, I want to **double-click a field on an already-submitted
> QSO in the table and type a new value**, so that **I can fix a mistake I
> notice after logging it, without restarting my session or hand-editing the
> exported file**.

**Acceptance criteria:**

- [ ] WHEN the operator double-clicks a cell in one of the QSO table's 7
      visible columns (CALL, QSO_DATE, TIME_ON, RST_RCVD, RST_SENT, FREQ,
      MODE — qso-entering Story 16) on an already-submitted row, THE SYSTEM
      SHALL make that cell editable in place, pre-filled with its current
      value.
- [ ] WHEN the operator commits an edit (by pressing Enter or moving focus
      away from the cell) with a value THE SYSTEM accepts (Story 2), THE
      SYSTEM SHALL update that QSO's stored field to the new value and
      display the new value in the table.
- [ ] WHEN the operator presses Escape while editing a cell, THE SYSTEM
      SHALL discard the in-progress edit and leave the QSO's stored field
      and the table's displayed value unchanged.
- [ ] WHEN an edit is committed, THE SYSTEM SHALL persist the updated QSO to
      the session file the same way a freshly submitted QSO is persisted
      (qso-entering Story 3), so the correction survives an application
      restart.
- [ ] WHEN the operator triggers "Generate ADIF" (adif-generation Story 1)
      after editing a QSO, THE SYSTEM SHALL write that QSO's edited values
      to the ADIF file, exactly as if they had been entered that way
      originally.
- [ ] THE SYSTEM SHALL allow editing any already-submitted row in the table,
      not only the most recently submitted one.
- [ ] THE SYSTEM SHALL NOT change the row's position in the table, or any
      other row's values, as a result of editing one field on one row.

### Story 2: Edited CALL, MODE, and FREQ keep the same rules as original entry

> As an **operator**, I want **an edited CALL, MODE, or FREQ to be checked
> and normalized the same way it would be at first entry**, so that **a
> correction can't leave my log less consistent than it was before I fixed
> it**.

**Acceptance criteria:**

- [ ] WHEN the operator edits a CALL cell, THE SYSTEM SHALL display and
      store any letters as uppercase and leave non-letter characters
      unchanged, exactly as the entry form's CALL field does (qso-entering
      Story 5), and SHALL NOT apply any format or callsign-lookup
      validation (qso-entering Story 1).
- [ ] WHEN the operator double-clicks a MODE cell, THE SYSTEM SHALL present
      a dropdown offering exactly "CW" and "SSB" — not free-text entry —
      the same restriction as the entry form's MODE dropdown (qso-entering
      Story 9).
- [ ] THE SYSTEM SHALL NOT allow any value other than "CW" or "SSB" to be
      committed to a QSO's MODE through this dropdown.
- [ ] WHEN the operator edits a FREQ cell, THE SYSTEM SHALL require the new
      value to be a decimal-MHz string accepted by the same format and
      band-plan checks used at original submission (qso-entering Story 1;
      adif-generation Story 1).
- [ ] IF an edited FREQ fails the decimal-MHz format check or does not fall
      within any band in the band-plan table, THEN THE SYSTEM SHALL reject
      the edit, revert the cell to its previous value, and display an error
      message to the operator, leaving the QSO's stored FREQ and BAND
      unchanged.
- [ ] WHEN an edited FREQ is accepted, THE SYSTEM SHALL re-derive that QSO's
      BAND from the new FREQ using the same band-plan table used at
      original submission, and store the updated BAND — even though BAND is
      not itself one of the 7 visible columns.

### Story 3: Edited TIME_ON keeps whole-minute precision and stays in sync with TIME_OFF

> As an **operator**, I want **an edited contact time to still be a whole
> minute and to keep the QSO's off-time consistent with it**, so that **a
> corrected time doesn't introduce a precision my paper log never had, or
> leave the contact's on/off times mismatched**.

**Acceptance criteria:**

- [ ] WHEN the operator double-clicks a TIME_ON cell, THE SYSTEM SHALL only
      allow entering hours and minutes, with no seconds component, the same
      as the entry form's TIME_ON field (qso-entering Story 14).
- [ ] WHEN an edited TIME_ON is committed, THE SYSTEM SHALL store it with
      the seconds component fixed at zero, and SHALL set that QSO's
      TIME_OFF equal to the new TIME_ON, the same invariant applied at
      original submission (qso-entering Story 2, Story 14).
- [ ] WHEN the operator triggers "Generate ADIF" after editing TIME_ON, THE
      SYSTEM SHALL write both TIME_ON and TIME_OFF using the edited value in
      ADIF's 6-digit HHMMSS format with seconds always "00" (qso-entering
      Story 14).

### Story 4: QSO_DATE, RST_SENT, and RST_RCVD can be edited with no extra format restriction

> As an **operator**, I want to **correct the date or a signal report on an
> already-submitted QSO by typing a new value**, so that **I can fix these
> the same way I'd have entered them the first time, without extra rules
> getting in the way**.

**Acceptance criteria:**

- [ ] WHEN the operator double-clicks a QSO_DATE cell, THE SYSTEM SHALL let
      the operator enter any valid calendar date, with no further format or
      range validation, matching the entry form's original QSO_DATE
      behavior.
- [ ] WHEN the operator double-clicks an RST_RCVD or RST_SENT cell, THE
      SYSTEM SHALL accept any text the operator types, with no format
      validation — the same "no restriction beyond the MODE-dependent
      default at first entry" treatment RST_SENT/RST_RCVD already receive
      (qso-entering Story 13).

### Story 5: Editing a past QSO never changes the in-progress entry form

> As an **operator**, I want **correcting a QSO I already logged to leave
> the entry form I'm currently filling in untouched**, so that **fixing a
> past mistake can't unexpectedly overwrite a value I've already typed for
> my next contact**.

**Acceptance criteria:**

- [ ] WHEN the operator edits any field of any already-submitted QSO,
      including the most recently submitted one that the currently
      displayed, not-yet-submitted entry form's defaults were carried
      forward from (qso-entering Story 2), THE SYSTEM SHALL NOT change any
      value already displayed on that entry form.
- [ ] THE SYSTEM SHALL apply the edited value only to future carry-forward
      once the operator submits a new QSO from the entry form as it
      currently stands — this story only guarantees the entry form's
      already-displayed values are left alone at the moment of the edit.

### Story 6: Delete a submitted QSO via a right-click context menu

> As an **operator**, I want to **right-click an already-submitted QSO's row
> and delete it**, so that **I can remove a duplicate or mistaken contact
> from my log without hand-editing the exported file**.

**Acceptance criteria:**

- [ ] WHEN the operator right-clicks anywhere within an already-submitted
      row in the QSO table, THE SYSTEM SHALL select that row (and only that
      row) and display a context menu offering a "Delete" action.
- [ ] WHEN the operator chooses "Delete" from the context menu, THE SYSTEM
      SHALL ask the operator to confirm the deletion before doing anything
      else, and SHALL leave the QSO table and stored session completely
      unchanged if the operator cancels.
- [ ] WHEN the operator confirms the deletion, THE SYSTEM SHALL remove that
      QSO from the table and from the underlying stored session.
- [ ] WHEN a QSO is deleted, THE SYSTEM SHALL persist the updated session to
      the session file (qso-entering Story 3), so the deletion survives an
      application restart.
- [ ] WHEN the operator triggers "Generate ADIF" (adif-generation Story 1)
      after deleting a QSO, THE SYSTEM SHALL NOT include the deleted QSO in
      the generated ADIF file.
- [ ] THE SYSTEM SHALL allow deleting any already-submitted row in the
      table, not only the most recently submitted one, including the only
      remaining row (leaving the table empty).
- [ ] WHEN a QSO is deleted, THE SYSTEM SHALL NOT change the relative order
      of the remaining QSOs in the table.
- [ ] THE SYSTEM SHALL operate on exactly one row per "Delete" action — the
      context menu deletes only the single row it was opened on.

### Story 7: Deleting a QSO never changes the in-progress entry form

> As an **operator**, I want **deleting a QSO I already logged to leave the
> entry form I'm currently filling in untouched**, so that **removing a past
> mistake can't unexpectedly change a value I've already typed for my next
> contact**.

**Acceptance criteria:**

- [ ] WHEN the operator deletes any already-submitted QSO, including the
      most recently submitted one that the currently displayed, not-yet
      submitted entry form's defaults were carried forward from
      (qso-entering Story 2), THE SYSTEM SHALL NOT change any value already
      displayed on that entry form.

## Out of scope

- Editing the 7 fields not shown as table columns (TIME_OFF, OPERATOR,
  MY_SIG, MY_SIG_INFO, MY_RIG, TX_PWR) — only CALL, QSO_DATE, TIME_ON,
  RST_RCVD, RST_SENT, and FREQ can be edited through the table; BAND is
  never directly editable, only re-derived from an edited FREQ (Story 2).
- Making MY_SIG_INFO, QSO_DATE, OPERATOR, or MY_RIG editable on the
  not-yet-submitted entry form — those remain plain text labels with no
  input mechanism (qso-entering Story 12); the only way to change them is
  still starting a new session (qso-entering Story 3, Story 6). Note that
  QSO_DATE is a text label on the entry form but a genuinely editable
  column once a QSO reaches the table — these are different UI elements for
  the same field name.
- Inserting a new row anywhere but the end, or reordering rows.
- Bulk/multi-cell editing, or editing more than one QSO at a time.
- Undo/redo of a committed edit — only an in-progress edit (before Enter or
  focus-out) can be discarded, via Escape (Story 1).
- Deleting more than one row at a time (bulk delete) — the context menu's
  "Delete" action always operates on exactly one row (Story 6).
- Undo/restore of a confirmed deletion — once the operator confirms, the
  QSO is permanently removed from the session and any future ADIF export
  (Story 6); there is no way to recover it short of not confirming the
  deletion prompt in the first place.
- Deleting a QSO by any means other than the right-click context menu's
  "Delete" action — e.g. a keyboard shortcut (Delete/Backspace) or a
  toolbar button.
- Prescribing the exact wording, styling, or dialog type of the deletion
  confirmation prompt (Story 6) — only that a confirmation step exists and
  can be cancelled.
- Syncing an edited QSO's value into the currently displayed, not-yet
  submitted entry form's carried-forward defaults, even when the edited QSO
  is the one those defaults were carried forward from (Story 5).
- Any change to the QSO table's fixed 7-column set or column order
  (qso-entering Story 16), its alternating row colors (qso-entering Story
  15), or the session-setup dialog (qso-entering Story 6).
- Any change to how a *new* QSO is submitted from the entry form —
  first-entry defaults, carry-forward, Enter-to-submit, or validation at
  submission time (qso-entering Stories 1, 2, 9, 11, 13) are unaffected by
  this feature.
- A confirmation dialog before committing an edit — committing happens
  immediately on Enter/focus-out (Story 1), with no separate confirm step.

## Open questions

- [ ] None outstanding for Stories 1-5 — scope, edit mechanism (inline, not
      a modal dialog), validation parity with original entry, automatic
      BAND/TIME_OFF re-derivation, and no carry-forward sync to the
      in-progress entry form were all confirmed during the first
      `/spec-requirements qso-editing` pass, and Stories 1-5 are already
      implemented.
- [ ] None outstanding for Stories 6-7 either — single-row-only deletion
      (no bulk/multi-row support) and a required confirmation step before a
      delete takes effect were both confirmed during this
      `/spec-requirements qso-editing` pass. Ready for a
      `/spec-design qso-editing` follow-up pass to decide the deletion
      mechanism (e.g. a new `LoggingSession` operation alongside `edit_qso`,
      a `QMenu`-based context menu on `QsoListWidget`, and where the
      confirmation prompt lives).
