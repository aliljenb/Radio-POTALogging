---
name: review
description: SDD - Review a feature's implementation against its approved requirements.md/design.md/tasks.md — checks task completion, DDD layering purity, and SRP.
argument-hint: [feature-name]
disable-model-invocation: true
allowed-tools: Read Glob Grep Bash(pytest:*) Bash(ruff:*) Bash(mypy:*) Bash(git diff:*) Bash(git log:*)
---

Review the implementation of feature **$1** against its spec. Read
`specs/$1/requirements.md`, `specs/$1/design.md`, and `specs/$1/tasks.md`
in full before looking at any code.

This skill is read-only analysis — it reports findings, it does not edit
code or spec files.

## Checks to run

1. **Task completion** — every checked-off task in tasks.md must have
   corresponding code at the file path it named. Flag any checked task
   whose file doesn't exist or clearly doesn't do what the task described.
   Flag any unchecked task that actually does have an implementation
   (tasks.md is stale).
2. **Requirements coverage** — every acceptance criterion in
   requirements.md should be traceable to at least one task/test. Flag
   gaps.
3. **DDD layering purity**, per `.claude/rules/structure.md`:
   - `domain/` files must import no framework/infrastructure packages
     (no ORM, no HTTP client, no framework request/response types).
   - `application/` files must not talk to the database/HTTP directly —
     only through repository interfaces defined in `domain/`.
   - Repository interfaces (ports) live in `domain/`; implementations
     (adapters) live in `infrastructure/`.
4. **Single Responsibility** — for each new/changed class or module,
   check it against the "Single Responsibility Check" table in design.md.
   Flag any class/function that has grown a second responsibility beyond
   what's documented, or any responsibility documented but not reflected
   in the code.
5. **Test coverage** — `tests/` should mirror the `src/` tree for
   everything touched. Run `pytest` for the affected paths, `ruff check`,
   and `mypy` on changed files; report failures.
6. **Scope discipline** — use `git diff`/`git log` to confirm changed
   files match what tasks.md scoped for this feature; flag unrelated
   changes bundled in.

## Reporting

Summarize findings grouped by severity (blocking vs. non-blocking).
For each finding, cite the file/line and the specific requirements.md,
design.md, or tasks.md item it violates. Do not fix issues yourself —
this skill only reports; fixes go back through `/implement-task` (or a
`/spec-design` revision if the design itself needs to change).
