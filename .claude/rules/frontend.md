---
paths:
  - "frontend/src/**/*"
---

# Frontend Rules

Applies to all code under `frontend/src/`. See
`.claude/rules/structure.md` for the full directory layout.

## Single Responsibility Principle

- One component, one job. A component that both fetches/owns data and
  renders a non-trivial view should usually be split into a container
  (data/state) and a presentational component (rendering).
- Keep API access, state management, and presentation in separate
  modules/files rather than inline in a single large component.

## Domain alignment

- Frontend types/DTOs for a feature should mirror the DTOs defined in that
  feature's `specs/<feature-name>/design.md` (Application Layer § DTOs and
  API Layer § Endpoints) — don't invent a divergent shape client-side.
- Domain terminology used in component/prop/state names should match the
  glossary in `.claude/rules/product.md` and the entity/value-object names
  in the relevant design.md, so the same concept isn't named two different
  ways across backend and frontend.

## Conventions

- All frontend source lives under `frontend/src/`; `frontend/package.json`
  is the single source of truth for dependencies — don't add a package
  without checking it's actually needed and updating that file.
