For each Bounded Context, let's design the Aggregates:

1. Identify Aggregate Roots (entities that control access)
2. For each Aggregate:
   - Define its consistency boundary
   - List all entities and value objects within it
   - Identify its invariants (business rules it must protect)
   - Define its domain events
   - Specify its commands/methods
3. Ensure aggregates are:
   - Small (for concurrency)
   - Focused on a single consistency boundary
   - Protecting clear business invariants

Template:
Aggregate: [Name]
- Root Entity: [Entity]
- Contains: [Entities & Value Objects]
- Invariants: [Business rules]
- Commands: [Operations]
- Events: [What it publishes]
- Size concern: [Evaluation]

Challenge any aggregate that seems too large or has unclear boundaries.