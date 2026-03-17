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
                        Aggregates define transactional consistency boundaries. The smallest unit within which business rules 
                        (invariants) are guaranteed to hold synchronously.
                    </p>
                    <div className="flex flex-col gap-4 mt-2">
                        <div className="bg-muted/30 p-4 rounded-md border space-y-3">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Visualization Explanation
                            </h3>
                            <ul className="space-y-2 text-sm text-muted-foreground list-disc pl-4 marker:text-muted-foreground/50">
                                <li><strong className="text-foreground">Aggregate Cards:</strong> Grouped by context, each card represents a transactional boundary encompassing a root entity and its children.</li>
                                <li><strong className="text-foreground">Evaluation Badges:</strong> Visual indicators ranking aggregate size and complexity.</li>
                                <li><strong className="text-foreground">Elements:</strong> The internal structural breakdown showing the Root Entity and attached Value Objects.</li>
                                <li><strong className="text-foreground">Invariants:</strong> The strict business rules that must be satisfied before this aggregate can be persisted to the database.</li>
                                <li><strong className="text-foreground">Commands & Events:</strong> The specific actions this aggregate can accept, and the resulting events it emits upon success.</li>
                            </ul>
                        </div>
                        <div className="bg-muted/30 p-4 rounded-md border space-y-3">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Usage Guide
                            </h3>
                            <ul className="space-y-2 text-sm text-muted-foreground list-disc pl-4 marker:text-muted-foreground/50">
                                <li><strong className="text-foreground">Prevent Contention:</strong> Be aware of aggregates marked as <em>large</em> and <em>monolithic</em>.</li>
                                <li><strong className="text-foreground">Review Design Decisions:</strong> Read the architectural reasoning at the page bottom to understand why specific boundaries were chosen.</li>
                            </ul>
                        </div>
                    </div>
                </div>
            }
        />
        );
}
