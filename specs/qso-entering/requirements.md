# Requirements: qso-entering

## Status

- [x] Draft
- [x] In Review
- [x] Approved

## Introduction

After a portable "Parks On The Air" (POTA) activation, an operator needs to
transcribe contacts (QSOs) from a paper log into digital form, quickly and
with minimal repeated typing, and produce a standard ADIF log file that can
be uploaded to POTA/ARRL/LoTW and similar services. This feature is a
desktop application form for entering QSOs one at a time, carrying forward
repetitive field values between entries, and generating an ADIF export
on demand.

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
- [ ] WHEN the form is first displayed, THE SYSTEM SHALL pre-fill QSO_DATE
      with the current date and TIME_ON with the current time (UTC), and
      SHALL leave MY_SIG_INFO and FREQ empty.
- [ ] THE SYSTEM SHALL always associate MY_SIG with the fixed value "POTA"
      for every QSO, whether or not MY_SIG is shown as an editable field.
- [ ] THE SYSTEM SHALL allow every pre-filled field to be edited by the
      operator before submission.
- [ ] IF the operator changes the value of a pre-filled field before
      submitting, THEN THE SYSTEM SHALL treat the edited value (not the
      original constant) as the value to carry forward per Story 2.
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
      required for the log file (see Story 4) for that QSO.
- [ ] WHEN a QSO is submitted, THE SYSTEM SHALL append it to the end of a
      visible QSO list, displayed above the entry form for the next QSO.
- [ ] WHEN the next entry form is displayed, THE SYSTEM SHALL pre-fill
      every field with the value from the just-submitted QSO, EXCEPT CALL
      and TIME_ON.
- [ ] WHEN the next entry form is displayed, THE SYSTEM SHALL leave CALL
      empty and SHALL set input focus to the CALL field.
- [ ] WHEN the next entry form is displayed, THE SYSTEM SHALL set TIME_ON
      to the previous QSO's TIME_ON plus 2 minutes.
- [ ] IF incrementing TIME_ON by 2 minutes crosses midnight, THEN THE
      SYSTEM SHALL roll TIME_ON over and advance QSO_DATE by one day for
      that pre-filled entry.

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
- [ ] IF the operator chooses to start clean, THEN THE SYSTEM SHALL begin
      a new, empty QSO list and present the first-entry defaults of Story
      1, without discarding the previous session's persisted file.

### Story 4: Generate an ADIF log file on demand

> As an **operator**, I want to **generate an ADIF file from all QSOs I've
> entered at any point**, so that **I can upload my log without waiting
> until every contact from the trip is transcribed**.

**Acceptance criteria:**

- [ ] THE SYSTEM SHALL provide a "Generate ADIF" action that is available
      at any time, independent of whether a QSO entry is in progress.
- [ ] WHEN the operator triggers "Generate ADIF", THE SYSTEM SHALL produce
      an ADIF-format file containing one record per submitted QSO.
- [ ] THE SYSTEM SHALL include only these fields per record: OPERATOR,
      CALL, QSO_DATE, TIME_ON, TIME_OFF, BAND, MODE, MY_SIG, MY_SIG_INFO,
      RST_SENT, RST_RCVD, FREQ, MY_RIG, TX_PWR.
- [ ] THE SYSTEM SHALL derive BAND for each record from that QSO's FREQ
      (MHz) using the following table; BAND is never entered directly by
      the operator:

  | FREQ range (MHz)  | BAND |
  |--------------------|------|
  | 1.800 – 2.000      | 160M |
  | 3.500 – 4.000      | 80M  |
  | 7.000 – 7.300      | 40M  |
  | 10.100 – 10.150    | 30M  |
  | 14.000 – 14.350    | 20M  |
  | 18.068 – 18.168    | 17M  |
  | 21.000 – 21.450    | 15M  |
  | 24.890 – 24.990    | 12M  |
  | 28.000 – 29.700    | 10M  |
  | 50.000 – 54.000    | 6M   |

- [ ] IF a QSO's FREQ does not fall within any range in the table above,
      THEN THE SYSTEM SHALL reject the QSO at submission time (see Story
      1/2) rather than produce a record with an undefined BAND.

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
- [ ] WHEN the operator triggers "Generate ADIF" (Story 4), THE SYSTEM
      SHALL write CALL in the ADIF file with any letters as uppercase,
      for every QSO in the file regardless of when it was submitted.
- [ ] THE SYSTEM SHALL NOT otherwise change the behavior described in
      Story 1's "no format or callsign-lookup validation" criterion — this
      story only affects letter case, not what characters are accepted.

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

## Open questions

- [ ] Story 5 was added after `design.md` and `tasks.md` for this feature
      were already approved and implemented (CALL is currently stored and
      exported exactly as typed). Implementing Story 5 needs a follow-up
      pass through `/spec-design qso-entering` (to decide where the
      uppercase normalization lives — e.g. the entry widget, the domain
      `Qso`/`LoggingSession`, and/or the ADIF exporter) and
      `/spec-tasks qso-entering` before `/implement-task` can add it,
      rather than editing already-shipped code ad hoc.

Resolved from earlier drafting, still valid:

- Platform: desktop GUI, built with PyQt (tracked as a decision in
  `.claude/rules/tech.md`).
- Persistence: file-based, in the application's launch directory, with a
  resume/start-clean prompt on startup (Story 3).
- BAND derivation: fixed frequency-range table (Story 4).
- FREQ format / CALL validation: FREQ is a decimal-MHz string; CALL has no
  format/lookup validation, but Story 5 now governs its letter case
  (Story 1).
