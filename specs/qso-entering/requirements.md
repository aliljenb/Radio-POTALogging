# Requirements: qso-entering

## Status

- [x] Draft
- [x] In Review
- [x] Approved

## Introduction

After a portable "Parks On The Air" (POTA) activation, an operator needs to
transcribe contacts (QSOs) from a paper log into digital form, quickly and
with minimal repeated typing, ahead of producing a standard ADIF log file
that can be uploaded to POTA/ARRL/LoTW and similar services (see the
adif-generation feature). This feature is a desktop application form for
entering QSOs one at a time, carrying forward repetitive field values
between entries, and triggering that ADIF export on demand.

## User stories

### Story 1: Enter the first QSO with sensible defaults

> As an **operator**, I want to **start a new QSO entry pre-filled with my
> usual station and mode settings**, so that **I don't have to retype the
> same information for every contact**.

**Acceptance criteria:**

- [ ] WHEN the operator opens the QSO entry form for the first time in a
      new session, THE SYSTEM SHALL display the fields CALL, QSO_DATE,
      TIME_ON, MODE, MY_SIG_INFO, RST_SENT, RST_RCVD, FREQ, OPERATOR,
      MY_RIG, and TX_PWR.
- [ ] WHEN the form is first displayed, THE SYSTEM SHALL pre-fill OPERATOR
      with "SM6Y", MODE with "CW", RST_SENT with "599", RST_RCVD with
      "599", MY_RIG with "Elecraft KX2", and TX_PWR with "5", from
      application constants.
- [ ] WHEN the form is first displayed for a new session, THE SYSTEM SHALL
      pre-fill QSO_DATE, TIME_ON, MY_SIG_INFO, and FREQ from the values
      the operator entered in the session-setup dialog (Story 6).
- [ ] THE SYSTEM SHALL always associate MY_SIG with the fixed value "POTA"
      for every QSO, whether or not MY_SIG is shown as an editable field.
- [ ] THE SYSTEM SHALL allow every pre-filled field to be edited by the
      operator before submission.
- [ ] IF the operator changes the value of a pre-filled field before
      submitting, THEN THE SYSTEM SHALL treat the edited value (not the
      original constant) as the value to carry forward per Story 2 — except
      RST_SENT and RST_RCVD, which always reset to "599" on the next entry
      regardless of any edit (Story 2).
- [ ] THE SYSTEM SHALL require FREQ to be entered in MHz as a decimal
      string (e.g. "14.062" or "14.0625").
- [ ] THE SYSTEM SHALL NOT apply any format or callsign-lookup validation
      to the CALL field; any non-empty text is accepted.

### Story 2: Submit a QSO and move straight to the next one

> As an **operator**, I want to **submit a QSO and have the next entry form
> pre-filled from the one I just submitted**, so that **I can log a rapid
> sequence of contacts without re-entering unchanged fields**.

**Acceptance criteria:**

- [ ] WHEN the operator submits a QSO, THE SYSTEM SHALL set TIME_OFF equal
      to TIME_ON for that QSO.
