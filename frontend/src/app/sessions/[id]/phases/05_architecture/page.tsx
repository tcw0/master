"use client";
import { useParams } from "next/navigation";
import { PhasePageTemplate } from "@/components/phases/PhasePageTemplate";

export default function Phase5Page() {
    const params = useParams<{ id: string }>();
    if (!params?.id) return null;

    return (
        <PhasePageTemplate
            sessionId={params.id}
            phaseNum={5}
            title="Architecture"
            description={
                <>
                    The Architecture phase maps the domain model into Hexagonal (Ports & Adapters) architecture. 
                    It ensures the inner domain layer remains pure and isolated from the outer infrastructure and presentation 
                    concerns. Verify that Anti-Corruption Layers protect your core contexts.
                </>
            }
        />
    );
}
