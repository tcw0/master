/**
 * TypeScript interfaces mirroring the backend Pydantic models.
 *
 * These types give compile-time safety to all artifact viewer components
 * and eliminate the need for `Record<string, unknown>`.
 */

// =============================================================================
// Phase 1 — Glossary
// =============================================================================

export interface GlossaryTerm {
  name: string;
  definition: string;
  category:
    | "entity"
    | "value_object"
    | "command"
    | "event"
    | "rule_policy"
    | "role"
    | "state"
    | "other";
  business_context: string;
  related_terms: string[];
  is_ambiguous: boolean;
  clarification_needed: string | null;
  bounded_context_hint: string | null;
}

export interface BoundedContextHint {
  context_name: string;
  term_names: string[];
  reasoning: string;
}

export interface GlossaryArtifact {
  terms: GlossaryTerm[];
  bounded_context_hints: BoundedContextHint[];
}

// =============================================================================
// Phase 2 — Event Storming
// =============================================================================

export interface Command {
  name: string;
  description: string;
  actor: string;
  target_aggregate: string;
}

export interface DomainEvent {
  name: string;
  description: string;
  triggered_by_command: string;
  aggregate: string;
}

export interface Policy {
  name: string;
  description: string;
  triggered_by_event: string;
  resulting_command: string | null;
}

export interface FlowStep {
  actor: string;
  command: string;
  aggregate: string;
  event: string;
  policy: string | null;
  next_command: string | null;
}

export interface EventFlow {
  name: string;
  description: string;
  steps: FlowStep[];
}

export interface EventStormingArtifact {
  commands: Command[];
  domain_events: DomainEvent[];
  policies: Policy[];
  flows: EventFlow[];
  ambiguities: string[];
}

// =============================================================================
// Phase 3 — Bounded Contexts
// =============================================================================

export interface BoundedContext {
  name: string;
  purpose: string;
  domain_type: "core" | "supporting" | "generic";
  key_aggregates: string[];
  ubiquitous_language_terms: string[];
}

export interface ContextRelationship {
  source_context: string;
  target_context: string;
  relationship_type:
    | "upstream_downstream"
    | "shared_kernel"
    | "customer_supplier"
    | "conformist"
    | "anti_corruption_layer"
    | "published_language"
    | "open_host_service"
    | "partnership"
    | "separate_ways";
  description: string;
}

export interface ContextSpecificMeaning {
  context_name: string;
  meaning: string;
}

export interface TermOverlap {
  term_name: string;
  contexts_and_meanings: ContextSpecificMeaning[];
}

export interface BoundedContextsArtifact {
  bounded_contexts: BoundedContext[];
  context_relationships: ContextRelationship[];
  term_overlaps: TermOverlap[];
}

// =============================================================================
// Phase 4 — Aggregates
// =============================================================================

export interface AggregateElement {
  name: string;
  element_type: "entity" | "value_object";
  description: string;
  properties: string[];
}

export interface Invariant {
  name: string;
  description: string;
}

export interface AggregateCommand {
  name: string;
  description: string;
  parameters: string[];
  emitted_events: string[];
  rules_applied: string[];
}

export interface Aggregate {
  name: string;
  bounded_context: string;
  root_entity: string;
  elements: AggregateElement[];
  invariants: Invariant[];
  commands: AggregateCommand[];
  domain_events: string[];
  size_evaluation: "small" | "moderate" | "large";
  size_rationale: string;
}

export interface AggregatesArtifact {
  aggregates: Aggregate[];
  design_decisions: string[];
}

// =============================================================================
// Phase 5 — Architecture
// =============================================================================

export interface DomainLayerElement {
  name: string;
  element_type:
    | "entity"
    | "value_object"
    | "domain_service"
    | "repository_interface"
    | "domain_event";
  description: string;
}

export interface ApplicationLayerElement {
  name: string;
  element_type:
    | "application_service"
    | "dto"
    | "command"
    | "query"
    | "command_handler"
    | "query_handler";
  description: string;
}

export interface InfrastructureLayerElement {
  name: string;
  element_type:
    | "repository_implementation"
    | "external_adapter"
    | "event_publisher"
    | "persistence_config"
    | "messaging";
  description: string;
}

export interface PresentationLayerElement {
  name: string;
  element_type:
    | "rest_controller"
    | "graphql_resolver"
    | "api_dto"
    | "middleware";
  description: string;
}

export interface HexagonalArchitecture {
  bounded_context: string;
  domain_layer: DomainLayerElement[];
  application_layer: ApplicationLayerElement[];
  infrastructure_layer: InfrastructureLayerElement[];
  presentation_layer: PresentationLayerElement[];
}

export interface AntiCorruptionLayer {
  owning_context: string;
  foreign_context: string;
  translation_description: string;
  translated_elements: string[];
}

export interface PublishedInterface {
  bounded_context: string;
  interface_type: "rest_api" | "graphql_api" | "domain_events" | "shared_kernel";
  description: string;
  exposed_operations: string[];
}

export interface TechnicalPattern {
  pattern_name: string;
  applied_in_context: string;
  justification: string;
}

export interface ArchitectureArtifact {
  architectures: HexagonalArchitecture[];
  anti_corruption_layers: AntiCorruptionLayer[];
  published_interfaces: PublishedInterface[];
  technical_patterns: TechnicalPattern[];
}

// =============================================================================
// Union type for all artifacts
// =============================================================================

export type ArtifactData =
  | GlossaryArtifact
  | EventStormingArtifact
  | BoundedContextsArtifact
  | AggregatesArtifact
  | ArchitectureArtifact;
