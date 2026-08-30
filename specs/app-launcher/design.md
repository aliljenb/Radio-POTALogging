# Design: app-launcher

## Status

- [x] Draft
- [x] In Review
- [x] Approved

## Overview

A macOS `.app` bundle at `macos/POTA QSO Logging.app/` containing only two
files: `Contents/Info.plist` (bundle metadata macOS needs to show it in
Finder/Dock) and `Contents/MacOS/launch` (a small shell script that is the
bundle's actual executable). Double-clicking the bundle runs the script,
which locates this project's `.venv` Python, ensures `~/POTA Logs` exists,
`cd`s into it, and runs the existing `radio_pota_logging.api.composition_root`
entry point — the same one already used from a terminal — capturing its
output to a log file and alerting if it exits with a failure code. No
Python source under `src/` changes; this is packaging/OS-integration, not
new business logic.

## Domain-Driven Design sections

This feature introduces no domain model, application use cases, or
infrastructure adapters under `src/radio_pota_logging/`, so the template's
Domain Model / Application Layer / Infrastructure / API Layer / Frontend
Design sections are not applicable:

- **Domain Model**: N/A. Nothing here has identity, a lifecycle, domain
  meaning, or invariants — it locates a file and runs it. Per
  `.claude/rules/domain-driven-design.md` ("Appropriate Use of DDD
  Patterns"), inventing an entity/value object/aggregate for "the
  launcher" would be DDD terminology for its own sake, not justified by
  any business rule.
- **Application Layer**: N/A. There is no new use case orchestrating
  domain objects — the script's one job (find Python, prepare a
  directory, exec) has no domain objects to orchestrate.
- **Infrastructure**: N/A in the `src/radio_pota_logging/infrastructure/`
  sense (no repository/exporter adapter is added). The launcher does talk
  to the OS (filesystem, process exec, native alerts), but as a
  standalone shell script outside the Python package, not as a port
  implementation.
- **API Layer / Frontend Design**: N/A. The launcher does not add UI; it
  starts the existing `MainWindow` unchanged.

See § macOS Launcher Bundle below for what this feature actually adds.

## macOS Launcher Bundle

### Layout

```
macos/
└── POTA QSO Logging.app/
    └── Contents/
        ├── Info.plist
        └── MacOS/
            └── launch          # executable (chmod +x), the bundle's CFBundleExecutable
```

### `Contents/Info.plist`

Minimal bundle metadata — no custom icon (`CFBundleIconFile` omitted, per
requirements' out-of-scope), and no `LSUIElement`/`LSBackgroundOnly` keys,
so macOS treats it as a normal foreground app with a Dock icon while
running (required by requirements Story 1):

| Key | Value |
|-----|-------|
| `CFBundleName` | `POTA QSO Logging` |
| `CFBundleIdentifier` | `local.radio-pota-logging.launcher` |
| `CFBundlePackageType` | `APPL` |
| `CFBundleExecutable` | `launch` |
| `CFBundleShortVersionString` | `1.0` |

### `Contents/MacOS/launch`

A POSIX shell script, hardcoding this machine's project path as a
default (per requirements: this machine only) but reading it from
`POTA_LAUNCHER_PROJECT_DIR` if set, so tests can override it without
touching the real path:

```sh
#!/bin/sh
PROJECT_DIR="${POTA_LAUNCHER_PROJECT_DIR:-/Volumes/iMac-Extended-01/Projects_EXT/Python/Radio-POTALogging}"
PYTHON="$PROJECT_DIR/.venv/bin/python"
LOGS_DIR="$HOME/POTA Logs"
LOG_FILE="$LOGS_DIR/launcher.log"

if [ ! -x "$PYTHON" ]; then
    osascript -e 'display alert "POTA QSO Logging" message "The project'\''s virtual environment (.venv) was not found at '"$PROJECT_DIR"'. Follow the setup steps in the project README, then try again." as critical'
    exit 1
fi

mkdir -p "$LOGS_DIR"
cd "$LOGS_DIR" || exit 1

"$PYTHON" -m radio_pota_logging.api.composition_root > "$LOG_FILE" 2>&1
exit_code=$?

if [ "$exit_code" -ne 0 ]; then
    osascript -e 'display alert "POTA QSO Logging" message "The application exited unexpectedly (exit code '"$exit_code"'). See '"$LOG_FILE"' for details." as critical'
fi

exit "$exit_code"
```

Covers every requirements.md acceptance criterion directly, plus one
design-time addition (crash diagnosis, added per design review — not in
the original acceptance criteria, but directly addresses the risk noted
below):

- Story 1: packaged as a `.app`; runs the GUI with no separate visible
  Terminal (double-clicking a `.app` never opens Terminal.app); runs this
  machine's fixed `.venv`; shows a native alert (`osascript display
  alert`) and exits non-zero if that `.venv`'s Python is missing/not
  executable.
- Story 2: always runs with `~/POTA Logs` as its working directory
  (`cd` before the app runs), creating it first if missing (`mkdir -p`);
  does not touch how the app behaves when launched directly from a
  terminal (that path never goes through this script).
- Addition: the app's stdout/stderr are redirected to
  `~/POTA Logs/launcher.log` (overwritten each run), and if the app exits
  with a non-zero code — e.g. an uncaught PyQt exception — the operator
  gets a native alert naming the exit code and pointing at that log file,
  instead of the app just silently disappearing with no visible Terminal.

The script no longer `exec`s the Python process (it must run to
completion first to read `$?`), so the shell script and the Python
process both exist as separate processes for the app's lifetime; this
does not affect whether the app shows a Dock icon, since that is driven
by the child PyQt/Cocoa process creating its own `NSApplication` and
windows, independent of its parent's process image.

### Single Responsibility Check

| File | Single responsibility |
|------|-------------------------|
| `Info.plist` | Declare this bundle's identity to macOS (name, executable, package type) so Finder/Dock/LaunchServices recognize it as an app |
| `launch` | Launch the QSO Logging app for this project's fixed `.venv`, surfacing setup or runtime failures via a native alert and a log file instead of failing silently |

## Testing Strategy

No new test tooling — plain `pytest` driving the script via `subprocess`,
with `POTA_LAUNCHER_PROJECT_DIR` and `HOME` overridden to temp directories
so tests never touch the real project path or `~/POTA Logs`.

- `tests/macos/test_launch.py`:
  - **Missing `.venv`**: point `POTA_LAUNCHER_PROJECT_DIR` at an empty
    temp dir (no `.venv`); prepend a stub `osascript` to `PATH` that
    records its arguments to a file; run `launch`; assert exit code is
    non-zero and the stub recorded a call (the alert fired) without
    creating `~/POTA Logs`.
  - **Happy path**: point `POTA_LAUNCHER_PROJECT_DIR` at a temp dir
    containing a stub executable at `.venv/bin/python` that writes its
    working directory and argv to a file and exits `0`, instead of really
    starting PyQt; run `launch` with `HOME` set to another temp dir;
    assert `~/POTA Logs` (under that temp `HOME`) was created, the stub
    ran with that directory as its cwd, its recorded argv is `-m
    radio_pota_logging.api.composition_root`, `launch` itself exits `0`,
    and no alert fired.
  - **`~/POTA Logs` already exists**: same as the happy path but
    pre-create the directory (with a marker file inside); assert the
    marker file still exists afterward (the script never recreates or
    clears the directory).
  - **Crash after launch**: use a stub `.venv/bin/python` that prints an
    error message and exits `1` (simulating an uncaught PyQt exception);
    stub `osascript` as above; run `launch`; assert `launch` exits `1`,
    `~/POTA Logs/launcher.log` contains the stub's printed message, and
    the stub `osascript` was called with a message naming exit code `1`
    and the log file's path.

This exercises every branch in `launch` without ever starting the real
PyQt application or depending on this machine's actual project path.

## Open Questions / Risks

None currently outstanding. Both raised during design review are resolved:

- **`structure.md` coverage**: `.claude/rules/structure.md` has been
  updated directly (this doesn't require touching `src/` or
  `frontend/src/`, so it isn't blocked by the design-phase restriction)
  with entries for `macos/` and its `tests/macos/` mirror, plus a
  Conventions note that `macos/` sits outside the `src/<python_module>/`
  DDD layering.
- **Crash diagnosis**: added to `launch`'s design above — stdout/stderr
  are redirected to `~/POTA Logs/launcher.log`, and a non-zero exit now
  triggers a native alert naming the exit code and the log file, covered
  by a new "Crash after launch" test case in § Testing Strategy.
