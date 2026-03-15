"use client";
import { useParams } from "next/navigation";
import { PhasePageTemplate } from "@/components/phases/PhasePageTemplate";

export default function Phase1Page() {
    const params = useParams<{ id: string }>();
    // Make sure we have the ID before rendering
    if (!params?.id) return null;

    return (
        <PhasePageTemplate
            sessionId={params.id}
            phaseNum={1}
            title="Glossary (Ubiquitous Language)"
            description={
                <>
                    The Ubiquitous Language is the foundation of Domain-Driven Design. It establishes a shared vocabulary 
                    between the development team and domain experts. Ensure all ambiguous terms are clarified before proceeding, 
                    as every subsequent phase builds on these definitions.
                </>
            }
        />
    );
}
