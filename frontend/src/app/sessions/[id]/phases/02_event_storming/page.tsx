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
                <div className="space-y-4">
                    <p>
                        Event Storming discovers the behavioral processes of the domain. It bridges the static glossary 
                        with the dynamic processes of the business.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                        <div className="bg-muted/30 p-4 rounded-md border space-y-2">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Visualization Explanation
                            </h3>
                            <p className="text-sm text-muted-foreground">Flowcharts representing business processes (left to right) and reference tables listing all unique commands, events, and policies. Solid arrows show the causal flow within a step: Actor → Command → Aggregate → Event → Policy. Dashed arrows connect steps, showing how one event triggers the next step in the process.</p>
                        </div>
                        <div className="bg-muted/30 p-4 rounded-md border space-y-2">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Usage Guide
                            </h3>
                            <p className="text-sm text-muted-foreground">Follow the flowchart arrows to ensure each story makes logical sense from actor intention to system reaction. Confirm that the reference lists have no missing entries compared to the flows.</p>
                        </div>
                    </div>
                </div>
            }
        />
    );
}
