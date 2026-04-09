"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Code, LayoutDashboard, Download } from "lucide-react";

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
  sessionId,
  phaseNum,
}: {
  phaseId: string;
  artifact: Record<string, unknown>;
  sessionId: string;
  phaseNum: number;
}) {
  const [showJson, setShowJson] = useState(false);

  const handleDownloadJson = () => {
    const jsonStr = JSON.stringify(artifact, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `session_${sessionId}_phase_${phaseNum}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

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
      <div className="flex justify-end gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleDownloadJson}
          className="gap-1.5 text-xs text-muted-foreground"
        >
          <Download className="h-3.5 w-3.5" />
          Download JSON
        </Button>
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
