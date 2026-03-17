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
                    <div className="flex flex-col gap-4 mt-2">
                        <div className="bg-muted/30 p-4 rounded-md border space-y-3">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Visualization Explanation
                            </h3>
                            <ul className="space-y-2 text-sm text-muted-foreground list-disc pl-4 marker:text-muted-foreground/50">
                                <li><strong className="text-foreground">Category Badges:</strong> Identifies the DDD classification of a term (Entity, Value Object, Command, Event, Rule/Policy, Role, State).</li>
                                <li><strong className="text-foreground">Definitions:</strong> Provides the agreed-upon business meaning of the term within the domain.</li>
                                <li><strong className="text-foreground">Related Terms:</strong> Shows immediate relationships to other glossary entries, hinting at future aggregate combinations.</li>
                                <li><strong className="text-foreground">Ambiguity Warnings:</strong> Highlights terms marked with a warning triangle that require further clarification from domain experts.</li>
                                <li><strong className="text-foreground">Bounded Context Hints:</strong> An expandable section at the bottom suggesting early boundary groupings based on term cohesion.</li>
                            </ul>
                        </div>
                        <div className="bg-muted/30 p-4 rounded-md border space-y-3">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Usage Guide
                            </h3>
                            <ul className="space-y-2 text-sm text-muted-foreground list-disc pl-4 marker:text-muted-foreground/50">
                                <li><strong className="text-foreground">Check Definitions:</strong> Review the definitions of each term to ensure they are clear and concise.</li>
                                <li><strong className="text-foreground">Resolve Ambiguities:</strong> Look for <span className="text-amber-500 font-medium">ambiguity indicators</span> first. These represent conceptual gaps that must be resolved with stakeholders before proceeding.</li>
                                <li><strong className="text-foreground">Identify Boundaries:</strong> Review the Bounded Context Hints to preview how the language might split into independent software modules.</li>
                            </ul>
                        </div>
                    </div>
                </div>
            }
        />
    );
}
