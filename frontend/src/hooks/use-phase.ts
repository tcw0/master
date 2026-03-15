import { useState, useCallback, useEffect } from "react";
import { toast } from "sonner";
import {
    getSession,
    runPhase,
    getArtifact,
    type Session,
    type PhaseStatus,
    type ArtifactResponse,
} from "@/lib/api";

export function usePhase(sessionId: string, phaseNum: number) {
    const [session, setSession] = useState<Session | null>(null);
    const [phase, setPhase] = useState<PhaseStatus | null>(null);
    const [artifact, setArtifact] = useState<ArtifactResponse | null>(null);
    const [running, setRunning] = useState(false);
    const [loading, setLoading] = useState(true);

    const loadData = useCallback(async () => {
        setLoading(true);
        try {
            const sess = await getSession(sessionId);
            setSession(sess);
            
            const p = sess.phases.find(p => p.phase_number === phaseNum);
            if (p) {
                setPhase(p);
                if (p.has_artifact) {
                    const art = await getArtifact(sessionId, p.phase_id);
                    setArtifact(art);
                }
            }
        } catch (error) {
            toast.error("Failed to load phase data");
            console.error(error);
        } finally {
            setLoading(false);
        }
    }, [sessionId, phaseNum]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    const isRunnable = (() => {
        if (!session || !phase) return false;
        if (phase.phase_number === 1) return true;
        // All previous must be completed
        for (const p of session.phases) {
            if (p.phase_number < phase.phase_number && p.status !== "completed") {
                return false;
            }
        }
        return true;
    })();

    const handleRun = async () => {
        if (!phase) return;
        setRunning(true);
        try {
            const result = await runPhase(sessionId, phase.phase_id);
            if (result.status === "completed") {
                toast.success(`${phase.phase_name} completed`);
            } else {
                toast.error(`${phase.phase_name} failed: ${result.error}`);
            }
            // Reload everything to get the new artifact and status
            await loadData();
        } catch (e) {
            toast.error(e instanceof Error ? e.message : "Phase execution failed");
        } finally {
            setRunning(false);
        }
    };

    return {
        session,
        phase,
        artifact,
        loading,
        running,
        isRunnable,
        handleRun,
        refresh: loadData
    };
}