- [ ] WHEN the operator submits a QSO, THE SYSTEM SHALL store all fields
      required for the log file (see the adif-generation feature's Story 1)
      for that QSO.
- [ ] WHEN a QSO is submitted, THE SYSTEM SHALL append it to the end of a
      visible QSO list, displayed above the entry form for the next QSO.
- [ ] WHEN the next entry form is displayed, THE SYSTEM SHALL pre-fill
      every field with the value from the just-submitted QSO, EXCEPT CALL,
      TIME_ON, RST_SENT, and RST_RCVD.
- [ ] WHEN the next entry form is displayed, THE SYSTEM SHALL leave CALL
      empty and SHALL set input focus to the CALL field.
- [ ] WHEN the next entry form is displayed, THE SYSTEM SHALL set TIME_ON
      to the previous QSO's TIME_ON plus 2 minutes.
- [ ] IF incrementing TIME_ON by 2 minutes crosses midnight, THEN THE
      SYSTEM SHALL roll TIME_ON over and advance QSO_DATE by one day for
      that pre-filled entry.
- [ ] WHEN the next entry form is displayed, THE SYSTEM SHALL reset both
      RST_SENT and RST_RCVD to "599", regardless of what was submitted (or
      edited to) on the just-submitted QSO — unlike every other carried-
      forward field, an edit to RST_SENT/RST_RCVD does not propagate to
      the next entry.

### Story 3: Resume an interrupted logging session

> As an **operator**, I want to **close and reopen the application without
> losing QSOs I've already entered**, so that **a low battery, a break, or
> a crash in the field doesn't cost me my log**.

**Acceptance criteria:**

- [ ] WHEN a QSO is submitted, THE SYSTEM SHALL persist it to a file in
      the directory the application was launched from, so it survives an
      application restart.
- [ ] WHEN the application starts and a persisted file from a previous,
      unfinished session is found, THE SYSTEM SHALL ask the operator to
      choose between resuming that session or starting a new, clean one,
      before showing the entry form.
- [ ] IF the operator chooses to resume, THEN THE SYSTEM SHALL restore the
      QSO list and pre-fill the next entry form as if continuing from the
      last submitted QSO (per Story 2), rather than resetting to the
      first-entry defaults of Story 1.
- [ ] IF the operator chooses to start clean, THEN THE SYSTEM SHALL show
      the session-setup dialog (Story 6) before beginning a new, empty QSO
      list with the first-entry defaults of Story 1, without discarding
      the previous session's persisted file.

### Story 5: CALL is always uppercase

> As an **operator**, I want **the CALL field to always show and store
> capital letters**, so that **my log matches standard callsign
> formatting regardless of my keyboard's Caps Lock or layout state, and
> doesn't need manual correction before uploading**.

**Acceptance criteria:**

- [ ] WHEN the operator types into the CALL field, THE SYSTEM SHALL
      display any letters as uppercase, regardless of the physical
      keyboard's case/layout state (e.g. Caps Lock off, a non-US layout).
- [ ] THE SYSTEM SHALL leave non-letter characters in CALL (digits, "/",
      etc.) unchanged.
- [ ] WHEN a QSO is submitted, THE SYSTEM SHALL store CALL with any
      letters as uppercase.
- [ ] WHEN the operator triggers "Generate ADIF" (adif-generation Story 1), THE SYSTEM
      SHALL write CALL in the ADIF file with any letters as uppercase,
      for every QSO in the file regardless of when it was submitted.
- [ ] THE SYSTEM SHALL NOT otherwise change the behavior described in
      Story 1's "no format or callsign-lookup validation" criterion — this
      story only affects letter case, not what characters are accepted.

### Story 6: Confirm park, date, start time, and frequency before a clean session begins

> As an **operator**, I want to **enter the POTA park reference, date,
> time, and frequency of my first QSO before I start logging**, so that
> **every QSO in this session is tagged with the right park, timestamps,
> and band from the very first entry, without relying solely on the
> computer's clock or retyping the frequency**.

**Acceptance criteria:**

- [ ] WHEN a clean session is about to begin — whether this is the
      application's first-ever launch (no previous session file found) or
      the operator chose to start clean after being asked to resume
      (Story 3) — THE SYSTEM SHALL show a modal dialog, before the QSO
      entry form, with four fields: "POTA park reference number", "Date",
      "Time of first QSO", and "Frequency".
- [ ] THE SYSTEM SHALL pre-fill "Date" with the current date and "Time of
      first QSO" with the current time (UTC), both editable; THE SYSTEM
      SHALL leave "POTA park reference number" and "Frequency" empty.
- [ ] THE SYSTEM SHALL provide "OK" and "Quit" actions on the dialog.
- [ ] THE SYSTEM SHALL NOT allow "OK" to proceed while "POTA park
      reference number" or "Frequency" is empty.
- [ ] WHEN the operator clicks "OK" with both a non-empty park reference
      and a non-empty Frequency, THE SYSTEM SHALL close the dialog and use
      "POTA park reference number" as MY_SIG_INFO, "Date" as QSO_DATE,
      "Time of first QSO" as TIME_ON, and "Frequency" as FREQ for the new
      session's first entry form (Story 1).
- [ ] WHEN the operator clicks "Quit", THE SYSTEM SHALL exit the
      application without creating a new session or showing the entry
      form.
- [ ] THE SYSTEM SHALL NOT apply the decimal-MHz format check or band
      lookup (Story 1/4) to "Frequency" within the dialog itself; "OK"
      only requires it to be non-empty. Those checks continue to happen
      only when the operator submits their first QSO, exactly as they
      already do for FREQ today.

### Story 7: MY_SIG_INFO is always uppercase

> As an **operator**, I want **MY_SIG_INFO (the POTA park reference) to
> always show and store capital letters, wherever I enter or edit it**, so
> that **my log matches standard POTA park-reference formatting regardless
> of my keyboard's Caps Lock or layout state, and doesn't need manual
> correction before uploading**.

**Acceptance criteria:**

- [ ] WHEN the operator types into the session-setup dialog's "POTA park
      reference number" field (Story 6), THE SYSTEM SHALL display any
      letters as uppercase, regardless of the physical keyboard's
      case/layout state (e.g. Caps Lock off, a non-US layout) — the same
      behavior as CALL (Story 5).
- [ ] WHEN the operator types into the MY_SIG_INFO field on the main QSO
      entry form, THE SYSTEM SHALL display any letters as uppercase in the
      same way.
- [ ] THE SYSTEM SHALL leave non-letter characters in MY_SIG_INFO (digits,
      "-", etc.) unchanged.
- [ ] WHEN a QSO is submitted, THE SYSTEM SHALL store MY_SIG_INFO with any
      letters as uppercase.
- [ ] WHEN the operator triggers "Generate ADIF" (adif-generation Story 1), THE SYSTEM
      SHALL write MY_SIG_INFO in the ADIF file with any letters as
      uppercase, for every QSO in the file regardless of when it was
      submitted.
- [ ] THE SYSTEM SHALL NOT otherwise change what characters are accepted
      in either field — this story only affects letter case.

### Story 8: OPERATOR is always uppercase

> As an **operator**, I want **the OPERATOR field to always show and store
> capital letters**, so that **my log matches standard callsign formatting
> regardless of my keyboard's Caps Lock or layout state, and doesn't need
> manual correction before uploading**.

**Acceptance criteria:**

- [ ] WHEN the operator types into the OPERATOR field, THE SYSTEM SHALL
      display any letters as uppercase, regardless of the physical
      keyboard's case/layout state (e.g. Caps Lock off, a non-US layout)
      — the same behavior as CALL (Story 5).
- [ ] THE SYSTEM SHALL leave non-letter characters in OPERATOR unchanged.
- [ ] WHEN a QSO is submitted, THE SYSTEM SHALL store OPERATOR with any
      letters as uppercase.
- [ ] WHEN the operator triggers "Generate ADIF" (adif-generation Story 1), THE SYSTEM
      SHALL write OPERATOR in the ADIF file with any letters as
      uppercase, for every QSO in the file regardless of when it was
      submitted.
- [ ] THE SYSTEM SHALL NOT otherwise change what characters are accepted
      in the OPERATOR field — this story only affects letter case.

### Story 9: MODE is a fixed CW/SSB dropdown

> As an **operator**, I want to **pick MODE from a short list instead of
> typing it**, so that **I can't accidentally log an invalid or
> misspelled mode**.

**Acceptance criteria:**

- [ ] THE SYSTEM SHALL render MODE as a dropdown list (not a free-text
      field) offering exactly two options: "CW" and "SSB".
- [ ] WHEN the QSO entry form is first displayed for a new session, THE
      SYSTEM SHALL default MODE to "CW".
- [ ] THE SYSTEM SHALL NOT allow any value other than "CW" or "SSB" to be
      entered into MODE.
- [ ] IF the operator changes MODE before submitting a QSO, THEN THE
      SYSTEM SHALL carry the new selection forward to the next entry
      form's MODE default, the same way other pre-filled fields are
      already carried forward (Story 2).

### Story 10: Main window opens at half width, three-quarters height

> As an **operator**, I want **the main window to open at a sensible,
> predictable size relative to my screen**, so that **I don't have to
> manually resize it every time I launch the application in the field**.

**Acceptance criteria:**

- [ ] WHEN the main window (the QSO entry form and log list) is created,
      THE SYSTEM SHALL set its initial size to half the primary display's
      width and three-quarters (3/4) of the primary display's height.
- [ ] THE SYSTEM SHALL determine "the primary display" using the screen
      the application is shown on at startup.
- [ ] THE SYSTEM SHALL still allow the operator to resize the window
      manually after it opens; this story only governs the initial size.
- [ ] THE SYSTEM SHALL NOT apply this sizing rule to the session-setup
      dialog (Story 6), which keeps its existing size behavior.

### Story 11: Enter submits the QSO from any field

> As an **operator**, I want to **press Enter to submit a QSO instead of
> reaching for the mouse**, so that **I can log contacts faster while
> juggling a paper log and a radio**.

**Acceptance criteria:**

- [ ] WHEN the operator presses Enter/Return while any field on the QSO
      entry form has focus, AND the CALL field is non-empty at that
      moment, THE SYSTEM SHALL submit the QSO exactly as if the operator
      had clicked "Submit".
- [ ] IF the operator presses Enter/Return while the CALL field is empty,
      THEN THE SYSTEM SHALL take no action — no submission occurs, and
      focus/other field values are left unchanged.
- [ ] THE SYSTEM SHALL NOT change any other Submit behavior (validation,
      error display, field carry-forward per Story 2) — Enter is only an
      additional trigger for the same submit action the button already
      performs.

### Story 12: Entry fields follow a fixed display and Tab order

> As an **operator**, I want **the entry form's fields laid out and
> Tab-ordered to match how I naturally fill them in from a paper log**, so
> that **I can move through the form quickly without hunting for the next
> field or reaching for the mouse**.

**Acceptance criteria:**

- [ ] THE SYSTEM SHALL display the 11 entry fields top-to-bottom in this
      order: CALL, RST_RCVD, RST_SENT, TIME_ON, FREQ, MY_SIG_INFO,
      QSO_DATE, MODE, OPERATOR, MY_RIG, TX_PWR.
- [ ] THE SYSTEM SHALL set the keyboard Tab order to visit the 11 fields in
      that same order.
- [ ] THE SYSTEM SHALL NOT otherwise change any field's behavior (default
      value, carry-forward, uppercase normalization, validation) — this
      story only reorders where fields appear and how Tab moves between
      them.

