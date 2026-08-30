# Project Index

This is a Spec-Driven Development (SDD) template project. Features are
built through a phase-gated workflow, and backend code follows
Domain-Driven Design with strict Single Responsibility.

## Workflow

Each feature moves through phases in order, one spec directory per
feature under `specs/<feature-name>/`. Every phase file must be
explicitly approved (its `## Status` checklist marked `Approved`) before
the next phase's command may run.

1. `/spec-new <feature-name>` — scaffold `specs/<feature-name>/`
2. `/spec-requirements <feature-name>` — write user stories + acceptance
   criteria
3. `/spec-design <feature-name>` — write the DDD domain model and layered
   design
4. `/spec-tasks <feature-name>` — break the design into a file-by-file
   task checklist
5. `/implement-task <feature-name> [task]` — implement tasks against the
   approved plan
6. `/review <feature-name>` — check the implementation against the spec

Full phase-gate rules: `.claude/rules/sdd-workflow.md`.

## Rules

Read these before working in this repo:

- `.claude/rules/product.md` — what this product is and why (fill in per project)
- `.claude/rules/tech.md` — approved stack; ask before adding anything not listed
- `.claude/rules/structure.md` — repo layout and DDD directory conventions
- `.claude/rules/sdd-workflow.md` — phase-gate rules
- `.claude/rules/backend.md` — DDD/SRP rules for `src/**/*.py`
- `.claude/rules/frontend.md` — SRP rules for `frontend/src/**/*`
- `.claude/rules/testing.md` — testing strategy, including Playwright for applicable UI tests

## Principles

- **Domain-Driven Design**: business logic lives in `domain/`, free of
  framework/infrastructure concerns; `application/` orchestrates it;
  `infrastructure/` and `api/` are the outermost, framework-facing
  layers. See `structure.md` and `backend.md`.
- **Single Responsibility**: every module/class has exactly one reason to
  change. Design docs must state each new module's single responsibility;
  implementation and review both check code against that statement.
