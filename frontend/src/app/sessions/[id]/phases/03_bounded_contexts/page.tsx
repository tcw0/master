"use client";
import { useParams } from "next/navigation";
import { PhasePageTemplate } from "@/components/phases/PhasePageTemplate";

export default function Phase3Page() {
    const params = useParams<{ id: string }>();
    if (!params?.id) return null;

    return (
        <PhasePageTemplate
            sessionId={params.id}
            phaseNum={3}
            title="Bounded Contexts"
            description={
                <div className="space-y-4">
                    <p>
                        Bounded Contexts are the strategic core of DDD, defining where one domain model ends and another begins.
                    </p>
                    <div className="flex flex-col gap-4 mt-2">
                        <div className="bg-muted/30 p-4 rounded-md border space-y-3">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Visualization Explanation
                            </h3>
                            <ul className="space-y-2 text-sm text-muted-foreground list-disc pl-4 marker:text-muted-foreground/50">
                                <li><strong className="text-foreground">Context Map:</strong> A landscape diagram showing independent models (rectangles) and their relationships (arrows).</li>
                                <li><strong className="text-foreground">Domain Types:</strong> Contexts are colored by strategic importance.</li>
                                <li><strong className="text-foreground">Relationships Table:</strong> Explicit documentation of how data and control move between contexts.</li>
                                <li><strong className="text-foreground">Context Details:</strong> Cards detailing the primary responsibility and core aggregates within each boundary.</li>
                                <li><strong className="text-foreground">Term Overlaps:</strong> A critical view highlighting ubiquitous language terms that exist in multiple contexts.</li>
                            </ul>
                        </div>
                        <div className="bg-muted/30 p-4 rounded-md border space-y-3">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Usage Guide
                            </h3>
                            <ul className="space-y-2 text-sm text-muted-foreground list-disc pl-4 marker:text-muted-foreground/50">
                                <li><strong className="text-foreground">Find Coupling Bottlenecks:</strong> Look at the Context Map. An upstream context supplying many downstream contexts is a critical point of failure.</li>
                                <li><strong className="text-foreground">Enforce Linguistic Purity:</strong> Check the <strong className="text-foreground">Term Overlaps</strong> section. If the same term means two different things across contexts, ensure it is specifically defined in each.</li>
                            </ul>
                        </div>
                    </div>
                </div>
            }
        />
    );
}
