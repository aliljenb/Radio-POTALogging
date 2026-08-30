---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---

# Backend Rules

Applies to all Python code under `src/` and `tests/`. See
`.claude/rules/structure.md` for the full directory layout and
`.claude/rules/tech.md` for the tooling stack.

## Domain-Driven Design

- `src/<python_module>/domain/` is pure business logic: zero imports from
  frameworks, ORMs, HTTP libraries, or any other infrastructure package.
  If a domain file needs to import something outside the standard library
  or another domain module, stop and reconsider — that dependency almost
  always belongs in `application/` or `infrastructure/` instead.
- Model aggregates, entities, value objects, domain events, and domain
  exceptions explicitly — don't collapse them into a single "models.py".
  Value objects are immutable; entities have identity; only aggregate
  roots are referenced from outside their aggregate.
- Repository interfaces (ports) are declared in `domain/<aggregate>/repository.py`
  as `Protocol`/`ABC`. Concrete implementations (adapters) live in
  `infrastructure/repositories/` and depend on the port, never the other
  way around.
- `application/` orchestrates domain objects for one use case per
  command/query. It may depend on domain ports, not on infrastructure
  implementations directly (wire concrete adapters at the API/composition
  root instead).

## Single Responsibility Principle

- One class/function, one reason to change. If you're writing "and" to
  describe what a class does, split it.
- Prefer several small, well-named modules over one large one. A module
  that mixes persistence, validation, and business rules should be split
  along those lines into infrastructure/domain/application respectively.

## Conventions

- All backend source lives under `src/<python_module>/`; test files mirror
  that tree under `tests/`.
- Follow `.claude/rules/tech.md` for language version, dependency
  management, testing, and linting/type-checking tools. Don't introduce a
  package not listed there without asking first.
- New runtime dependencies get added to the table in `tech.md`, with the
  reasoning noted in its Decision log.
