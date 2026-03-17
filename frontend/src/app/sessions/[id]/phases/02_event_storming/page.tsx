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
                    <div className="flex flex-col gap-4 mt-2">
                        <div className="bg-muted/30 p-4 rounded-md border space-y-3">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Visualization Explanation
                            </h3>
                            <ul className="space-y-2 text-sm text-muted-foreground list-disc pl-4 marker:text-muted-foreground/50">
                                <li><strong className="text-foreground">Process Flowcharts:</strong> Visual maps of business processes reading from left to right.</li>
                                <li><strong className="text-foreground">Components:</strong> Actors (users/systems), Commands (intentions/actions), Aggregates (data/rules), Events (facts/results), and Policies (automated reactions).</li>
                                <li><strong className="text-foreground">Solid Arrows (→):</strong> Indicate direct causal flow within a single step (e.g., Command hitting an Aggregate).</li>
                                <li><strong className="text-foreground">Dashed Arrows (- - →):</strong> Indicate asynchronous triggers connecting one event to the start of the next process step.</li>
                                <li><strong className="text-foreground">Reference Tables:</strong> Exhaustive lists of all unique elements discovered across all flows.</li>
                            </ul>
                        </div>
                        <div className="bg-muted/30 p-4 rounded-md border space-y-3">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Usage Guide
                            </h3>
                            <ul className="space-y-2 text-sm text-muted-foreground list-disc pl-4 marker:text-muted-foreground/50">
                                <li><strong className="text-foreground">Verify Story Logic:</strong> Follow the flowchart arrows to ensure each story makes logical sense from actor intention to system consequence.</li>
                                <li><strong className="text-foreground">Check Completeness:</strong> Confirm that the reference lists have no missing entries compared to the flows.</li>
                            </ul>
                        </div>
                    </div>
                </div>
            }
        />
    );
}
