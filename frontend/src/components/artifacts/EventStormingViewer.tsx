"use client";

import { useMemo } from "react";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertTriangle } from "lucide-react";
import { MermaidDiagram } from "./MermaidDiagram";
import type { EventStormingArtifact, EventFlow } from "@/lib/types";

// ---------------------------------------------------------------------------
// Mermaid generation helpers
// ---------------------------------------------------------------------------

/** Sanitize a label for Mermaid (escape quotes, brackets) */
function sanitize(label: string): string {
  return label.replace(/"/g, "#quot;").replace(/[[\](){}]/g, " ");
}

/** Generate a Mermaid graph LR definition for one EventFlow */
function flowToMermaid(flow: EventFlow): string {
  const lines: string[] = [
    "graph LR",
    "  classDef actor fill:#fbbf24,stroke:#92400e,color:#1c1917",
    "  classDef command fill:#3b82f6,stroke:#1e40af,color:#fff",
    "  classDef aggregate fill:#f59e0b,stroke:#92400e,color:#1c1917",
    "  classDef event fill:#f97316,stroke:#9a3412,color:#fff",
    "  classDef policy fill:#a855f7,stroke:#6b21a8,color:#fff",
  ];

  flow.steps.forEach((step, i) => {
    const prefix = `s${i}`;
    const actorId = `${prefix}_actor`;
    const cmdId = `${prefix}_cmd`;
    const aggId = `${prefix}_agg`;
    const evtId = `${prefix}_evt`;

    lines.push(`  ${actorId}["👤 ${sanitize(step.actor)}"]:::actor`);
    lines.push(`  ${cmdId}["${sanitize(step.command)}"]:::command`);
    lines.push(`  ${aggId}["${sanitize(step.aggregate)}"]:::aggregate`);
    lines.push(`  ${evtId}["${sanitize(step.event)}"]:::event`);

    lines.push(`  ${actorId} --> ${cmdId}`);
    lines.push(`  ${cmdId} --> ${aggId}`);
    lines.push(`  ${aggId} --> ${evtId}`);

    if (step.policy) {
      const polId = `${prefix}_pol`;
      lines.push(`  ${polId}["⚡ ${sanitize(step.policy)}"]:::policy`);
      lines.push(`  ${evtId} --> ${polId}`);

      if (step.next_command) {
        const nextCmdId = `${prefix}_next`;
        lines.push(`  ${nextCmdId}["${sanitize(step.next_command)}"]:::command`);
        lines.push(`  ${polId} --> ${nextCmdId}`);
      }
    }

    // Connect to next step
    if (i < flow.steps.length - 1) {
      const nextPrefix = `s${i + 1}`;
      if (step.policy && step.next_command) {
        lines.push(`  ${prefix}_next -.-> ${nextPrefix}_actor`);
      } else if (step.policy) {
        lines.push(`  ${prefix}_pol -.-> ${nextPrefix}_actor`);
      } else {
        lines.push(`  ${evtId} -.-> ${nextPrefix}_actor`);
      }
    }
  });

  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function EventStormingViewer({ data }: { data: EventStormingArtifact }) {
  const flowDiagrams = useMemo(
    () => data.flows.map((flow) => ({ flow, mermaid: flowToMermaid(flow) })),
    [data.flows],
  );

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
        <span>{data.commands.length} commands</span>
        <span>{data.domain_events.length} events</span>
        <span>{data.policies.length} policies</span>
        <span>{data.flows.length} flows</span>
      </div>

      {/* Ambiguities */}
      {data.ambiguities && data.ambiguities.length > 0 && (
        <div className="space-y-2 pb-2">
          <h4 className="text-sm font-semibold flex items-center gap-1.5">
            <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
            Ambiguities ({data.ambiguities.length})
          </h4>
          <div className="space-y-1">
            {data.ambiguities.map((a, i) => (
              <p key={i} className="text-xs text-muted-foreground pl-5">• {a}</p>
            ))}
          </div>
        </div>
      )}

      <Tabs defaultValue="flows">
        <TabsList>
          <TabsTrigger value="flows">Flows</TabsTrigger>
          <TabsTrigger value="reference">Reference Lists</TabsTrigger>
        </TabsList>

        {/* Flows tab — Mermaid diagrams */}
        <TabsContent value="flows" className="space-y-6 mt-4">
          
          {/* Legend */}
          <div className="flex flex-wrap gap-2 p-3 bg-muted/30 rounded-md border text-xs">
            <span className="font-semibold mr-2 flex items-center">Legend:</span>
            <span className="flex items-center gap-1"><div className="w-3 h-3 bg-yellow-500 rounded-sm border border-yellow-700"></div> Actor</span>
            <span className="flex items-center gap-1"><div className="w-3 h-3 bg-blue-500 rounded-sm border border-blue-700"></div> Command</span>
            <span className="flex items-center gap-1"><div className="w-3 h-3 bg-amber-500 rounded-sm border border-amber-700"></div> Aggregate</span>
            <span className="flex items-center gap-1"><div className="w-3 h-3 bg-orange-500 rounded-sm border border-orange-700"></div> Domain Event</span>
            <span className="flex items-center gap-1"><div className="w-3 h-3 bg-purple-500 rounded-sm border border-purple-700"></div> Policy</span>
            <span className="flex items-center gap-1 ml-2 text-muted-foreground">- - -{">"} triggers</span>
          </div>

          {flowDiagrams.map(({ flow, mermaid }) => (
            <div key={flow.name} className="space-y-2">
              <div>
                <h4 className="text-sm font-semibold">{flow.name}</h4>
                <p className="text-xs text-muted-foreground">{flow.description}</p>
              </div>
              <div className="border rounded-md p-4 bg-background">
                <MermaidDiagram definition={mermaid} />
              </div>
            </div>
          ))}
          {flowDiagrams.length === 0 && (
            <p className="text-sm text-muted-foreground py-4">No flows defined.</p>
          )}
        </TabsContent>

        {/* Reference Lists tab — Tables */}
        <TabsContent value="reference" className="space-y-6 mt-4">
          {/* Commands */}
          <div>
            <h4 className="text-sm font-semibold mb-2">Commands ({data.commands.length})</h4>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Actor</TableHead>
                    <TableHead>Target Aggregate</TableHead>
                    <TableHead>Description</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.commands.map((cmd) => (
                    <TableRow key={cmd.name}>
                      <TableCell className="font-medium">{cmd.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-xs bg-yellow-500/15 text-yellow-400 border-yellow-500/30">{cmd.actor}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-xs bg-amber-500/15 text-amber-400 border-amber-500/30">{cmd.target_aggregate}</Badge>
                      </TableCell>
                      <TableCell className="text-sm">{cmd.description}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>

          {/* Domain Events */}
          <div>
            <h4 className="text-sm font-semibold mb-2">Domain Events ({data.domain_events.length})</h4>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Triggered By</TableHead>
                    <TableHead>Aggregate</TableHead>
                    <TableHead>Description</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.domain_events.map((evt) => (
                    <TableRow key={evt.name}>
                      <TableCell className="font-medium">{evt.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-xs bg-blue-500/15 text-blue-400 border-blue-500/30">{evt.triggered_by_command}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-xs bg-amber-500/15 text-amber-400 border-amber-500/30">{evt.aggregate}</Badge>
                      </TableCell>
                      <TableCell className="text-sm">{evt.description}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>

          {/* Policies */}
          <div>
            <h4 className="text-sm font-semibold mb-2">Policies ({data.policies.length})</h4>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Triggered By Event</TableHead>
                    <TableHead>Resulting Command</TableHead>
                    <TableHead>Description</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.policies.map((pol) => (
                    <TableRow key={pol.name}>
                      <TableCell className="font-medium">{pol.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-xs bg-orange-500/15 text-orange-400 border-orange-500/30">{pol.triggered_by_event}</Badge>
                      </TableCell>
                      <TableCell>
                        {pol.resulting_command ? (
                          <Badge variant="outline" className="text-xs bg-blue-500/15 text-blue-400 border-blue-500/30">{pol.resulting_command}</Badge>
                        ) : (
                          <span className="text-xs text-muted-foreground">—</span>
                        )}
                      </TableCell>
                      <TableCell className="text-sm">{pol.description}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
