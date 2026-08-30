---
name: spec-tasks
description: SDD - Generate tasks.md for a feature — a file-by-file implementation checklist derived from design.md — following the project's SDD template.
argument-hint: [feature-name]
disable-model-invocation: true      # only run when the user explicitly types /spec-tasks
allowed-tools: Read Write Glob Grep # no Bash/Edit — this phase never touches code
---

If not already existing, generate `specs/$1/tasks.md` using the template at
`skills/spec-tasks/template.md`.

## Preconditions

- If `specs/$1/requirements.md` does not exist, refuse and point the user to
  `/spec-requirements $1` first.
- If `specs/$1/design.md` does not exist, refuse and point the user to
  `/spec-design $1` first.
- If `specs/$1/design.md` exists but its `## Status` checklist does not
  have `Approved` checked, stop and tell the user design must be approved
  before tasks can be generated. Do not proceed on an assumption that it's
  "close enough."

## Generating tasks

Read `specs/$1/design.md` in full and derive tasks directly from it:

- Every entity, value object, event, exception, and repository interface
  in the Domain Model section becomes a task naming its exact file path
  (per `.claude/rules/structure.md`'s layout) and the class/function it
  implements.
- Every command/query/DTO in the Application Layer section becomes a task
  the same way, and so on for Infrastructure, API, and Frontend sections.
- Add a matching test task for each implementation task, under `tests/`,
  mirroring the source path.
- **No vague tasks.** A task like "implement the service layer" is not
  allowed — split it into one task per file/function, each citing the
  design.md section it implements. If design.md doesn't have enough detail
  to name specific files/functions for some part of the feature, stop and
  send the user back to `/spec-design $1` to fill that gap rather than
  inventing detail here.
- Order tasks domain → application → infrastructure/API → frontend, and
  note any cross-task dependencies in the "Task Dependencies" section.

## Restrictions

- Never modify files in `src/` or `frontend/src/` while completing this
  skill — task planning does not write implementation code.
- Only write to `specs/$1/tasks.md`.

Update `specs/$1/tasks.md`, then remind the user that tasks.md must be
explicitly approved (Status: Approved) before `/implement-task $1` can run
against it.
