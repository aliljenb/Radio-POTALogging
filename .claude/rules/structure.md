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
├── frontend/                       # not used by this project — see note below
│   ├── src/
│   └── package.json
├── macos/                          # macOS .app bundle launcher(s); no Python source, see note below
│   └── POTA QSO Logging.app/
│       └── Contents/
│           ├── Info.plist
│           └── MacOS/
│               └── launch
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
│   │   └── repositories/           # concrete repo implementations — the "adapters"
│   └── api/                        # presentation layer: PyQt windows/widgets, DI wiring
├── tests/
│   └── macos/                      # tests for macos/ launcher scripts (mirrors macos/, not src/)
├── .gitignore
├── pyproject.toml
└── README.md
```

## Conventions

- All backend source code lives under `src/<python_module>/`
- This project is a PyQt desktop GUI, not a web app: `frontend/` is unused
  template scaffolding, and `src/<python_module>/api/` holds the PyQt
  presentation layer (windows/widgets/DI wiring) instead of HTTP routes
  (see `.claude/rules/tech.md` decision log, 2026-08-30)
- There is no ORM/database, so `infrastructure/` has no `db/` subfolder —
  persistence is file-based, under `infrastructure/repositories/`
- `macos/` holds OS-level launcher bundles (plain shell script + Info.plist,
  no Python) for this machine only — see `specs/app-launcher/design.md`;
  it is not part of the `src/<python_module>/` package or its DDD layering
- Test files mirror the backend source tree; `tests/macos/` mirrors
  `macos/` the same way
- One spec directory per feature — specs are never shared across features
- Steering documents live under `.claude/rules/`
