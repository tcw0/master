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
                <>
                    Bounded Contexts are the strategic core of DDD, defining where one domain model ends and another begins. 
                    The Context Map documents how these independent boundaries interact. Pay special attention to 
                    <span className="font-medium text-foreground mx-1">Term Overlaps</span>, as they prove boundaries are correct.
                </>
            }
        />
    );
}
