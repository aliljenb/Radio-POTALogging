# Tasks: app-launcher

## Status

- [x] Draft
- [x] In Review
- [x] Approved

## How to use this file

Each task must name the exact file(s) and function/class/method it creates
or changes, and cite the design.md section it implements. Vague tasks
("wire up the backend") are not allowed — split them until each one is a
single, independently completable unit of work with a clear file target.

## Note on this feature's structure

design.md explicitly marks the template's Domain Model / Application
Layer / Infrastructure / API Layer / Frontend sections N/A — this feature
adds no Python source under `src/`, only a macOS `.app` bundle (see
design.md § macOS Launcher Bundle). Tasks below follow that structure
instead. `.claude/rules/structure.md` was already updated during the
design phase (to document `macos/` and `tests/macos/`), so no task is
needed for it here.

## macOS Launcher Bundle

`macos/POTA QSO Logging.app/`

- [x] `Contents/Info.plist` — create with exactly these keys per
      design.md § `Contents/Info.plist`: `CFBundleName` = `POTA QSO
      Logging`, `CFBundleIdentifier` = `local.radio-pota-logging.launcher`,
      `CFBundlePackageType` = `APPL`, `CFBundleExecutable` = `launch`,
      `CFBundleShortVersionString` = `1.0`. No `CFBundleIconFile`,
      `LSUIElement`, or `LSBackgroundOnly` keys.
- [x] `Contents/MacOS/launch` — create the POSIX shell script exactly as
      specified in design.md § `Contents/MacOS/launch` (reads
      `POTA_LAUNCHER_PROJECT_DIR` with the hardcoded project path as
      default; alerts via `osascript` and exits `1` if `.venv/bin/python`
      is not executable; creates `~/POTA Logs` if missing; `cd`s into it;
      runs the app with output redirected to
      `~/POTA Logs/launcher.log`; alerts via `osascript` naming the exit
      code and log path if the app exits non-zero; exits with that same
      code). Set the executable bit (`chmod +x`) so it is a valid
      `CFBundleExecutable`.

## Tests

`tests/macos/` mirrors `macos/` (per `.claude/rules/structure.md`).

- [x] `tests/macos/test_launch.py` — implement, against
      `macos/POTA QSO Logging.app/Contents/MacOS/launch` via
      `subprocess`, all four cases from design.md § Testing Strategy:
      - `test_shows_alert_and_exits_nonzero_when_venv_missing`:
        `POTA_LAUNCHER_PROJECT_DIR` points at an empty temp dir; a stub
        `osascript` prepended to `PATH` records its invocation; assert
        `launch` exits non-zero, the stub was invoked, and
        `~/POTA Logs` (temp `HOME`) was not created.
      - `test_creates_logs_dir_and_runs_python_with_expected_argv_and_cwd`:
        `POTA_LAUNCHER_PROJECT_DIR` points at a temp dir with a stub
        `.venv/bin/python` that records its cwd and argv to a file and
        exits `0`; assert `~/POTA Logs` (temp `HOME`) was created, the
        recorded cwd is that directory, the recorded argv is `-m
        radio_pota_logging.api.composition_root`, `launch` exits `0`, and
        the `osascript` stub was not invoked.
      - `test_does_not_touch_existing_logs_directory_contents`: same
        setup as above but `~/POTA Logs` is pre-created with a marker
        file inside; assert the marker file still exists after `launch`
        runs.
      - `test_shows_alert_with_exit_code_and_log_path_on_crash`: stub
        `.venv/bin/python` prints an error message to stderr and exits
        `1`; assert `launch` exits `1`, `~/POTA Logs/launcher.log`
        contains the stub's printed message, and the `osascript` stub was
        invoked with a message naming exit code `1` and the log file's
        path.

## Task Dependencies

- `Contents/Info.plist` and `Contents/MacOS/launch` have no dependency on
  each other and may be done in either order, but both must exist (with
  `launch` executable) before the bundle is a valid, launchable `.app`.
- `tests/macos/test_launch.py` depends on `Contents/MacOS/launch` existing
  and being executable — the tests invoke it directly via `subprocess`.