## Out of scope

- Editing or deleting a QSO after it has been submitted and added to the
  list.
- Callsign validation/lookup against an external callbook or database.
- Importing paper logs via OCR or scanning.
- Multi-operator or multi-user support; the application assumes a single
  operator per session.
- Uploading the generated ADIF file directly to POTA, ARRL LoTW, or any
  other service — the feature only produces the file.
- Exporting formats other than ADIF.
- Any timezone conversion: TIME_ON/TIME_OFF are entered and stored as
  already being in UTC.
- Validating the format of "POTA park reference number" (e.g. against
  real POTA park ID patterns like "K-1234") — only non-empty is required
  (Story 6).
- Remembering or suggesting a previously used park reference across
  sessions — the session-setup dialog's park reference field starts empty
  every time (Story 6).
- Validating the setup dialog's "Frequency" field as a decimal MHz value
  or checking it against the band-plan table — only non-empty is required
  there; the existing decimal-format/band-lookup checks (Story 1/4) still
  apply only at QSO submission time (Story 6).
- Any MODE value other than "CW" or "SSB" (e.g. FM, RTTY, digital modes)
  — MODE only ever holds one of those two fixed values (Story 9).

## Open questions

- [ ] The Story 2 RST_SENT/RST_RCVD change needs a follow-up pass through
      `/spec-design qso-entering` to decide exactly where the "always 599,
      never carried forward" rule is enforced — likely
      `LoggingSession.record_qso`'s `next_entry_defaults` construction
      (hardcoding `rst_sent`/`rst_rcvd` to `"599"` there instead of
      threading the submitted values through) — then `/spec-tasks
      qso-entering` before `/implement-task` can add it.
