"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Code, LayoutDashboard } from "lucide-react";

import { JsonFallback } from "./JsonFallback";
import { GlossaryViewer } from "./GlossaryViewer";
import { EventStormingViewer } from "./EventStormingViewer";
import { BoundedContextsViewer } from "./BoundedContextsViewer";
import { AggregatesViewer } from "./AggregatesViewer";
import { ArchitectureViewer } from "./ArchitectureViewer";

import type {
  GlossaryArtifact,
  EventStormingArtifact,
  BoundedContextsArtifact,
  AggregatesArtifact,
  ArchitectureArtifact,
} from "@/lib/types";

/**
 * Routes `phase_id` to the correct visualization component.
 * Includes a toggle to switch between visual and raw JSON views.
 */
export function ArtifactViewer({
  phaseId,
  artifact,
}: {
  phaseId: string;
  artifact: Record<string, unknown>;
}) {
  const [showJson, setShowJson] = useState(false);

  function renderViewer() {
    switch (phaseId) {
      case "01_glossary":
        return <GlossaryViewer data={artifact as unknown as GlossaryArtifact} />;
      case "02_event_storming":
        return <EventStormingViewer data={artifact as unknown as EventStormingArtifact} />;
      case "03_bounded_contexts":
        return <BoundedContextsViewer data={artifact as unknown as BoundedContextsArtifact} />;
      case "04_aggregates":
        return <AggregatesViewer data={artifact as unknown as AggregatesArtifact} />;
      case "05_architecture":
        return <ArchitectureViewer data={artifact as unknown as ArchitectureArtifact} />;
      default:
        return <JsonFallback data={artifact} />;
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex justify-end">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowJson(!showJson)}
          className="gap-1.5 text-xs text-muted-foreground"
        >
          {showJson ? (
            <>
              <LayoutDashboard className="h-3.5 w-3.5" />
              Visual View
            </>
          ) : (
            <>
              <Code className="h-3.5 w-3.5" />
              View JSON
            </>
          )}
        </Button>
      </div>
      {showJson ? <JsonFallback data={artifact} /> : renderViewer()}
    </div>
  );
}
