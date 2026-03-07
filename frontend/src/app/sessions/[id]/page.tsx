"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

import {
    getSession,
    runPhase,
    getArtifact,
    type Session,
    type PhaseStatus,
    type ArtifactResponse,
} from "@/lib/api";

// =============================================================================
// Status helpers
// =============================================================================

function statusBadge(status: string) {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
        completed: "default",
        running: "secondary",
        failed: "destructive",
        pending: "outline",
    };
    return (
        <Badge variant={variants[status] || "outline"} className="capitalize">
            {status}
        </Badge>
    );
}

function sourceBadge(source: string | null, version: number | null) {
    if (!source || !version) return null;
    return (
        <span className="text-xs text-muted-foreground">
            v{version} · {source}
        </span>
    );
}

// =============================================================================
// Phase Card
// =============================================================================

function PhaseCard({
    phase,
    sessionId,
    isRunnable,
    onPhaseComplete,
}: {
    phase: PhaseStatus;
    sessionId: string;
    isRunnable: boolean;
    onPhaseComplete: () => void;
}) {
    const [running, setRunning] = useState(false);
    const [expanded, setExpanded] = useState(false);
    const [artifact, setArtifact] = useState<ArtifactResponse | null>(null);
    const [loadingArtifact, setLoadingArtifact] = useState(false);

    const loadArtifact = useCallback(async () => {
        if (!phase.has_artifact) return;
        setLoadingArtifact(true);
        try {
            const data = await getArtifact(sessionId, phase.phase_id);
            setArtifact(data);
        } catch {
            toast.error("Failed to load artifact");
        } finally {
            setLoadingArtifact(false);
        }
    }, [sessionId, phase.phase_id, phase.has_artifact]);

    async function handleRun() {
        setRunning(true);
        try {
            const result = await runPhase(sessionId, phase.phase_id);
            if (result.status === "completed") {
                toast.success(`${phase.phase_name} completed`);
                setArtifact({
                    phase_id: result.phase_id,
                    phase_name: result.phase_name,
                    version: result.version,
                    source: result.source,
                    artifact: result.artifact!,
                });
                setExpanded(true);
            } else {
                toast.error(`${phase.phase_name} failed: ${result.error}`);
            }
            onPhaseComplete();
        } catch (e) {
            toast.error(e instanceof Error ? e.message : "Phase execution failed");
        } finally {
            setRunning(false);
        }
    }

    function handleToggle() {
        if (!expanded && phase.has_artifact && !artifact) {
            loadArtifact();
        }
        setExpanded(!expanded);
    }

    return (
        <Card
            className={
                phase.status === "completed"
                    ? "border-green-800/40"
                    : phase.status === "failed"
                        ? "border-red-800/40"
                        : ""
            }
        >
            <CardHeader
                className="cursor-pointer"
                onClick={handleToggle}
            >
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <span className="flex h-7 w-7 items-center justify-center rounded-full bg-muted text-sm font-medium">
                            {phase.phase_number}
                        </span>
                        <div>
                            <CardTitle className="text-base">{phase.phase_name}</CardTitle>
                            <div className="flex items-center gap-2 mt-1">
                                {statusBadge(phase.status)}
                                {sourceBadge(phase.source, phase.version)}
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        {isRunnable && phase.status !== "running" && (
                            <Button
                                size="sm"
                                variant={phase.status === "completed" ? "outline" : "default"}
                                disabled={running}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleRun();
                                }}
                            >
                                {running
                                    ? "Running..."
                                    : phase.status === "completed"
                                        ? "Re-run"
                                        : "Run"}
                            </Button>
                        )}
                        {phase.has_artifact && (
                            <span className="text-xs text-muted-foreground">
                                {expanded ? "▲" : "▼"}
                            </span>
                        )}
                    </div>
                </div>
            </CardHeader>

            {expanded && (
                <CardContent>
                    <Separator className="mb-4" />
                    {loadingArtifact ? (
                        <p className="text-sm text-muted-foreground">Loading artifact...</p>
                    ) : artifact ? (
                        <div className="space-y-2">
                            <div className="flex items-center justify-between">
                                <p className="text-sm text-muted-foreground">
                                    Artifact v{artifact.version} · {artifact.source}
                                </p>
                            </div>
                            <ScrollArea className="h-[400px] rounded-md border bg-muted/30 p-4">
                                <pre className="text-xs font-mono whitespace-pre-wrap break-words">
                                    {JSON.stringify(artifact.artifact, null, 2)}
                                </pre>
                            </ScrollArea>
                        </div>
                    ) : phase.status === "failed" ? (
                        <p className="text-sm text-destructive">Phase failed. Click Run to retry.</p>
                    ) : (
                        <p className="text-sm text-muted-foreground">
                            No artifact yet. Run this phase to generate one.
                        </p>
                    )}
                </CardContent>
            )}
        </Card>
    );
}

// =============================================================================
// Session Page
// =============================================================================

export default function SessionPage() {
    const params = useParams<{ id: string }>();
    const [session, setSession] = useState<Session | null>(null);
    const [loading, setLoading] = useState(true);

    const loadSession = useCallback(async () => {
        try {
            const data = await getSession(params.id);
            setSession(data);
        } catch {
            toast.error("Failed to load session");
        } finally {
            setLoading(false);
        }
    }, [params.id]);

    useEffect(() => {
        loadSession();
    }, [loadSession]);

    if (loading) {
        return <p className="text-muted-foreground">Loading session...</p>;
    }

    if (!session) {
        return <p className="text-destructive">Session not found.</p>;
    }

    // A phase is runnable if all its prerequisites are met
    function isPhaseRunnable(phase: PhaseStatus): boolean {
        if (!session) return false;
        // Phase 1 is always runnable
        if (phase.phase_number === 1) return true;
        // All previous phases must be completed
        for (const p of session.phases) {
            if (p.phase_number < phase.phase_number && p.status !== "completed") {
                return false;
            }
        }
        return true;
    }

    const completed = session.phases.filter((p) => p.status === "completed").length;

    return (
        <div className="space-y-6">
            {/* Session Header */}
            <div>
                <div className="flex items-center gap-3">
                    <a href="/" className="text-muted-foreground hover:text-foreground text-sm">
                        ← Sessions
                    </a>
                </div>
                <h1 className="mt-2 text-2xl font-bold">{session.requirements_name}</h1>
                <p className="text-sm text-muted-foreground">
                    {session.provider}/{session.model} · T={session.temperature} ·{" "}
                    {completed}/5 phases complete ·{" "}
                    <span className="font-mono">{session.id}</span>
                </p>
            </div>

            <Separator />

            {/* Pipeline Phases */}
            <div className="space-y-3">
                {session.phases.map((phase) => (
                    <PhaseCard
                        key={phase.phase_id}
                        phase={phase}
                        sessionId={session.id}
                        isRunnable={isPhaseRunnable(phase)}
                        onPhaseComplete={loadSession}
                    />
                ))}
            </div>
        </div>
    );
}
