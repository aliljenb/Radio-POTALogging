# Requirements: adif-generation

## Status

- [ ] Draft
- [ ] In Review
- [ ] Approved

## Introduction

<!-- One paragraph: what is this feature and why does it exist? -->

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
      qso-entering feature's Story 1/2) rather than produce a record with
      an undefined BAND.
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

### Story 2: [Short title]

> As a **[user type]**, I want to **[goal]**, so that **[benefit]**.

**Acceptance criteria:**

- [ ]
- [ ]

## Out of scope

<!-- Explicitly list what this feature will NOT do -->

## Open questions

<!-- Questions that must be answered before design begins -->

- [ ]
