# Radio-POTALogging

A desktop app for quickly transcribing radio contacts (QSOs) from a paper
log after a Parks On The Air (POTA) activation, and exporting them as an
[ADIF](https://adif.org/adif) log file.

## Status

The `qso-entering` feature is implemented — see
[`specs/qso-entering/`](specs/qso-entering/) for its requirements, design,
and task breakdown.

## Requirements

- Python 3.12+ (see `.python-version`)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

This installs the app's runtime dependency (PyQt6) and the dev tools
(pytest, pytest-cov, pytest-qt, ruff, mypy).

## Running the app

```bash
python -m radio_pota_logging.api.composition_root
```

Run this from whatever directory you want the session's log file to live
in — the app persists the in-progress session as `.qso_session.json` in
its launch directory, and asks whether to resume or start clean if it
finds one left over from a previous run.

## Development

```bash
pytest                        # run tests
ruff check . && ruff format . # lint + format
mypy                           # type-check
```

GUI tests use [pytest-qt](https://pytest-qt.readthedocs.io/) and run
headless; set `QT_QPA_PLATFORM=offscreen` if running them outside a
graphical session (e.g. CI, over SSH):

```bash
QT_QPA_PLATFORM=offscreen pytest
```

## Layout

```
src/radio_pota_logging/   # package code (domain / application / infrastructure / api)
tests/                     # pytest suite (mirrors src/)
specs/<feature>/           # requirements.md, design.md, tasks.md
docs/domain/               # ubiquitous language glossary and bounded contexts
.claude/                   # spec-driven development workflow and steering rules
```

This project follows the spec-driven development workflow described in
[`.claude/CLAUDE.md`](.claude/CLAUDE.md): each feature moves through
requirements → design → tasks before implementation.
