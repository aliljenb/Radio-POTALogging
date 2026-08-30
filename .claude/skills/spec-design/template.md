# Design: [feature-name]

## Status

- [ ] Draft
- [ ] In Review
- [ ] Approved

## Overview

<!-- One paragraph: the technical approach in plain language. -->

## Domain Model

> Pure business logic. Zero framework/infra imports. Lives under
> `src/<python_module>/domain/<aggregate_name>/`.

- Bounded context:
- New/changed aggregates:
- New domain events:
- Repository interface changes:

### Aggregates

<!-- Name each aggregate and its aggregate root. One aggregate = one
     transactional consistency boundary. -->

- **[AggregateName]** — root: `[EntityName]`

### Entities

<!-- Objects with identity that persists across changes. -->

| Entity | Identity | Key attributes | Invariants |
|--------|----------|-----------------|------------|
|        |          |                 |            |

### Value Objects

<!-- Immutable, no identity, defined by their attributes. -->

| Value Object | Attributes | Validation rules |
|--------------|------------|-------------------|
|              |            |                   |

### Domain Events

<!-- Facts that happened in the domain, past tense. -->

| Event | Raised when | Carries |
|-------|-------------|---------|
|       |             |         |

### Domain Exceptions

| Exception | Raised when |
|-----------|-------------|
|           |             |

### Repository Interfaces (ports)

<!-- Abstract interfaces only (Protocol/ABC) — no persistence details here. -->

- `[AggregateName]Repository`: `get(id)`, `add(entity)`, `...`

## Application Layer (Use Cases)

> Orchestrates domain objects. No framework code. Lives under
> `src/<python_module>/application/<aggregate_name>/`.

- Use cases:

### Commands (write use cases)

| Command | Input DTO | Domain objects touched | Output |
|---------|-----------|--------------------------|--------|
|         |           |                          |        |

### Queries (read use cases)

| Query | Input | Output DTO |
|-------|-------|------------|
|       |       |            |

### DTOs

<!-- Data crossing the application boundary — not domain objects. -->

## Infrastructure

> Everything that talks to the outside world. Lives under
> `src/<python_module>/infrastructure/`.

### Persistence

<!-- ORM models, migrations, session/unit-of-work management. -->

### Repository Implementations (adapters)

<!-- Concrete classes implementing the ports declared above. -->

## API Layer

> Lives under `src/<python_module>/api/`.

### Endpoints

| Method | Path | Command/Query used | Request schema | Response schema |
|--------|------|---------------------|------------------|-------------------|
|        |      |                     |                  |                   |

## Frontend Design

<!-- Only if this feature has UI. Components under frontend/src/. -->

### Components

| Component | Responsibility | Consumes (API/state) |
|-----------|-----------------|------------------------|
|           |                 |                        |

### State management

<!-- Where feature state lives and how it flows. -->

## Single Responsibility Check

<!-- One line per new module/class stating its one reason to change.
     Anything with two or more reasons must be split before Approved. -->

| Module/Class | Single responsibility |
|---------------|-------------------------|
|               |                         |

## Testing Strategy

<!-- Mirrors src/ under tests/. Note unit vs integration boundaries,
     e.g. domain tests need no mocks/infra at all. -->

## Open Questions / Risks

- [ ]
