# Tech Stack

> Claude will not introduce packages or tools not listed here without asking first.

## Language

- **Python 3.12+**

## Package management

- **pip** + `requirements.txt`
  _(swap to uv or poetry if preferred — update this doc if you do)_

## Testing

- **pytest** — unit and integration tests
- **pytest-cov** — coverage reporting
- **pytest-qt** — widget-level tests for the PyQt desktop GUI (approved
  exception to the Playwright rule in `.claude/rules/testing.md`, which
  covers browser-based UI; Playwright cannot drive a PyQt window — see
  decision log)

## Code quality

- **ruff** — linting and formatting
- **mypy** — static type checking

## Runtime dependencies

| Package | Purpose |
|---------|---------|
| PyQt6   | Desktop GUI toolkit |

## Decision log

| Date | Decision | Alternatives considered | Rationale |
|------|----------|------------------------|-----------|
| 2026-08-30 | Build the app as a PyQt desktop GUI, not a browser frontend | Web app (`frontend/src` + FastAPI API), terminal/TUI | qso-entering is a single-operator field tool; a desktop GUI avoids running a local web server and fits offline, portable use |
| 2026-08-30 | Pin PyQt to major version 6 (PyQt6) | PyQt5 (legacy, Qt5-based) | Qt6 is the actively maintained line; no constraint requires PyQt5 |
| 2026-08-30 | Approve `pytest-qt` for GUI-level tests, as an exception to `testing.md`'s Playwright rule | No automated GUI tests (manual only) | qso-entering's UI is a PyQt desktop window, which Playwright (browser-only) cannot automate; pytest-qt is the standard PyQt/PySide testing library |
