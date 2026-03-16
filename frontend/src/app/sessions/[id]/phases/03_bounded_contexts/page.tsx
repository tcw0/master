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
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                        <div className="bg-muted/30 p-4 rounded-md border space-y-2">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Visualization Explanation
                            </h3>
                            <p className="text-sm text-muted-foreground">A visual map of independent contexts and their integration patterns (e.g. Shared Kernel, Anti-Corruption Layer). The Details tab expands on their internal aggregates and terms.</p>
                        </div>
                        <div className="bg-muted/30 p-4 rounded-md border space-y-2">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Usage Guide
                            </h3>
                            <p className="text-sm text-muted-foreground">Look for coupling bottlenecks on the Context Map. An upstream context supplying many downstream contexts is a critical point of failure. Check the <strong className="text-foreground">Term Overlaps</strong> section for the same terms meaning two different things across contexts.</p>
                        </div>
                    </div>
                </div>
            }
        />
    );
}
