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
                        The Architecture phase translates your domain model into software implementation patterns, focusing on Hexagonal mapping.
                    </p>
                    <div className="flex flex-col gap-4 mt-2">
                        <div className="bg-muted/30 p-4 rounded-md border space-y-3">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Visualization Explanation
                            </h3>
                            <ul className="space-y-2 text-sm text-muted-foreground list-disc pl-4 marker:text-muted-foreground/50">
                                <li><strong className="text-foreground">Hexagonal Layers:</strong> Concentric maps showing layer isolation: Domain (inner core) ← Application ← Infrastructure & Presentation.</li>
                                <li><strong className="text-foreground">Layer Elements:</strong> Software artifacts mapped to proper layers.</li>
                                <li><strong className="text-foreground">Anti-Corruption Layers (ACL):</strong> Explicit translation boundaries separating pure internal models from messy external systems.</li>
                                <li><strong className="text-foreground">Published Interfaces:</strong> Specifications of how APIs are exposed to consumers.</li>
                                <li><strong className="text-foreground">Technical Patterns:</strong> Implementation strategies applied to specific parts of the system.</li>
                            </ul>
                        </div>
                        <div className="bg-muted/30 p-4 rounded-md border space-y-3">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                Usage Guide
                            </h3>
                            <ul className="space-y-2 text-sm text-muted-foreground list-disc pl-4 marker:text-muted-foreground/50">
                                <li><strong className="text-foreground">Verify Domain Purity:</strong> Inspect the Domain and Application layers which should not contain infrastructure elements.</li>
                                <li><strong className="text-foreground">Check ACL Implementation:</strong> Review the Anti-Corruption Layers to ensure complex data translations are properly isolated rather than leaking into the core model.</li>
                                <li><strong className="text-foreground">Assess Pattern Fit:</strong> Review the Justification column in Technical Patterns to ensure complex patterns are only used where necessary.</li>
                            </ul>
                        </div>
                    </div>
                </div>
            }
        />
    );
}
