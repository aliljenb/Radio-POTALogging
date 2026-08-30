# Project Structure

> Update this file whenever new top-level files or directories are added.

```
<Project>/
├── .claude/
│   ├── skills/
│   │   ├── spec-requirements/
│   │   │   ├── SKILL.md
│   │   │   └── template.md            # requirements.md template
│   │   ├── spec-design/
│   │   │   ├── SKILL.md
│   │   │   └── template.md            # design.md template
│   │   ├── spec-tasks/
│   │   │   ├── SKILL.md
│   │   │   └── template.md            # tasks.md template
│   │   ├── implement-task/
│   │   │   └── SKILL.md
│   │   └── review/
│   │       └── SKILL.md
│   ├── rules/                         # project-wide steering & restrictions
│   │   ├── sdd-workflow.md            # phase-gate rules (no skipping phases, etc.)
│   │   ├── product.md                 # what/why — Kiro-style steering doc
│   │   ├── tech.md                    # tech steering/constraints (Q3)
│   │   ├── structure.md               # repo conventions, naming, layering
│   │   ├── backend.md                 # path-scoped: src/**/*.py
│   │   └── frontend.md                # path-scoped: frontend/src/**/*
│   └── CLAUDE.md                      # short, top-level index/entry point
├── frontend/
│   ├── src/
│   └── package.json
├── specs/
│   ├── <feature-name-1>/
│   │   ├── requirements.md
│   │   ├── design.md
│   │   └── tasks.md
│   └── <feature-name-2>/
│       └── ...
├── src/<python_module>/
│   ├── domain/                    # pure business logic — zero framework/infra imports
│   │   ├── <aggregate_name>/
│   │   │   ├── entities.py        # entities (have identity)
│   │   │   ├── value_objects.py   # value objects (immutable, no identity)
│   │   │   ├── events.py          # domain events
│   │   │   ├── exceptions.py      # domain-specific exceptions
│   │   │   └── repository.py      # abstract repository interface (Protocol/ABC) — the "port"
│   │   └── shared/                # shared value objects/exceptions across aggregates
│   ├── application/                # use cases — orchestrate domain objects, no framework code
│   │   ├── <aggregate_name>/
│   │   │   ├── commands.py         # write use cases
│   │   │   ├── queries.py          # read use cases
│   │   │   └── dto.py              # data transfer objects crossing the boundary
│   ├── infrastructure/             # everything that talks to the outside world
│   │   ├── db/                     # ORM models, migrations, session management
│   │   └── repositories/           # concrete repo implementations — the "adapters"
│   └── api/                        # FastAPI routers, request/response schemas, DI wiring
├── tests/
├── .gitignore
├── pyproject.toml
└── README.md
```

## Conventions

- All backend source code lives under `src/<python_module>/`
- All frontend source code lives under `frontend/src`
- Test files mirror the backend source tree
- One spec directory per feature — specs are never shared across features
- Steering documents live under `.claude/rules/`
