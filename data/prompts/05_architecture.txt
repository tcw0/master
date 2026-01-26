Design the technical architecture following DDD patterns:

1. Hexagonal Architecture:
   - Domain Layer: [Entities, VOs, Domain Services, Repositories interfaces]
   - Application Layer: [Application Services, DTOs, Commands/Queries]
   - Infrastructure Layer: [Repository implementations, External service adapters]
   - Presentation Layer: [APIs (REST/GRAPHQL)]

2. For each Bounded Context:
   - Design the anti-corruption layers needed
   - Define the published events/APIs

3. Technical patterns to apply:
   - Repository pattern for aggregate persistence
   - Specification pattern for complex queries
   - Domain Events for decoupling

Show how each technical decision supports the domain model.