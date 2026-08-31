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
      `CFBundleShortVersionString` = `1.0`, `LSRequiresNativeExecution` =
      `true` (added post-approval — see implementation-notes.md — to force
      native/arm64 execution and prevent macOS defaulting the bundle to
      Rosetta). No `CFBundleIconFile`, `LSUIElement`, or
      `LSBackgroundOnly` keys.
- [x] `Contents/MacOS/launch` — rewrite the POSIX shell script exactly as
      specified in design.md § `Contents/MacOS/launch` (previous version
      used `POTA_LAUNCHER_PROJECT_DIR`/a hardcoded default path — replace
      it entirely): resolves `SCRIPT_DIR` from `$0`'s own directory
      (`cd "$(dirname "$0")" && pwd`), then `PROJECT_DIR` by walking up
      four levels from `SCRIPT_DIR` (`Contents/MacOS` → `Contents` →
      `POTA QSO Logging.app` → `macos` → project root); alerts via
      `osascript` and exits `1` if `$PROJECT_DIR/.venv/bin/python` is not
      executable; creates `~/POTA Logs` if missing; `cd`s into it; runs
      the app via `arch -"$NATIVE_ARCH"` (added post-approval — see
      implementation-notes.md — to force the true native architecture via
      `sysctl -n hw.optional.arm64` regardless of the Rosetta/native state
      the script itself was launched under) with output redirected to
      `~/POTA Logs/launcher.log`; alerts via `osascript` naming the exit
      code and log path if the app exits non-zero; exits with that same
      code. Set the executable bit (`chmod +x`) so it is a valid
      `CFBundleExecutable`.

## Tests

`tests/macos/` mirrors `macos/` (per `.claude/rules/structure.md`).

- [x] `tests/macos/test_launch.py` — rewrite against the new
      location-relative `launch`, per design.md § Testing Strategy. Add a
      shared fixture/helper that builds a throwaway "fake clone" temp
      directory tree reproducing the real bundle layout —
      `<fake-clone>/macos/POTA QSO Logging.app/Contents/MacOS/launch`
      (copied from the real script) plus `<fake-clone>/.venv/bin/python`
      — since `POTA_LAUNCHER_PROJECT_DIR` no longer exists for tests to
      point at. All five cases:
      - `test_resolves_project_dir_from_bundle_location_regardless_of_where_the_clone_lives`
        (new): build two fake clones in unrelated temp directories, each
        with its own stub `.venv/bin/python` recording cwd/argv; run
        `launch` from each; assert each run's stub recorded that fake
        clone's own paths, proving `PROJECT_DIR` resolution follows the
        bundle's location rather than any fixed path.
      - `test_shows_alert_and_exits_nonzero_when_venv_missing`: fake
        clone with no `.venv` at all; a stub `osascript` prepended to
        `PATH` records its invocation; assert `launch` exits non-zero,
        the stub was invoked, and `~/POTA Logs` (temp `HOME`) was not
        created.
      - `test_creates_logs_dir_and_runs_python_with_expected_argv_and_cwd`:
        fake clone with a stub `.venv/bin/python` that records its cwd
        and argv to a file and exits `0`; run `launch` with `HOME` set to
        another temp dir; assert `~/POTA Logs` (temp `HOME`) was created,
        the recorded cwd is that directory, the recorded argv is `-m
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
