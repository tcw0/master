"use client";
import { useParams } from "next/navigation";
import { PhasePageTemplate } from "@/components/phases/PhasePageTemplate";

export default function Phase2Page() {
    const params = useParams<{ id: string }>();
    if (!params?.id) return null;

    return (
        <PhasePageTemplate
            sessionId={params.id}
            phaseNum={2}
            title="Event Storming"
            description={
                <>
                    Event Storming discovers the behavioral processes of the domain. It maps what happens as a 
                    sequence of actors, commands, aggregates, events, and policies. Trace the flows from left to right 
                    to understand how business rules trigger automated reactions.
                </>
            }
        />
    );
}