- [ ] The Story 10 height-fraction change (half → three-quarters) needs a
      follow-up pass through `/spec-design qso-entering` to update the
      already-implemented `MainWindow.__init__` resize call's height
      divisor, then `/spec-tasks qso-entering` before `/implement-task`
      can add it.
- [ ] Story 12 needs a follow-up pass through `/spec-design qso-entering`
      to decide the Qt mechanism for the field order: reordering
      `QsoEntryFormWidget`'s `QFormLayout.addRow(...)` calls to match the
      new display order (which also determines default Tab order for a
      `QFormLayout`, since Qt tabs through child widgets in the order
      they're added, unless overridden), or whether an explicit
      `QWidget.setTabOrder(...)` chain is also needed to be safe — then
      `/spec-tasks qso-entering` before `/implement-task` can add it.

Resolved from earlier drafting, still valid:

- Story 10 (main window half-screen sizing) and Story 11 (Enter submits
  from any field) needed their own follow-up design/tasks pass; that's
  done — `MainWindow.__init__` resizes via
  `QApplication.primaryScreen().availableGeometry()`;
  `QsoEntryFormWidget` installs an `eventFilter` on all 11 fields and
  guards Enter-to-submit on a non-empty CALL, without changing the Submit
  button's own behavior (see `specs/qso-entering/design.md` and
  `tasks.md`). The Story 10 height fraction is being revisited above.
