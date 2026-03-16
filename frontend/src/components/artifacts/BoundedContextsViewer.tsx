"use client";

import { useMemo } from "react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { MermaidDiagram } from "./MermaidDiagram";
import type { BoundedContextsArtifact } from "@/lib/types";

// ---------------------------------------------------------------------------
// Styling
// ---------------------------------------------------------------------------

const DOMAIN_TYPE_COLORS: Record<string, string> = {
  core: "bg-indigo-500/15 text-indigo-400 border-indigo-500/30",
  supporting: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  generic: "bg-gray-500/15 text-gray-400 border-gray-500/30",
};

const DOMAIN_TYPE_MERMAID: Record<string, string> = {
  core: "fill:#4338ca,stroke:#312e81,color:#e0e7ff",
  supporting: "fill:#b45309,stroke:#78350f,color:#fef3c7",
  generic: "fill:#4b5563,stroke:#1f2937,color:#f3f4f6",
};

const RELATIONSHIP_LABELS: Record<string, string> = {
  upstream_downstream: "Upstream / Downstream",
  shared_kernel: "Shared Kernel",
  customer_supplier: "Customer / Supplier",
  conformist: "Conformist",
  anti_corruption_layer: "Anti-Corruption Layer",
  published_language: "Published Language",
  open_host_service: "Open Host Service",
  partnership: "Partnership",
  separate_ways: "Separate Ways",
};

// ---------------------------------------------------------------------------
// Mermaid generation
// ---------------------------------------------------------------------------

function sanitize(label: string): string {
  return label.replace(/"/g, "#quot;").replace(/[[\](){}]/g, " ");
}

function contextMapToMermaid(data: BoundedContextsArtifact): string {
  const lines: string[] = ["graph LR"];

  // ClassDefs
  for (const [type, style] of Object.entries(DOMAIN_TYPE_MERMAID)) {
    lines.push(`  classDef ${type} ${style}`);
  }

  // Nodes
  const nodeIds = new Map<string, string>();
  data.bounded_contexts.forEach((ctx, i) => {
    const id = `ctx${i}`;
    nodeIds.set(ctx.name, id);
    const label = `${sanitize(ctx.name)}\\n(${ctx.domain_type})`;
    lines.push(`  ${id}["${label}"]:::${ctx.domain_type}`);
  });

  // Edges
  data.context_relationships.forEach((rel) => {
    const srcId = nodeIds.get(rel.source_context);
    const tgtId = nodeIds.get(rel.target_context);
    if (srcId && tgtId) {
      const label = sanitize(RELATIONSHIP_LABELS[rel.relationship_type] || rel.relationship_type);
      // Use different line styles based on relationship
      if (rel.relationship_type === "conformist" || rel.relationship_type === "separate_ways") {
        lines.push(`  ${srcId} -.-|"${label}"| ${tgtId}`);
      } else if (rel.relationship_type === "shared_kernel" || rel.relationship_type === "partnership") {
        lines.push(`  ${srcId} ===|"${label}"| ${tgtId}`);
      } else {
        lines.push(`  ${srcId} -->|"${label}"| ${tgtId}`);
      }
    }
  });

  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function BoundedContextsViewer({ data }: { data: BoundedContextsArtifact }) {
  const mermaidDef = useMemo(() => contextMapToMermaid(data), [data]);

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
        <span>{data.bounded_contexts.length} contexts</span>
        <span>{data.context_relationships.length} relationships</span>
        {data.term_overlaps.length > 0 && (
          <span>{data.term_overlaps.length} term overlaps</span>
        )}
      </div>

      <Tabs defaultValue="map">
        <TabsList>
          <TabsTrigger value="map">Context Map</TabsTrigger>
          <TabsTrigger value="details">Details</TabsTrigger>
        </TabsList>

        {/* Context Map — Mermaid */}
        <TabsContent value="map" className="mt-4 space-y-4">
          
          {/* Legend */}
          <div className="flex flex-wrap gap-4 p-3 bg-muted/30 rounded-md border text-xs">
            <span className="font-semibold flex items-center">Legend:</span>
            <div className="flex items-center gap-2 border-r pr-4">
              <span className="flex items-center gap-1"><div className="w-3 h-3 bg-indigo-500 rounded-sm border border-indigo-700"></div> Core</span>
              <span className="flex items-center gap-1"><div className="w-3 h-3 bg-amber-500 rounded-sm border border-amber-700"></div> Supporting</span>
              <span className="flex items-center gap-1"><div className="w-3 h-3 bg-gray-500 rounded-sm border border-gray-700"></div> Generic</span>
            </div>
          </div>

          <div className="border rounded-md p-4 bg-background">
            <MermaidDiagram definition={mermaidDef} />
          </div>

          {/* Relationship table */}
          {data.context_relationships.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold mb-2">Relationships</h4>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Source</TableHead>
                      <TableHead>Relationship</TableHead>
                      <TableHead>Target</TableHead>
                      <TableHead>Description</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.context_relationships.map((rel, i) => (
                      <TableRow key={i}>
                        <TableCell className="font-medium">{rel.source_context}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-xs">
                            {RELATIONSHIP_LABELS[rel.relationship_type] || rel.relationship_type}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-medium">{rel.target_context}</TableCell>
                        <TableCell className="text-sm max-w-[400px] break-words whitespace-pre-wrap">{rel.description}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          )}
        </TabsContent>

        {/* Details — Cards */}
        <TabsContent value="details" className="mt-4 space-y-4">
          <div className="grid gap-3 md:grid-cols-2">
            {data.bounded_contexts.map((ctx) => (
              <Card key={ctx.name} className="bg-muted/30">
                <CardHeader className="py-3 px-4">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">{ctx.name}</CardTitle>
                    <Badge variant="outline" className={`text-xs ${DOMAIN_TYPE_COLORS[ctx.domain_type]}`}>
                      {ctx.domain_type}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="pb-3 px-4 pt-0 space-y-2">
                  <p className="text-xs text-muted-foreground">{ctx.purpose}</p>
                  {ctx.key_aggregates.length > 0 && (
                    <div>
                      <p className="text-xs font-medium mb-1">Key Aggregates</p>
                      <div className="flex flex-wrap gap-1">
                        {ctx.key_aggregates.map((a) => (
                          <Badge key={a} variant="outline" className="text-xs bg-amber-500/15 text-amber-400 border-amber-500/30">{a}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {ctx.ubiquitous_language_terms.length > 0 && (
                    <div>
                      <p className="text-xs font-medium mb-1">Terms</p>
                      <div className="flex flex-wrap gap-1">
                        {ctx.ubiquitous_language_terms.map((t) => (
                          <Badge key={t} variant="outline" className="text-xs">{t}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Term overlaps */}
          {data.term_overlaps.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold mb-2">Term Overlaps</h4>
              <div className="space-y-2">
                {data.term_overlaps.map((overlap) => (
                  <Card key={overlap.term_name} className="bg-muted/30">
                    <CardHeader className="py-3 px-4">
                      <CardTitle className="text-sm">
                        <Tooltip>
                          <TooltipTrigger className="underline decoration-dashed cursor-help">
                            {overlap.term_name}
                          </TooltipTrigger>
                          <TooltipContent>Term with different meanings across contexts</TooltipContent>
                        </Tooltip>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pb-3 px-4 pt-0 space-y-1">
                      {overlap.contexts_and_meanings.map((cm) => (
                        <div key={cm.context_name} className="flex gap-2 text-xs">
                          <Badge variant="outline" className="text-xs shrink-0">{cm.context_name}</Badge>
                          <span className="text-muted-foreground">{cm.meaning}</span>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
