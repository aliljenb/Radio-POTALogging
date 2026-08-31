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
which derives the project root from the script's own on-disk location
(never a hardcoded absolute path), locates that project's `.venv` Python,
ensures `~/POTA Logs` exists, `cd`s into it, and runs the existing
`radio_pota_logging.api.composition_root` entry point — the same one
already used from a terminal — capturing its output to a log file and
alerting if it exits with a failure code. Because the project root is
derived from the bundle's own location rather than baked in at build time,
the same bundle works unmodified regardless of where the repository has
been cloned, on any Mac that has it cloned and its `.venv` set up — as
long as the bundle stays at its checked-in path,
`macos/POTA QSO Logging.app`, inside that clone (requirements Story 1). No
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
| `LSRequiresNativeExecution` | `true` |

`LSRequiresNativeExecution` forces macOS to always run this bundle
natively (arm64 on Apple Silicon) and disables Finder's "Open using
Rosetta" option for it. Without this key, `open`/a Finder double-click
was observed (during implementation testing) to default this bundle to
Rosetta (x86_64) on this machine, which then failed at import time
because the project's installed PyQt6 ships an arm64-only
`QtWidgets.framework` — see implementation-notes.md for the full
diagnosis.

### `Contents/MacOS/launch`

A POSIX shell script. Per the (now-approved) requirement that the
launcher not hardcode any machine-specific absolute path, it derives
`PROJECT_DIR` from its own on-disk location instead: macOS invokes a
bundle's executable with `$0` set to that executable's real path (Finder
double-click and `open` both do this), so resolving `$0`'s directory and
walking up four levels — `Contents/MacOS` → `Contents` →
`POTA QSO Logging.app` → `macos` → the project root — always finds the
project this specific bundle copy lives in, wherever that clone is on
disk:

```sh
#!/bin/sh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
PYTHON="$PROJECT_DIR/.venv/bin/python"
LOGS_DIR="$HOME/POTA Logs"
LOG_FILE="$LOGS_DIR/launcher.log"

if [ ! -x "$PYTHON" ]; then
    osascript -e 'display alert "POTA QSO Logging" message "The project'\''s virtual environment (.venv) was not found at '"$PROJECT_DIR"'. Follow the setup steps in the project README, then try again." as critical'
    exit 1
fi

mkdir -p "$LOGS_DIR"
cd "$LOGS_DIR" || exit 1

if [ "$(sysctl -n hw.optional.arm64 2>/dev/null)" = "1" ]; then
    NATIVE_ARCH="arm64"
else
    NATIVE_ARCH="x86_64"
fi

arch -"$NATIVE_ARCH" "$PYTHON" -m radio_pota_logging.api.composition_root > "$LOG_FILE" 2>&1
exit_code=$?

if [ "$exit_code" -ne 0 ]; then
    osascript -e 'display alert "POTA QSO Logging" message "The application exited unexpectedly (exit code '"$exit_code"'). See '"$LOG_FILE"' for details." as critical'
fi

exit "$exit_code"
```

The `sysctl -n hw.optional.arm64`/`arch -"$NATIVE_ARCH"` pair (added
post-approval — see implementation-notes.md) forces the Python process to
always run at this Mac's true native architecture, regardless of whether
macOS itself launched the `launch` script under Rosetta translation.
`sysctl hw.optional.arm64` reports the host hardware's real capability
(`1` on Apple Silicon) even from inside a translated process, unlike
`uname -m`, which reports the *process's* translated architecture instead
of the hardware's; `arch -<arch> <command>` then spawns `$PYTHON` at that
architecture regardless of what architecture the calling shell itself is
running under. This keeps the launcher working on both Apple Silicon and
Intel Macs without hardcoding a single architecture.

Covers every requirements.md acceptance criterion directly, plus one
design-time addition (crash diagnosis, added per design review — not in
the original acceptance criteria, but directly addresses the risk noted
below):

- Story 1: packaged as a `.app` checked into the repo at
  `macos/POTA QSO Logging.app`; runs the GUI with no separate visible
  Terminal (double-clicking a `.app` never opens Terminal.app); derives
  its project root from its own bundle location (`SCRIPT_DIR` walked up
  four levels) rather than a hardcoded path, so the same bundle works on
  any Mac that has this project cloned and its `.venv` set up, wherever
  that clone lives on disk — as long as the bundle stays at its
  checked-in path inside that clone; shows a native alert (`osascript
  display alert`) and exits non-zero if that `.venv`'s Python is
  missing/not executable.
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
| `launch` | Launch the QSO Logging app for the project `.venv` found relative to this bundle's own location, surfacing setup or runtime failures via a native alert and a log file instead of failing silently |

## Testing Strategy

No new test tooling — plain `pytest` driving the script via `subprocess`.
Tests never touch the real project path or `~/POTA Logs`: each test
builds a throwaway "fake clone" directory tree in a temp dir that
reproduces the real bundle layout —
`<fake-clone>/macos/POTA QSO Logging.app/Contents/MacOS/launch` (a copy
of the real script) plus a stub `<fake-clone>/.venv/bin/python` — so
`launch`'s own `SCRIPT_DIR`/`PROJECT_DIR` resolution runs unmodified and
is itself under test, with `HOME` overridden to a separate temp dir.

- `tests/macos/test_launch.py`:
  - **Different fake-clone locations resolve correctly**: run the same
    happy-path scenario (below) from two fake clones in unrelated temp
    directories; assert both resolve `PROJECT_DIR` to their own clone (via
    the stub's recorded cwd/argv), proving the script never depends on a
    fixed path — directly exercising the new "any Mac, any location"
    requirement.
  - **Missing `.venv`**: fake clone with no `.venv` at all; prepend a stub
    `osascript` to `PATH` that records its arguments to a file; run
    `launch`; assert exit code is non-zero and the stub recorded a call
    (the alert fired) without creating `~/POTA Logs`.
  - **Happy path**: fake clone containing a stub executable at
    `.venv/bin/python` that writes its working directory and argv to a
    file and exits `0`, instead of really starting PyQt; run `launch`
    with `HOME` set to another temp dir; assert `~/POTA Logs` (under that
    temp `HOME`) was created, the stub ran with that directory as its
    cwd, its recorded argv is `-m radio_pota_logging.api.composition_root`,
    `launch` itself exits `0`, and no alert fired.
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

This exercises every branch in `launch`, including its own path
resolution, without ever starting the real PyQt application or depending
on any fixed, machine-specific project path.

## Open Questions / Risks

None currently outstanding. Raised during design review, all resolved:

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
- **Path portability**: `PROJECT_DIR` is now derived from the bundle's
  own on-disk location (`$0` → `SCRIPT_DIR` → four levels up) instead of
  a hardcoded absolute path or a test-only env var override, per the
  revised requirements.md (2026-08-31) requiring the launcher to work
  regardless of where the project is checked out, on any Mac with the
  repo cloned and `.venv` set up. This relies on macOS setting `$0` to
  the bundle executable's real invocation path, which holds for both
  Finder double-click and `open`. Moving/copying the `.app` bundle itself
  out of the repository (e.g. into `/Applications`) is explicitly out of
  scope (requirements' Out of scope) — the operator adds a Dock alias to
  the in-repo bundle instead.
