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
                <div className="space-y-4">
                    <p>
                        The Architecture phase translates your domain model into software implementation patterns, focusing on Hexagonal (Ports & Adapters) mapping.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                        <div className="bg-muted/30 p-4 rounded-md border space-y-2">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Visualization Explanation
                            </h3>
                            <p className="text-sm text-muted-foreground">A concentric layer map representing isolation (Domain ← Application ← Infrastructure), as well as details on Anti-Corruption Layers, APIs, and specific technical pattern implementations.</p>
                        </div>
                        <div className="bg-muted/30 p-4 rounded-md border space-y-2">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Usage Guide
                            </h3>
                            <p className="text-sm text-muted-foreground">The Domain and Application layers should contain NO infrastructure elements. Use the <strong className="text-foreground flex items-center gap-1 inline-flex"><div className="w-3 h-3 bg-indigo-500 rounded-sm"></div> Domain</strong> map as the core to test independently. Additionally, review the <strong className="text-foreground">Anti-Corruption Layers</strong> section to ensure complex translations from legacy/external systems are properly wrapped rather than leaking into the core model.</p>
                        </div>
                    </div>
                </div>
            }
        />
    );
}
