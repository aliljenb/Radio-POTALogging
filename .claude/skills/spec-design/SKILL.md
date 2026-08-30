---
name: spec-design
description: SDD - Generate design.md for a feature — a DDD domain model plus application/infrastructure/API layering — following the project's SDD template.
argument-hint: [feature-name]
disable-model-invocation: true      # only run when the user explicitly types /spec-design
allowed-tools: Read Write Glob Grep # no Bash/Edit — this phase never touches code
---

If not already existing, generate `specs/$1/design.md` using the template at
`skills/spec-design/template.md`.

## Preconditions

- If `specs/$1/requirements.md` does not exist, refuse and point the user to
  `/spec-requirements $1` first. Do not create a design without requirements.
- If `specs/$1/requirements.md` exists but its `## Status` checklist does not
  have `Approved` checked, stop and tell the user requirements must be
  approved before design can proceed. Do not proceed on an assumption that
  it's "close enough."

## Before writing or editing anything

If any part of the technical approach is ambiguous or has more than one
reasonable design — aggregate boundaries, what belongs in one aggregate vs.
another, sync vs. async processing, API shape, which existing domain
concepts this feature reuses vs. extends — stop and ask control questions
before drafting or changing design.md.

- Ask one question at a time, or a small batch of tightly related ones.
- Each question must offer 2-4 concrete, mutually exclusive multiple-choice
  options (plus the user can always answer "Other" with free text).
- Use the `AskUserQuestion` tool so the options are clickable. Only fall
  back to a lettered list (A/B/C/D) in chat if that tool isn't available.
- Do not proceed to writing or editing design.md until blocking ambiguities
  are resolved. Minor, non-blocking assumptions can just be stated inline
  in the design instead of asked about.

## Domain-Driven Design requirements

This project practices DDD. Every design.md must:

- Derive the domain model directly from the user stories in
  `specs/$1/requirements.md` — each noun/behavior in a story should map to
  an entity, value object, or domain event; do not invent domain concepts
  the requirements don't support.
- Identify aggregates and their roots, and keep aggregate boundaries small
  — one aggregate per transactional consistency boundary, per
  `.claude/rules/structure.md`'s domain/application/infrastructure/api
  layering.
- Keep the domain model free of framework or infrastructure concerns
  (no ORM, no HTTP, no I/O) — those belong in the Infrastructure and API
  sections only.
- Express repositories as abstract interfaces (ports) in the domain model;
  concrete implementations (adapters) belong under Infrastructure.

## Single Responsibility Principle

For every module/class introduced in the design, state its single
responsibility in the "Single Responsibility Check" table. If a
module/class needs more than one sentence without "and"/"or" to describe
its job, split it before marking design.md Approved.

## Restrictions

- Never modify files in `src/` or `frontend/src/` while completing this
  skill — Design phase is planning-only, per
  `.claude/rules/sdd-workflow.md`.
- Only write to `specs/$1/design.md`.

Read the file `specs/$1/design.md` and help me create or refine the design.
Update `specs/$1/design.md` with the refined design, then remind the user
that design.md must be explicitly approved (Status: Approved) before
`/spec-tasks $1` can run.
