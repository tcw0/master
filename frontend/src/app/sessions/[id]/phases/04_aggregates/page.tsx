"use client";
import { useParams } from "next/navigation";
import { PhasePageTemplate } from "@/components/phases/PhasePageTemplate";

export default function Phase4Page() {
    const params = useParams<{ id: string }>();
    if (!params?.id) return null;

    return (
        <PhasePageTemplate
            sessionId={params.id}
            phaseNum={4}
            title="Aggregates"
            description={
                <>
                    Aggregates define transactional consistency boundaries — the smallest unit within which business rules 
                    (invariants) are guaranteed to hold. Review the size evaluations; large aggregates create contention 
                    and should often be split.
                </>
            }
        />
    );
}
