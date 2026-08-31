# Requirements: app-launcher

## Status

- [x] Draft
- [x] In Review
- [x] Approved

## Introduction

The operator currently starts the QSO Logging application from a terminal
(`python -m radio_pota_logging.api.composition_root`). This feature adds a
double-clickable macOS launcher — a standard `.app` bundle the operator can
keep in the Dock — so the application can be started like any other Mac
app, without opening a terminal. The launcher must work regardless of
where on disk this project is checked out, and on any Mac (not just this
developer's current machine) — as long as the project has been cloned and
its `.venv` set up there per the README. It does not need to run on a Mac
that doesn't have this project checked out; it is not a standalone,
dependency-free bundle (see Out of scope).

## User stories

### Story 1: Launch the app from the Dock without a terminal

> As an **operator**, I want to **start the QSO Logging application by
> clicking an icon in the Dock**, so that **I don't need to open a
> terminal to log QSOs**.

**Acceptance criteria:**

- [ ] THE SYSTEM SHALL be packaged as a standard macOS `.app` bundle
      (a folder containing `Info.plist` and an executable) checked into
      the repository at `macos/POTA QSO Logging.app`, so it behaves like
      any other Mac application and shows a normal Dock icon while
      running.
- [ ] WHEN the operator double-clicks the launcher (from Finder or the
      Dock), THE SYSTEM SHALL start the QSO Logging application's PyQt
      GUI without opening a visible Terminal window.
- [ ] THE SYSTEM SHALL locate the project's root directory relative to
      the `.app` bundle's own location on disk (it does not hardcode any
      machine-specific absolute path), and SHALL run the application
      using the `.venv` Python interpreter found under that project root
      (`<project-root>/.venv/bin/python`). This makes the launcher work
      regardless of where the repository has been cloned, and on any Mac
      that has this project checked out and its `.venv` set up — not only
      this developer's current machine.
- [ ] THE SYSTEM SHALL require the `.app` bundle to remain in its
      checked-in location inside the repository (`macos/POTA QSO Logging
      .app`) for this location-relative lookup to succeed. The operator
      adds it to the Dock as an alias/shortcut to that location; copying
      or moving the `.app` bundle itself out of the repository (e.g. into
      `/Applications`) is not supported.
- [ ] IF the project's `.venv` or its Python interpreter is missing when
      the launcher runs, THEN THE SYSTEM SHALL show a native macOS alert
      describing the problem, rather than failing silently or giving no
      visible feedback.
- [ ] THE SYSTEM SHALL be delivered as a build output checked into (or
      generated into) the repository (e.g. `macos/POTA QSO Logging.app`).
      Adding it to the Dock is a manual, one-time step the operator
      performs themselves; the feature does not automate that step.

### Story 2: A predictable place for QSO data when launched from the Dock

> As an **operator**, I want **the app to always write its session file
> and ADIF exports to the same known folder when I start it from the
> Dock**, so that **I can find my logs without having to remember which
> directory I launched from**.

**Acceptance criteria:**

- [ ] WHEN the operator starts the application via this launcher, THE
      SYSTEM SHALL run it with `~/POTA Logs` as its working directory, so
      the existing session-persistence behavior (qso-entering Story 3)
      reads/writes `.qso_session.json` there.
- [ ] IF `~/POTA Logs` does not already exist, THEN THE SYSTEM SHALL
      create it before starting the application.
- [ ] THE SYSTEM SHALL NOT change how the application behaves when
      started directly from a terminal (outside this launcher); that
      continues to use the current working directory at invocation, per
      the existing qso-entering feature.

## Out of scope

- A custom application icon; the default generic macOS app icon is
  acceptable for this feature.
- A fully self-contained, dependency-free launcher that runs on a Mac
  without this project checked out (no bundled interpreter, no
  py2app/PyInstaller-style standalone packaging). The launcher still
  requires the project repository and its `.venv` to be present on the
  target Mac.
- Copying or moving the `.app` bundle itself out of the repository (e.g.
  into `/Applications`); only adding a Dock alias/shortcut to the
  in-repo bundle is supported.
- Automatically installing the `.app`, adding it to the Dock, or cloning
  the repository/setting up `.venv` on a new Mac — the operator does all
  of this manually, once, per the project's README.
- Rebuilding or updating the launcher automatically when the application's
  code changes.

## Open questions

None currently outstanding. Questions raised during drafting were
resolved:

- Launcher type: a lightweight hand-built `.app` wrapper (no new packaging
  tool/dependency), not a py2app-style standalone bundle.
- Portability: the repository (and its checked-in `.app` bundle) may live
  anywhere on disk, on any Mac with the project cloned and `.venv` set up;
  the launcher locates its project root relative to its own bundle
  location rather than a hardcoded path.
- Installation: the `.app` lives in the repo at a fixed path
  (`macos/POTA QSO Logging.app`); the operator adds a Dock alias to it
  themselves. It is not copied into `/Applications`.
- Working directory when Dock-launched: the fixed folder `~/POTA Logs`
  (Story 2), created automatically if missing.
