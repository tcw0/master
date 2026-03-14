"use client";

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
import { Shield } from "lucide-react";
import type { ArchitectureArtifact, HexagonalArchitecture } from "@/lib/types";

// ---------------------------------------------------------------------------
// Layer config
// ---------------------------------------------------------------------------

interface LayerConfig {
  key: keyof Pick<
    HexagonalArchitecture,
    "presentation_layer" | "infrastructure_layer" | "application_layer" | "domain_layer"
  >;
  label: string;
  bg: string;
  border: string;
}

const LAYERS: LayerConfig[] = [
  {
    key: "presentation_layer",
    label: "Presentation",
    bg: "bg-sky-500/5",
    border: "border-sky-500/20",
  },
  {
    key: "infrastructure_layer",
    label: "Infrastructure",
    bg: "bg-emerald-500/5",
    border: "border-emerald-500/20",
  },
  {
    key: "application_layer",
    label: "Application",
    bg: "bg-amber-500/5",
    border: "border-amber-500/20",
  },
  {
    key: "domain_layer",
    label: "Domain",
    bg: "bg-indigo-500/10",
    border: "border-indigo-500/30",
  },
];

const ELEMENT_TYPE_COLORS: Record<string, string> = {
  // Domain
  entity: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  value_object: "bg-teal-500/15 text-teal-400 border-teal-500/30",
  domain_service: "bg-indigo-500/15 text-indigo-400 border-indigo-500/30",
  repository_interface: "bg-violet-500/15 text-violet-400 border-violet-500/30",
  domain_event: "bg-orange-500/15 text-orange-400 border-orange-500/30",
  // Application
  application_service: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  dto: "bg-slate-500/15 text-slate-400 border-slate-500/30",
  command: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  query: "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
  command_handler: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  query_handler: "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
  // Infrastructure
  repository_implementation: "bg-violet-500/15 text-violet-400 border-violet-500/30",
  external_adapter: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  event_publisher: "bg-orange-500/15 text-orange-400 border-orange-500/30",
  persistence_config: "bg-slate-500/15 text-slate-400 border-slate-500/30",
  messaging: "bg-pink-500/15 text-pink-400 border-pink-500/30",
  // Presentation
  rest_controller: "bg-sky-500/15 text-sky-400 border-sky-500/30",
  graphql_resolver: "bg-fuchsia-500/15 text-fuchsia-400 border-fuchsia-500/30",
  api_dto: "bg-slate-500/15 text-slate-400 border-slate-500/30",
  middleware: "bg-gray-500/15 text-gray-400 border-gray-500/30",
};

const INTERFACE_TYPE_COLORS: Record<string, string> = {
  rest_api: "bg-sky-500/15 text-sky-400 border-sky-500/30",
  graphql_api: "bg-fuchsia-500/15 text-fuchsia-400 border-fuchsia-500/30",
  domain_events: "bg-orange-500/15 text-orange-400 border-orange-500/30",
  shared_kernel: "bg-violet-500/15 text-violet-400 border-violet-500/30",
};

// ---------------------------------------------------------------------------
// Concentric layers component
// ---------------------------------------------------------------------------

function HexagonalView({ arch }: { arch: HexagonalArchitecture }) {
  return (
    <div className="space-y-1">
      {LAYERS.map((layer) => {
        const elements = arch[layer.key];
        return (
          <div
            key={layer.key}
            className={`rounded-lg border p-3 ${layer.bg} ${layer.border}`}
          >
            <p className="text-xs font-semibold mb-2 text-muted-foreground uppercase tracking-wider">
              {layer.label} Layer
            </p>
            {elements.length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {elements.map((el) => (
                  <Tooltip key={el.name}>
                    <TooltipTrigger>
                      <Badge
                        variant="outline"
                        className={`text-xs ${ELEMENT_TYPE_COLORS[el.element_type] || ""}`}
                      >
                        {el.name}
                      </Badge>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs">
                      <p className="text-xs font-medium">{el.element_type.replace(/_/g, " ")}</p>
                      <p className="text-xs text-muted-foreground">{el.description}</p>
                    </TooltipContent>
                  </Tooltip>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground italic">No elements</p>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export function ArchitectureViewer({ data }: { data: ArchitectureArtifact }) {
  const defaultTab = data.architectures[0]?.bounded_context || "";

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
        <span>{data.architectures.length} architectures</span>
        <span>{data.anti_corruption_layers.length} ACLs</span>
        <span>{data.published_interfaces.length} interfaces</span>
        <span>{data.technical_patterns.length} patterns</span>
      </div>

      {/* Per-context hexagonal architectures */}
      {data.architectures.length > 0 && (
        <Tabs defaultValue={defaultTab}>
          <TabsList className="flex-wrap h-auto gap-1">
            {data.architectures.map((arch) => (
              <TabsTrigger key={arch.bounded_context} value={arch.bounded_context} className="text-xs">
                {arch.bounded_context}
              </TabsTrigger>
            ))}
          </TabsList>
          {data.architectures.map((arch) => (
            <TabsContent key={arch.bounded_context} value={arch.bounded_context} className="mt-4">
              <HexagonalView arch={arch} />
            </TabsContent>
          ))}
        </Tabs>
      )}

      {/* Anti-corruption layers */}
      {data.anti_corruption_layers.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-border">
          <h4 className="text-sm font-semibold flex items-center gap-1.5">
            <Shield className="h-3.5 w-3.5" />
            Anti-Corruption Layers
          </h4>
          <div className="grid gap-2 md:grid-cols-2">
            {data.anti_corruption_layers.map((acl, i) => (
              <Card key={i} className="bg-muted/30">
                <CardHeader className="py-3 px-4">
                  <CardTitle className="text-xs">
                    {acl.owning_context} ← {acl.foreign_context}
                  </CardTitle>
                </CardHeader>
                <CardContent className="pb-3 px-4 pt-0 space-y-1">
                  <p className="text-xs text-muted-foreground">{acl.translation_description}</p>
                  <div className="flex flex-wrap gap-1">
                    {acl.translated_elements.map((el) => (
                      <Badge key={el} variant="outline" className="text-xs">{el}</Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Published interfaces */}
      {data.published_interfaces.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-border">
          <h4 className="text-sm font-semibold">Published Interfaces</h4>
          <div className="grid gap-2 md:grid-cols-2">
            {data.published_interfaces.map((pi, i) => (
              <Card key={i} className="bg-muted/30">
                <CardHeader className="py-3 px-4">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-xs">{pi.bounded_context}</CardTitle>
                    <Badge variant="outline" className={`text-xs ${INTERFACE_TYPE_COLORS[pi.interface_type] || ""}`}>
                      {pi.interface_type.replace(/_/g, " ")}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="pb-3 px-4 pt-0 space-y-1">
                  <p className="text-xs text-muted-foreground">{pi.description}</p>
                  <div className="flex flex-wrap gap-1">
                    {pi.exposed_operations.map((op) => (
                      <Badge key={op} variant="outline" className="text-xs">{op}</Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Technical patterns */}
      {data.technical_patterns.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-border">
          <h4 className="text-sm font-semibold">Technical Patterns</h4>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Pattern</TableHead>
                  <TableHead>Applied In</TableHead>
                  <TableHead>Justification</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.technical_patterns.map((tp, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium text-sm">{tp.pattern_name}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-xs">{tp.applied_in_context}</Badge>
                    </TableCell>
                    <TableCell className="text-sm">{tp.justification}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      )}
    </div>
  );
}
