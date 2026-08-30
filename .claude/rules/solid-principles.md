# SRP Rules

- Every class/module must have a one-sentence responsibility. If describing it
  needs "and," split it.
- A class that both validates input and persists data has two responsibilities —
  separate a validator/domain rule from the repository call.
- Application services orchestrate; they must not contain conditional business
  logic that belongs on a domain entity (e.g. `if order.total > 1000` discount
  logic belongs on the Order entity, not the OrderService).
- If a class imports from more than one of {domain, infrastructure, api}, it is
  likely doing more than one job — reconsider its boundaries.
- Prefer several small, named domain methods over one large method with several
  boolean flags controlling its behavior.
- A repository handles persistence for one aggregate.
- API route files group by resource, not by HTTP method.
- If a service method exceeds ~30 lines, it likely violates SRP — decompose it.