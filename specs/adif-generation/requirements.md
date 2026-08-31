# Requirements: adif-generation

## Status

- [x] Draft
- [x] In Review
- [x] Approved

## Introduction

After a POTA activation, an operator needs to turn the QSOs they've
transcribed (see the qso-entering feature) into a standard ADIF file that
can be uploaded to POTA/ARRL/LoTW and similar services. This feature adds
a "Generate ADIF" action to the main window that exports every QSO in the
current session to an ADIF 3.x file the operator chooses a location and
filename for. Most of this feature already exists in the codebase
(`AdifFileExporter`, `GenerateAdifCommand`, the "Generate ADIF" button);
this requirements pass documents that implementation and calls out the one
piece — a suggested filename — that is written here but not yet built
(see the last acceptance criterion below and § Open questions).

## User stories

### Story 1: Generate an ADIF log file on demand

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
      THEN THE SYSTEM SHALL reject the QSO at submission time (see the
      qso-entering feature's Story 1, FREQ entry) rather than produce a
      record with an undefined BAND.
- [ ] WHEN the operator triggers "Generate ADIF", THE SYSTEM SHALL suggest
      a filename of the form "<QSO_DATE>-<MY_SIG_INFO>.adi", where
      QSO_DATE is rendered as an 8-digit YYYYMMDD string (e.g. "20260831"),
      using the date and POTA park reference the operator entered in the
      session-setup dialog (qso-entering Story 6) — fixed for the whole
      session regardless of any later per-QSO edit or midnight date
      rollover (qso-entering Story 2).
- [ ] THE SYSTEM SHALL allow the operator to change the suggested filename
      before saving; the suggestion is a pre-filled default, not an
      enforced value.

## Out of scope

- Importing or parsing ADIF files.
- Exporting any format other than ADIF (e.g. Cabrillo).
- Uploading or submitting the generated file to POTA/ARRL/LoTW or any
  other service directly — the operator does that themselves afterward
  with the saved `.adi` file.
- Exporting QSOs from a session other than the current one; an archived
  (previously completed) session's QSOs are not reachable from "Generate
  ADIF" — the operator would need to resume that session first.
- Re-validating FREQ/BAND at export time — a QSO with an unrepresentable
  BAND can never exist in a session, because qso-entering rejects it at
  submission (Story 1 above), so "Generate ADIF" never needs to handle
  that case itself.

## Open questions

None outstanding for requirements — the one still-open item is a design
question, not a requirements question, and is deferred to design.md:

- The filename-suggestion criterion above needs the session's *original*
  QSO_DATE and POTA park reference (MY_SIG_INFO) — fixed at session
  start, unaffected by later per-QSO edits or midnight rollover. Today
  `LoggingSession` only tracks `next_entry_defaults`, which mutates after
  every submitted QSO, and `.qso_session.json` (the file-based
  repository) has no field for the original start values either. design.md
  needs to decide how to model and persist "the session's fixed start
  values" so the API layer can read them when building the save dialog's
  default filename.
