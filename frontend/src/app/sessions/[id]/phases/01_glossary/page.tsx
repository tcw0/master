"use client";
import { useParams } from "next/navigation";
import { PhasePageTemplate } from "@/components/phases/PhasePageTemplate";

export default function Phase1Page() {
    const params = useParams<{ id: string }>();
    if (!params?.id) return null;

    return (
        <PhasePageTemplate
            sessionId={params.id}
            phaseNum={1}
            title="Glossary (Ubiquitous Language)"
            description={
                <div className="space-y-4">
                    <p>
                        The Ubiquitous Language is the foundation of Domain-Driven Design. It establishes a shared vocabulary 
                        between the development team and domain experts.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                        <div className="bg-muted/30 p-4 rounded-md border space-y-2">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Visualization Explanation
                            </h3>
                            <p className="text-sm text-muted-foreground">A filterable table of all domain terms categorized by their DDD classification (Entity, Value Object, Command, Event, etc.). It displays definitions, related terms, and potential early boundaries.</p>
                        </div>
                        <div className="bg-muted/30 p-4 rounded-md border space-y-2">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Usage Guide
                            </h3>
                            <p className="text-sm text-muted-foreground">Look for <span className="text-amber-500 font-medium">ambiguity indicators</span> which represent conceptual gaps that must be resolved with stakeholders before proceeding.</p>
                        </div>
                    </div>
                </div>
            }
        />
    );
}
