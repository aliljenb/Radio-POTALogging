---
name: implement-task
description: SDD - Implement one or more tasks from a feature's tasks.md, writing code that follows the approved design's domain model, DDD layering, and SRP.
argument-hint: [feature-name] [task-reference]
disable-model-invocation: true
allowed-tools: Read Write Edit Glob Grep Bash(pytest:*) Bash(ruff:*) Bash(mypy:*) Bash(git:*)
---

Implement task(s) for feature **$1** from `specs/$1/tasks.md`. If a second
argument is given, treat it as the specific task (by checkbox text or line
reference) to implement; otherwise implement the next unchecked task(s) in
file order, one at a time.

## Preconditions

- If `specs/$1/tasks.md` does not exist, refuse and point the user to
  `/spec-tasks $1` first.
- If `specs/$1/tasks.md` exists but its `## Status` checklist does not have
  `Approved` checked, stop and confirm with the user before implementing —
  do not silently build against an unapproved plan.
- Re-read `specs/$1/design.md` before implementing anything; the task
  file names files/functions, but design.md is the source of truth for
  behavior, invariants, and layering.

## Implementing a task

1. Pick the next unchecked task (or the one named by `$2`).
2. Implement exactly what it describes, in the exact file it names, per
   `.claude/rules/structure.md`'s layout:
   - `domain/` code must stay free of framework/infrastructure imports.
   - `application/` code orchestrates domain objects only — no direct
     ORM/HTTP/I/O calls; those go through repository ports.
   - `infrastructure/` and `api/` are where framework/I/O code belongs.
3. Honor Single Responsibility: if implementing a task reveals that a
   class/function is doing more than the one thing named in design.md's
   "Single Responsibility Check" table, split it rather than bolting on a
   second responsibility.
4. Write/update the matching test task from the same tasks.md alongside
   the implementation, mirroring `src/` under `tests/`.
5. If you discover the task can't be implemented as written (design.md is
   wrong, missing detail, or contradicts requirements.md), stop and raise
   it with the user rather than improvising a divergent design. Record any
   approved deviation in `specs/$1/implementation-notes.md` (see
   `skills/implement-task/template.md`) — most tasks need no entry there.
6. After implementing, run the project's checks on the changed files:
   `ruff check`, `mypy`, and `pytest` for the relevant test paths. Fix
   failures before moving on.
7. Check off the task's checkbox (and its test checkbox) in
   `specs/$1/tasks.md` only once the code exists and checks pass.

## Restrictions

- Do not implement tasks out of dependency order noted in tasks.md's "Task
  Dependencies" section.
- Do not touch files outside what the current task names. If a task turns
  out to require touching another file not listed, add a task for it in
  tasks.md (or ask the user) rather than silently expanding scope.
- Do not mark a task complete if its tests fail.

When done, report which task(s) were completed, which files changed, and
whether all checks passed.
