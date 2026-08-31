# Implementation Notes: app-launcher

## Deviation: `LSRequiresNativeExecution` added to `Info.plist`

**Date:** 2026-08-31

**What happened:** After implementing tasks.md's `Contents/MacOS/launch`
and `Contents/Info.plist` tasks per the approved design.md, the bundle was
launched for real (via `open "macos/POTA QSO Logging.app"`, the same path
a Finder double-click takes) to verify the feature end-to-end. The
application crashed with:

```
ImportError: dlopen(.../PyQt6/QtWidgets.abi3.so, ...): Library not loaded: @rpath/QtWidgets.framework/...
Reason: ... incompatible architecture (have 'arm64', need 'x86_64')
```

**Diagnosis:**
- `.venv/bin/python` → `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12`
  is a universal binary (arm64 + x86_64 slices) — confirmed via `lipo -info`.
- The installed PyQt6's `QtWidgets.framework/Versions/A/QtWidgets` is
  arm64-only — confirmed via `lipo -info`.
- `open "macos/POTA QSO Logging.app"` (no arch flag) reproducibly ran the
  bundle under Rosetta (x86_64) on this machine; `open --arch arm64
  "macos/POTA QSO Logging.app"` launched it natively and it started
  successfully. This isolated the crash to a Rosetta-vs-native launch
  default for this bundle, not a broken `.venv`/interpreter.

**Fix attempt 1 (approved by user before applying):** added
`LSRequiresNativeExecution = true` to `Contents/Info.plist`, re-registered
the bundle with `lsregister -f`, and retested via plain `open`. This did
**not** fix the crash — the app still launched under Rosetta and hit the
same `ImportError`. `LSRequiresNativeExecution` is documented to force
native execution for a bundle's `CFBundleExecutable`, but this bundle's
`CFBundleExecutable` is a POSIX shell script rather than a Mach-O binary;
LaunchServices' architecture-selection logic did not treat that the same
way. The key was left in place (harmless, still Apple's documented
signal) but is not what actually fixed the issue.

**Fix attempt 2 (the one that worked):** changed `Contents/MacOS/launch`
itself to stop trusting whatever architecture macOS chose to run the
script under, and instead force the Python child process to the Mac's
*true* native architecture directly:

```sh
if [ "$(sysctl -n hw.optional.arm64 2>/dev/null)" = "1" ]; then
    NATIVE_ARCH="arm64"
else
    NATIVE_ARCH="x86_64"
fi
arch -"$NATIVE_ARCH" "$PYTHON" -m radio_pota_logging.api.composition_root > "$LOG_FILE" 2>&1
```

This relies on two verified-by-testing facts about Apple Silicon Macs:
`sysctl -n hw.optional.arm64` reports the *hardware's* real capability
(`1`) even when read from inside a Rosetta-translated process (unlike
`uname -m`, which reports the calling process's translated architecture,
not the hardware's), and `arch -<arch> <command>` can spawn a child at a
specific architecture regardless of the calling shell's own translated
state. Verified directly: `arch -x86_64 sysctl -n hw.optional.arm64` still
printed `1`, and `arch -x86_64 /bin/sh -c 'uname -m; arch -arm64 uname -m'`
printed `x86_64` then `arm64` for the same shell. This also keeps the
launcher working on a hypothetical Intel Mac (`hw.optional.arm64` is
unset there, so it falls back to `x86_64`) without hardcoding one
architecture, consistent with requirements' "any Mac" scope.

**Root cause of the Rosetta default itself was not fully identified** —
plain `open "macos/POTA QSO Logging.app"` reproducibly launched the
bundle under Rosetta on this machine even after the `Info.plist` fix,
while running the same script directly from a native arm64 shell (or via
`open --arch arm64`) ran it natively. This may be specific to
script-based `CFBundleExecutable` bundles or to a LaunchServices
preference cached before this bundle existed. The `arch`-forcing fix in
`launch` sidesteps the question entirely by not depending on how the
script itself got launched.

**Verification after fix attempt 2:** `open "macos/POTA QSO Logging.app"`
(no arch flag, i.e. the same path a Finder double-click takes) launched
the app successfully — `radio_pota_logging.api.composition_root` started
natively and stayed running, no crash, no `launcher.log` entry, no alert.
Process was then terminated manually (`pkill`) since this was a manual
verification run, not a persistent launch. `pytest tests/macos/test_launch.py`
(5/5), `ruff check`, and `mypy` all still pass against the updated script
and tests.

**Spec updates:** `design.md` § `Contents/Info.plist` and §
`Contents/MacOS/launch`, and both corresponding tasks in `tasks.md`, were
updated to include this key and the `arch`-forcing logic with the
reasoning above.
