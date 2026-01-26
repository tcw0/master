"""
Pydantic models for Technical Architecture artifact (Phase 5).

Schema design principles:
- Capture hexagonal architecture layers per bounded context
- Model ACL and integration patterns explicitly
- Support C4 and component diagram generation
- Enable code scaffolding from architecture decisions
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


# Layer types for hexagonal architecture
LayerType = Literal["domain", "application", "infrastructure", "presentation"]

# API types for published interfaces
APIType = Literal["rest", "graphql", "grpc", "events", "websocket"]

# Pattern names for technical decisions
PatternName = Literal[
    "repository",
    "unit_of_work",
    "specification",
    "domain_events",
    "cqrs",
    "event_sourcing",
    "saga",
    "outbox",
    "factory",
    "domain_service",
]


class Component(BaseModel):
    """A component within an architecture layer."""

    name: str = Field(
        ...,
        description="Component name (e.g., 'BookingRepository', 'CreateBookingHandler')"
    )
    type: str = Field(
        ...,
        description="Component type (e.g., 'Repository', 'ApplicationService', 'Controller')"
    )
    description: str = Field(
        ...,
        description="What this component does"
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="Other components this depends on"
    )


class DomainLayer(BaseModel):
    """
    Domain layer - pure business logic, no infrastructure dependencies.
    
    Contains: Entities, Value Objects, Domain Services, Repository Interfaces, Domain Events
    """

    aggregates: list[str] = Field(
        ...,
        description="Aggregate names implemented in this layer"
    )
    entities: list[str] = Field(
        default_factory=list,
        description="Entity classes (including aggregate roots)"
    )
    value_objects: list[str] = Field(
        default_factory=list,
        description="Value object classes"
    )
    domain_services: list[Component] = Field(
        default_factory=list,
        description="Domain services for cross-aggregate logic"
    )
    repository_interfaces: list[str] = Field(
        default_factory=list,
        description="Repository interface definitions (e.g., 'IBookingRepository')"
    )
    domain_events: list[str] = Field(
        default_factory=list,
        description="Domain event classes"
    )
    specifications: list[str] = Field(
        default_factory=list,
        description="Specification classes for complex queries"
    )


class ApplicationLayer(BaseModel):
    """
    Application layer - use case orchestration, no business logic.
    
    Contains: Application Services, Command/Query Handlers, DTOs, Event Handlers
    """

    application_services: list[Component] = Field(
        default_factory=list,
        description="Application/use case service classes"
    )
    command_handlers: list[Component] = Field(
        default_factory=list,
        description="Command handler classes (if using CQRS)"
    )
    query_handlers: list[Component] = Field(
        default_factory=list,
        description="Query handler classes (if using CQRS)"
    )
    event_handlers: list[Component] = Field(
        default_factory=list,
        description="Domain event handler classes"
    )
    dtos: list[str] = Field(
        default_factory=list,
        description="Data transfer object classes"
    )
    commands: list[str] = Field(
        default_factory=list,
        description="Command classes (input DTOs for writes)"
    )
    queries: list[str] = Field(
        default_factory=list,
        description="Query classes (input DTOs for reads)"
    )


class InfrastructureLayer(BaseModel):
    """
    Infrastructure layer - technical implementations.
    
    Contains: Repository Implementations, External Adapters, Persistence, Messaging
    """

    repository_implementations: list[Component] = Field(
        default_factory=list,
        description="Repository implementation classes"
    )
    persistence_models: list[str] = Field(
        default_factory=list,
        description="ORM/database model classes"
    )
    external_service_adapters: list[Component] = Field(
        default_factory=list,
        description="Adapters for external services (e.g., 'SendGridEmailAdapter')"
    )
    messaging_adapters: list[Component] = Field(
        default_factory=list,
        description="Message queue/event bus adapters"
    )
    configuration: list[str] = Field(
        default_factory=list,
        description="Configuration and setup classes"
    )


class PresentationLayer(BaseModel):
    """
    Presentation layer - API and UI concerns.
    
    Contains: Controllers, GraphQL Resolvers, Request/Response Models
    """

    controllers: list[Component] = Field(
        default_factory=list,
        description="REST/API controllers"
    )
    graphql_resolvers: list[Component] = Field(
        default_factory=list,
        description="GraphQL resolvers (if applicable)"
    )
    request_models: list[str] = Field(
        default_factory=list,
        description="API request DTOs"
    )
    response_models: list[str] = Field(
        default_factory=list,
        description="API response DTOs"
    )
    middleware: list[str] = Field(
        default_factory=list,
        description="Middleware components (auth, logging, etc.)"
    )


class HexagonalArchitecture(BaseModel):
    """
    Complete hexagonal (ports & adapters) architecture for a bounded context.
    
    Designed for component diagram generation and code scaffolding.
    """

    domain_layer: DomainLayer = Field(
        ...,
        description="Core domain logic"
    )
    application_layer: ApplicationLayer = Field(
        ...,
        description="Use case orchestration"
    )
    infrastructure_layer: InfrastructureLayer = Field(
        ...,
        description="Technical implementations"
    )
    presentation_layer: PresentationLayer = Field(
        ...,
        description="API/UI layer"
    )


class AntiCorruptionLayer(BaseModel):
    """
    Anti-Corruption Layer design between contexts.
    
    Protects the downstream context from upstream model pollution.
    """

    name: str = Field(
        ...,
        description="ACL name (e.g., 'PaymentGatewayACL')"
    )
    source_context: str = Field(
        ...,
        description="External/upstream context name"
    )
    target_context: str = Field(
        ...,
        description="The context being protected"
    )
    translator_services: list[Component] = Field(
        ...,
        description="Services that translate between models"
    )
    facade_interface: Optional[str] = Field(
        None,
        description="Simplified interface exposed to target context"
    )
    translated_concepts: list[str] = Field(
        default_factory=list,
        description="Concepts being translated (e.g., 'ExternalPayment -> DomainPayment')"
    )
    rationale: str = Field(
        ...,
        description="Why this ACL is needed"
    )


class PublishedInterface(BaseModel):
    """
    A published API or event interface from a bounded context.
    
    Documents what a context exposes to others.
    """

    context_name: str = Field(
        ...,
        description="The context publishing this interface"
    )
    interface_type: APIType = Field(
        ...,
        description="Type of interface"
    )
    name: str = Field(
        ...,
        description="Interface name (e.g., 'BookingAPI', 'ReservationEvents')"
    )
    endpoints: list[str] = Field(
        default_factory=list,
        description="API endpoints (e.g., 'POST /bookings', 'GET /rooms/{id}')"
    )
    events_published: list[str] = Field(
        default_factory=list,
        description="Events published (e.g., 'BookingConfirmed', 'RoomReleased')"
    )
    consumers: list[str] = Field(
        default_factory=list,
        description="Contexts or systems that consume this interface"
    )
    versioning_strategy: Optional[str] = Field(
        None,
        description="How this API is versioned"
    )


class TechnicalPattern(BaseModel):
    """
    A technical pattern applied in the architecture.
    
    Documents architectural decisions and their rationale.
    """

    pattern: PatternName = Field(
        ...,
        description="Pattern name"
    )
    applied_in: list[str] = Field(
        ...,
        description="Contexts or aggregates where this pattern is used"
    )
    rationale: str = Field(
        ...,
        description="Why this pattern was chosen"
    )
    implementation_notes: Optional[str] = Field(
        None,
        description="Specific implementation guidance"
    )


class ContextArchitecture(BaseModel):
    """
    Complete architecture design for a single bounded context.
    
    Main unit for C4 container/component diagrams.
    """

    context_name: str = Field(
        ...,
        description="Name of the bounded context"
    )
    description: str = Field(
        ...,
        description="Brief description of this context's technical architecture"
    )

    # Hexagonal layers
    layers: HexagonalArchitecture = Field(
        ...,
        description="Layer breakdown following hexagonal architecture"
    )

    # Integration
    anti_corruption_layers: list[AntiCorruptionLayer] = Field(
        default_factory=list,
        description="ACLs protecting this context"
    )
    published_interfaces: list[PublishedInterface] = Field(
        default_factory=list,
        description="APIs/events this context publishes"
    )
    consumed_interfaces: list[str] = Field(
        default_factory=list,
        description="Interfaces from other contexts this consumes"
    )

    # Technical choices
    persistence_technology: str = Field(
        ...,
        description="Database technology (e.g., 'PostgreSQL', 'MongoDB')"
    )
    messaging_technology: Optional[str] = Field(
        None,
        description="Message broker if used (e.g., 'RabbitMQ', 'Kafka')"
    )


class DeploymentUnit(BaseModel):
    """
    A deployment unit (service/container) grouping one or more bounded contexts.
    """

    name: str = Field(
        ...,
        description="Deployment unit/service name"
    )
    contexts_included: list[str] = Field(
        ...,
        description="Bounded contexts deployed together"
    )
    rationale: str = Field(
        ...,
        description="Why these contexts are deployed together"
    )
    scaling_considerations: Optional[str] = Field(
        None,
        description="Scaling and performance notes"
    )


class ArchitectureArtifact(BaseModel):
    """
    Complete Technical Architecture artifact for Phase 5 of the DDD workflow.
    
    Designed for:
    - Machine-readable JSON storage
    - C4 system/container diagram generation
    - Hexagonal architecture component diagrams
    - Code scaffolding and project structure generation
    """

    # Per-context architecture
    context_architectures: list[ContextArchitecture] = Field(
        ...,
        description="Architecture design for each bounded context"
    )

    # Cross-cutting patterns
    technical_patterns: list[TechnicalPattern] = Field(
        ...,
        description="Technical patterns applied across the system"
    )

    # Integration strategy
    integration_approach: str = Field(
        ...,
        description="Overall integration strategy (e.g., 'Event-driven with REST for queries')"
    )
    event_bus_technology: Optional[str] = Field(
        None,
        description="Central event bus technology if used"
    )
    api_gateway: Optional[str] = Field(
        None,
        description="API gateway approach if used"
    )

    # Deployment
    deployment_units: list[DeploymentUnit] = Field(
        default_factory=list,
        description="Suggested deployment units/services"
    )
    deployment_approach: Optional[str] = Field(
        None,
        description="Deployment strategy (e.g., 'Kubernetes microservices', 'Modular monolith')"
    )

    # Concerns and recommendations
    infrastructure_concerns: list[str] = Field(
        default_factory=list,
        description="Technical concerns or risks"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Architecture recommendations"
    )

    # Metadata
    schema_version: str = Field(
        default="1.0",
        description="Schema version for compatibility"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "context_architectures": [
                        {
                            "context_name": "Reservation",
                            "description": "Handles room booking lifecycle",
                            "layers": {
                                "domain_layer": {
                                    "aggregates": ["Booking", "Room"],
                                    "entities": ["Booking", "Room"],
                                    "value_objects": ["TimeSlot", "BookingId", "RoomId"],
                                    "domain_services": [
                                        {
                                            "name": "AvailabilityChecker",
                                            "type": "DomainService",
                                            "description": "Checks room availability across bookings",
                                            "dependencies": ["IBookingRepository", "IRoomRepository"]
                                        }
                                    ],
                                    "repository_interfaces": ["IBookingRepository", "IRoomRepository"],
                                    "domain_events": ["BookingCreated", "BookingConfirmed", "BookingCancelled"],
                                    "specifications": ["AvailableRoomSpecification", "UpcomingBookingsSpecification"]
                                },
                                "application_layer": {
                                    "application_services": [
                                        {
                                            "name": "BookingService",
                                            "type": "ApplicationService",
                                            "description": "Orchestrates booking use cases",
                                            "dependencies": ["IBookingRepository", "AvailabilityChecker", "IEventPublisher"]
                                        }
                                    ],
                                    "command_handlers": [],
                                    "query_handlers": [],
                                    "event_handlers": [
                                        {
                                            "name": "BookingConfirmedHandler",
                                            "type": "EventHandler",
                                            "description": "Handles BookingConfirmed event",
                                            "dependencies": ["INotificationService"]
                                        }
                                    ],
                                    "dtos": ["BookingDTO", "RoomDTO"],
                                    "commands": ["CreateBookingCommand", "CancelBookingCommand"],
                                    "queries": ["GetBookingQuery", "ListAvailableRoomsQuery"]
                                },
                                "infrastructure_layer": {
                                    "repository_implementations": [
                                        {
                                            "name": "PostgresBookingRepository",
                                            "type": "Repository",
                                            "description": "PostgreSQL implementation of IBookingRepository",
                                            "dependencies": ["DbContext"]
                                        }
                                    ],
                                    "persistence_models": ["BookingEntity", "RoomEntity"],
                                    "external_service_adapters": [],
                                    "messaging_adapters": [
                                        {
                                            "name": "RabbitMQEventPublisher",
                                            "type": "EventPublisher",
                                            "description": "Publishes domain events to RabbitMQ",
                                            "dependencies": ["IConnection"]
                                        }
                                    ],
                                    "configuration": ["ReservationDbContext", "RepositoryRegistration"]
                                },
                                "presentation_layer": {
                                    "controllers": [
                                        {
                                            "name": "BookingsController",
                                            "type": "RESTController",
                                            "description": "REST API for booking operations",
                                            "dependencies": ["BookingService"]
                                        }
                                    ],
                                    "graphql_resolvers": [],
                                    "request_models": ["CreateBookingRequest", "CancelBookingRequest"],
                                    "response_models": ["BookingResponse", "RoomResponse"],
                                    "middleware": ["AuthenticationMiddleware", "ValidationMiddleware"]
                                }
                            },
                            "anti_corruption_layers": [],
                            "published_interfaces": [
                                {
                                    "context_name": "Reservation",
                                    "interface_type": "rest",
                                    "name": "BookingAPI",
                                    "endpoints": ["POST /bookings", "GET /bookings/{id}", "DELETE /bookings/{id}"],
                                    "events_published": [],
                                    "consumers": ["Frontend"],
                                    "versioning_strategy": "URL versioning (/v1/bookings)"
                                },
                                {
                                    "context_name": "Reservation",
                                    "interface_type": "events",
                                    "name": "ReservationEvents",
                                    "endpoints": [],
                                    "events_published": ["BookingConfirmed", "BookingCancelled"],
                                    "consumers": ["Notification", "Billing"],
                                    "versioning_strategy": "Event schema versioning"
                                }
                            ],
                            "consumed_interfaces": [],
                            "persistence_technology": "PostgreSQL",
                            "messaging_technology": "RabbitMQ"
                        }
                    ],
                    "technical_patterns": [
                        {
                            "pattern": "repository",
                            "applied_in": ["Reservation", "Notification"],
                            "rationale": "Abstracts persistence for testability and flexibility",
                            "implementation_notes": "Interface in domain, implementation in infrastructure"
                        },
                        {
                            "pattern": "domain_events",
                            "applied_in": ["Reservation"],
                            "rationale": "Decouples bounded contexts via async messaging",
                            "implementation_notes": "Publish after aggregate changes, use outbox pattern for reliability"
                        }
                    ],
                    "integration_approach": "Event-driven for cross-context communication, REST for external API",
                    "event_bus_technology": "RabbitMQ",
                    "api_gateway": "Kong API Gateway",
                    "deployment_units": [
                        {
                            "name": "reservation-service",
                            "contexts_included": ["Reservation"],
                            "rationale": "Core domain, independent scaling",
                            "scaling_considerations": "Scale based on booking volume"
                        }
                    ],
                    "deployment_approach": "Kubernetes microservices",
                    "infrastructure_concerns": ["Event ordering not guaranteed with RabbitMQ"],
                    "recommendations": ["Consider Kafka if strict ordering needed", "Add circuit breakers for external integrations"],
                    "schema_version": "1.0"
                }
            ]
        }
    }
