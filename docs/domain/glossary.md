# Glossary

Ubiquitous language shared between product and code. Keep entity/value
object names here in sync with `specs/*/design.md`.

| Term | Meaning |
|------|---------|
| QSO | A single logged radio contact between the operator and another station. |
| POTA | Parks On The Air — the activation program this application logs contacts for; the source of the fixed `MY_SIG` value. |
| ADIF | Amateur Data Interchange Format — the external log-file format this application exports to. |
| LoggingSession | The aggregate representing one activation's in-progress (or resumed) ordered sequence of QSOs, from which an ADIF file can be generated at any time. Introduced in `specs/qso-entering/design.md`. |
| Qso (value object) | An immutable, submitted contact record within a `LoggingSession` — call, timestamp, mode, signal reports, frequency, station info. Introduced in `specs/qso-entering/design.md`. |
| EntryDefaults | The set of field values used to pre-fill the next QSO entry form, carried forward from the previously submitted QSO (or seeded from `StationDefaults` for a brand-new session). Introduced in `specs/qso-entering/design.md`. |
| StationDefaults | The fixed application-level constants (operator, mode, MY_SIG, signal reports, rig, power) used to seed the very first QSO entry of a new session. Introduced in `specs/qso-entering/design.md`. |
| Frequency | A QSO's operating frequency in MHz; derives the QSO's `Band` via the fixed ADIF band-plan table. Introduced in `specs/qso-entering/design.md`. |
| Band | The amateur radio band (e.g. `20M`) derived from a `Frequency`. Introduced in `specs/qso-entering/design.md`. |
| QsoTimestamp | The combined QSO date + time-on (UTC) of a QSO; knows how to advance by 2 minutes with correct day rollover. Introduced in `specs/qso-entering/design.md`. |
