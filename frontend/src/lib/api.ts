/**
 * API client for the DDD Pipeline backend.
 *
 * Typed functions wrapping fetch calls to the FastAPI endpoints.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// =============================================================================
// Types
// =============================================================================

export interface PhaseStatus {
    phase_id: string;
    phase_name: string;
    phase_number: number;
    status: string;
    has_artifact: boolean;
    has_validation: boolean;
    version: number | null;
    source: string | null;
}

export interface Session {
    id: string;
    requirements_text: string;
    requirements_name: string;
    provider: string;
    model: string;
    temperature: number;
    phases: PhaseStatus[];
    created_at: string;
    updated_at: string;
}

export interface CreateSessionRequest {
    requirements_text: string;
    requirements_name: string;
    provider: string;
    model: string;
    temperature: number;
}

export interface RefinePhaseRequest {
    instructions: string;
    max_retries?: number;
}

export interface RunPhaseResponse {
    phase_id: string;
    phase_name: string;
    status: string;
    version: number;
    source: string;
    artifact: Record<string, unknown> | null;
    validation: Record<string, unknown> | null;
    error: string | null;
}

export interface ArtifactResponse {
    phase_id: string;
    phase_name: string;
    version: number;
    source: string;
    artifact: Record<string, unknown>;
}

export interface ArtifactVersionSummary {
    version: number;
    source: string;
    status: string;
    created_at: string;
}

export interface ArtifactHistoryResponse {
    phase_id: string;
    phase_name: string;
    versions: ArtifactVersionSummary[];
}

// =============================================================================
// Helper
// =============================================================================

async function apiFetch<T>(
    path: string,
    options?: RequestInit,
): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(body.detail || `API error: ${res.status}`);
    }
    if (res.status === 204) return undefined as T;
    return res.json();
}

// =============================================================================
// Sessions
// =============================================================================

export async function createSession(
    req: CreateSessionRequest,
): Promise<Session> {
    return apiFetch<Session>("/sessions", {
        method: "POST",
        body: JSON.stringify(req),
    });
}

export async function listSessions(): Promise<{
    sessions: Session[];
    count: number;
}> {
    return apiFetch("/sessions");
}

export async function getSession(id: string): Promise<Session> {
    return apiFetch<Session>(`/sessions/${id}`);
}

export async function deleteSession(id: string): Promise<void> {
    return apiFetch(`/sessions/${id}`, { method: "DELETE" });
}

// =============================================================================
// Phases
// =============================================================================

export async function runPhase(
    sessionId: string,
    phaseId: string,
    maxRetries = 2,
): Promise<RunPhaseResponse> {
    return apiFetch<RunPhaseResponse>(
        `/sessions/${sessionId}/phases/${phaseId}/run`,
        {
            method: "POST",
            body: JSON.stringify({ max_retries: maxRetries }),
        },
    );
}

export async function refinePhase(
    sessionId: string,
    phaseId: string,
    req: RefinePhaseRequest,
): Promise<RunPhaseResponse> {
    return apiFetch<RunPhaseResponse>(
        `/sessions/${sessionId}/phases/${phaseId}/refine`,
        {
            method: "POST",
            body: JSON.stringify({
                instructions: req.instructions,
                max_retries: req.max_retries ?? 2,
            }),
        },
    );
}

export async function getArtifact(
    sessionId: string,
    phaseId: string,
): Promise<ArtifactResponse> {
    return apiFetch<ArtifactResponse>(
        `/sessions/${sessionId}/phases/${phaseId}/artifact`,
    );
}

export async function getArtifactHistory(
    sessionId: string,
    phaseId: string,
): Promise<ArtifactHistoryResponse> {
    return apiFetch<ArtifactHistoryResponse>(
        `/sessions/${sessionId}/phases/${phaseId}/history`,
    );
}
