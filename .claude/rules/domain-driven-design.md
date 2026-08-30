# Domain-Driven Design Rules

## Appropriate Use of DDD Patterns

- Do not introduce DDD patterns merely to satisfy terminology.
- Use an Entity only when identity and lifecycle matter.
- Use a Value Object only when the concept has domain meaning.
- Use an Aggregate only when an explicit consistency boundary is needed.
- Use a Domain Service only when behavior genuinely does not belong to an Entity or Value Object.

Without a domain-driven justification, do not introduce:
- factories
- domain events
- repositories
- domain services
- aggregates


## Layering (see docs/domain/ for the current model)
api → application → domain ← infrastructure
- `domain/` imports NOTHING from other layers
  If a domain class needs external data, define an interface in `domain/` and
  implement it in `infrastructure/`.
- `application/` imports from `domain/` only
- `application/` orchestrates domain objects to fulfill a use case; it does not
  contain business rules itself — those belong in the domain layer.
- `infrastructure/` implements `domain/` interfaces
- Only `infrastructure/` may import ORM/framework code.
- `api/` depends on `application/` (never `domain/` directly)


## Tactical patterns
- **Entity**: has identity that persists across state changes. Identity comparison,
  not attribute comparison.
- **Value Object**: immutable, compared by value, no identity. Prefer these over
  primitive types for anything with domain meaning (Money, EmailAddress, not float/str).
- **Aggregate**: a cluster of entities/value objects with one Aggregate Root that
  owns all invariants. External code only references the aggregate by the root's ID.
- **Repository**: one per aggregate root, not per table. Interface lives in `domain/`.
- **Domain Event**: something that happened, named in past tense (OrderPlaced,
  not PlaceOrder).

## Process
- Before writing design.md, read `docs/domain/glossary.md` and
  `docs/domain/bounded-contexts.md`. Reuse existing terms — do not invent a
  synonym for a concept that already has a name.
- If a feature introduces a new domain concept (entity, value object, aggregate,
  event), add it to `docs/domain/` as part of the design phase, not as an
  afterthought.
