# Radio-POTALogging

A desktop app for quickly transcribing radio contacts (QSOs) from a paper
log after a Parks On The Air (POTA) activation, and exporting them as an
[ADIF](https://adif.org/adif) log file.

## Status

The `qso-entering` and `app-launcher` features are implemented — see
[`specs/qso-entering/`](specs/qso-entering/) and
[`specs/app-launcher/`](specs/app-launcher/) for their requirements,
design, and task breakdowns.

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

### macOS Dock launcher

`macos/POTA QSO Logging.app` is a double-clickable launcher for this
machine: drag it into the Dock or `/Applications` and open it like any
other Mac app — no terminal needed. It always runs the app with
`~/POTA Logs` as its working directory (creating that folder if needed),
so the session file and any generated ADIF exports land there
consistently regardless of how the app was started. If the project's
`.venv` is missing, or the app exits unexpectedly, it shows a native
alert; unexpected-exit output is captured to `~/POTA Logs/launcher.log`.

This launcher is a thin wrapper hardcoded to this project's path on this
machine — it isn't relocatable to another Mac or user account. See
[`specs/app-launcher/design.md`](specs/app-launcher/design.md) for details.

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
macos/                     # macOS .app launcher bundle (this machine only)
tests/                     # pytest suite (mirrors src/ and macos/)
specs/<feature>/           # requirements.md, design.md, tasks.md
docs/domain/               # ubiquitous language glossary and bounded contexts
.claude/                   # spec-driven development workflow and steering rules
```

This project follows the spec-driven development workflow described in
[`.claude/CLAUDE.md`](.claude/CLAUDE.md): each feature moves through
requirements → design → tasks before implementation.