- Story 8 (OPERATOR uppercase) and Story 9 (MODE CW/SSB dropdown) needed
  their own follow-up design/tasks pass; that's done — OPERATOR
  normalization lives in `Qso.__post_init__`/`EntryDefaults.__post_init__`
  plus the shared `uppercase_field.uppercase_as_typed()` helper; MODE is a
  non-editable `QComboBox` populated from the domain-level `MODE_OPTIONS`
  constant, re-exported through `application/logging_session/dto.py` so
  `api/` never imports `domain/` directly (see
  `specs/qso-entering/design.md` and `tasks.md`).
- Story 7 (MY_SIG_INFO uppercase) needed the same kind of follow-up
  design/tasks pass; that's done — normalization lives in
  `Qso.__post_init__`/`EntryDefaults.__post_init__` plus a shared
  `uppercase_field.uppercase_as_typed()` helper reused across CALL,
  MY_SIG_INFO, and the setup dialog's park reference field (see
  `specs/qso-entering/design.md` and `tasks.md`).
- The Story 6 Frequency extension (adding "Frequency" to the setup
  dialog) needed its own follow-up design/tasks pass; that's done — see
  `specs/qso-entering/design.md` and `tasks.md`.
- Story 6 (the session-setup dialog itself — park reference, date, time)
  needed the same kind of follow-up design/tasks pass; that's done — see
  `specs/qso-entering/design.md` and `tasks.md`.
- Story 5 (CALL uppercase) needed the same kind of follow-up
  design/tasks pass; that's done — normalization lives in
  `Qso.__post_init__` plus a live-uppercase handler on the CALL widget
  (see `specs/qso-entering/design.md` and `tasks.md`).
- Platform: desktop GUI, built with PyQt (tracked as a decision in
  `.claude/rules/tech.md`).
- Persistence: file-based, in the application's launch directory, with a
  resume/start-clean prompt on startup (Story 3).
- BAND derivation: fixed frequency-range table (adif-generation Story 1).
- FREQ format / CALL validation: FREQ is a decimal-MHz string; CALL has no
  format/lookup validation, but Story 5 now governs its letter case
  (Story 1).
