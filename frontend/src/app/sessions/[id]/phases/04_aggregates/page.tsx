"use client";
import { useParams } from "next/navigation";
import { PhasePageTemplate } from "@/components/phases/PhasePageTemplate";

export default function Phase4Page() {
    const params = useParams<{ id: string }>();
    if (!params?.id) return null;

    return (
        <PhasePageTemplate
            sessionId={params.id}
            phaseNum={4}
            title="Aggregates"
            description={
                <div className="space-y-4">
                    <p>
                        Aggregates define transactional consistency boundaries — the smallest unit within which business rules 
                        (invariants) are guaranteed to hold synchronously.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                        <div className="bg-muted/30 p-4 rounded-md border space-y-2">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Visualization Explanation
                            </h3>
                            <p className="text-sm text-muted-foreground">A breakdown of root entities and their child components grouped by bounded context. It specifies their invariants, properties, and explicit transaction sizing.</p>
                        </div>
                        <div className="bg-muted/30 p-4 rounded-md border space-y-2">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Usage Guide
                            </h3>
                            <p className="text-sm text-muted-foreground">Focus on the <strong className="text-amber-500 font-medium">Evaluation</strong> badges. An aggregate marked as <em>large</em> or <em>monolithic</em> is a red flag for database contention and sluggish writes. Review its child entities where necessary.</p>
                        </div>
                    </div>
                </div>
            }
        />
        );
}
