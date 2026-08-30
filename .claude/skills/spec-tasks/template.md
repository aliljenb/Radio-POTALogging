# Tasks: [feature-name]

## Status

- [ ] Draft
- [ ] In Review
- [ ] Approved

## How to use this file

Each task must name the exact file(s) and function/class/method it creates
or changes, and cite the design.md section it implements. Vague tasks
("wire up the backend") are not allowed — split them until each one is a
single, independently completable unit of work with a clear file target.

## Domain Layer

- [ ] `src/<python_module>/domain/<aggregate>/entities.py` — implement
      `[EntityName]` per design.md § Entities
- [ ] `src/<python_module>/domain/<aggregate>/value_objects.py` — implement
      `[ValueObjectName]` per design.md § Value Objects
- [ ] `src/<python_module>/domain/<aggregate>/events.py` — implement
      `[EventName]` per design.md § Domain Events
- [ ] `src/<python_module>/domain/<aggregate>/exceptions.py` — implement
      `[ExceptionName]` per design.md § Domain Exceptions
- [ ] `src/<python_module>/domain/<aggregate>/repository.py` — define
      `[AggregateName]Repository` protocol per design.md § Repository
      Interfaces

## Application Layer

- [ ] `src/<python_module>/application/<aggregate>/commands.py` —
      implement `[CommandName]` per design.md § Commands
- [ ] `src/<python_module>/application/<aggregate>/queries.py` —
      implement `[QueryName]` per design.md § Queries
- [ ] `src/<python_module>/application/<aggregate>/dto.py` — implement
      `[DtoName]` per design.md § DTOs

## Infrastructure Layer

- [ ] `src/<python_module>/infrastructure/db/models.py` — implement
      `[ModelName]` ORM model per design.md § Persistence
- [ ] `src/<python_module>/infrastructure/repositories/<aggregate>_repository.py`
      — implement `[AggregateName]RepositoryImpl` per design.md §
      Repository Implementations

## API Layer

- [ ] `src/<python_module>/api/<aggregate>_router.py` — implement
      `[endpoint]` per design.md § Endpoints
- [ ] `src/<python_module>/api/schemas.py` — implement
      `[RequestSchema]`/`[ResponseSchema]` per design.md § Endpoints

## Frontend

- [ ] `frontend/src/<path>/[Component].tsx` — implement `[Component]` per
      design.md § Components

## Tests

<!-- Mirror the src/ tree under tests/. -->

- [ ] `tests/domain/<aggregate>/test_entities.py` — unit tests for
      `[EntityName]` invariants
- [ ] `tests/application/<aggregate>/test_commands.py` — unit tests for
      `[CommandName]` (domain objects only, no infra mocks needed beyond
      the repository port)
- [ ] `tests/infrastructure/repositories/test_<aggregate>_repository.py`
      — integration tests for `[AggregateName]RepositoryImpl`
- [ ] `tests/api/test_<aggregate>_router.py` — integration tests for
      `[endpoint]`

## Task Dependencies

<!-- Note ordering constraints, e.g. "Task 3 depends on Task 1". Domain
     tasks generally come first, then application, then
     infrastructure/API, then frontend. -->
