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
app, without opening a terminal. The launcher targets this developer's own
machine only; it is not required to be portable to another Mac.

## User stories

### Story 1: Launch the app from the Dock without a terminal

> As an **operator**, I want to **start the QSO Logging application by
> clicking an icon in the Dock**, so that **I don't need to open a
> terminal to log QSOs**.

**Acceptance criteria:**

- [ ] THE SYSTEM SHALL be packaged as a standard macOS `.app` bundle
      (a folder containing `Info.plist` and an executable) so it behaves
      like any other Mac application: it can be dragged into the Dock or
      `/Applications`, and shows a normal Dock icon while running.
- [ ] WHEN the operator double-clicks the launcher (from Finder or the
      Dock), THE SYSTEM SHALL start the QSO Logging application's PyQt
      GUI without opening a visible Terminal window.
- [ ] THE SYSTEM SHALL run the application using this project's existing
      `.venv` Python interpreter and installed dependencies at their
      current fixed location on this machine; it is explicitly not
      required to keep working if the launcher or the project is copied
      to a different machine or user account.
- [ ] IF the project's `.venv` or its Python interpreter is missing when
      the launcher runs, THEN THE SYSTEM SHALL show a native macOS alert
      describing the problem, rather than failing silently or giving no
      visible feedback.
- [ ] THE SYSTEM SHALL be delivered as a build output checked into (or
      generated into) the repository (e.g. `macos/POTA QSO Logging.app`).
      Placing it in the Dock or `/Applications` is a manual, one-time step
      the operator performs themselves; the feature does not automate
      that step.

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
- Supporting the launcher on any Mac other than this developer's machine
  (no relocatable/self-contained bundling, e.g. no py2app).
- Automatically installing the `.app` into `/Applications` or pinning it
  to the Dock — the operator does this manually, once.
- Rebuilding or updating the launcher automatically when the application's
  code changes.
- Automating first-time environment setup (`.venv` creation, dependency
  installation) — assumed already done per the project's README.

## Open questions

None currently outstanding. The three questions raised during drafting
were resolved:

- Launcher type: a lightweight hand-built `.app` wrapper (no new packaging
  tool/dependency), not a py2app-style standalone bundle.
- Portability: this machine only.
- Installation: lives in the repo; the operator drags it to the
  Dock/Applications themselves.
- Working directory when Dock-launched: the fixed folder `~/POTA Logs`
  (Story 2), created automatically if missing.
