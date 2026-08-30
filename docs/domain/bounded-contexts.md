# Bounded Contexts

## QSO Logging

Owns the `LoggingSession` aggregate: capturing an operator's radio
contacts during a POTA activation, deriving each contact's band from its
frequency, and exporting the session to an ADIF log file. Introduced by
`specs/qso-entering/design.md`.

Module: `src/radio_pota_logging/`.

This is currently the only bounded context in the project — there is no
context map yet because nothing else exists to map it against. Add a
context map here if/when a second bounded context is introduced.
