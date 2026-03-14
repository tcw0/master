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
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Box, ChevronDown, Layers, ShieldCheck } from "lucide-react";
import type { AggregatesArtifact, Aggregate } from "@/lib/types";

// ---------------------------------------------------------------------------
// Styling
// ---------------------------------------------------------------------------

const SIZE_COLORS: Record<string, string> = {
  small: "bg-green-500/15 text-green-400 border-green-500/30",
  moderate: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
  large: "bg-red-500/15 text-red-400 border-red-500/30",
};

// ---------------------------------------------------------------------------
// Aggregate Card
// ---------------------------------------------------------------------------

function AggregateCard({ agg }: { agg: Aggregate }) {
  return (
    <Card className="bg-muted/30">
      <CardHeader className="py-3 px-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Box className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-sm">{agg.name}</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Tooltip>
              <TooltipTrigger>
                <Badge variant="outline" className={`text-xs ${SIZE_COLORS[agg.size_evaluation]}`}>
                  {agg.size_evaluation}
                </Badge>
              </TooltipTrigger>
              <TooltipContent className="max-w-xs">
                <p className="text-xs">{agg.size_rationale}</p>
              </TooltipContent>
            </Tooltip>
          </div>
        </div>
        <p className="text-xs text-muted-foreground mt-1">
          Root: <span className="font-medium text-foreground">{agg.root_entity}</span>
        </p>
      </CardHeader>
      <CardContent className="pb-3 px-4 pt-0 space-y-3">
        {/* Elements */}
        <Collapsible>
          <CollapsibleTrigger className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground">
            <ChevronDown className="h-3 w-3" />
            <Layers className="h-3 w-3" />
            Elements ({agg.elements.length})
          </CollapsibleTrigger>
          <CollapsibleContent className="mt-2 space-y-1.5 pl-5">
            {agg.elements.map((el) => (
              <div key={el.name} className="flex items-start gap-2">
                <Badge
                  variant="outline"
                  className={`text-xs shrink-0 ${
                    el.element_type === "entity"
                      ? "bg-blue-500/15 text-blue-400 border-blue-500/30"
                      : "bg-teal-500/15 text-teal-400 border-teal-500/30"
                  }`}
                >
                  {el.element_type === "entity" ? "E" : "VO"}
                </Badge>
                <div>
                  <p className="text-xs font-medium">{el.name}</p>
                  <p className="text-xs text-muted-foreground">{el.description}</p>
                  {el.properties.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-0.5">
                      {el.properties.map((p) => (
                        <span key={p} className="text-xs text-muted-foreground font-mono bg-muted px-1 rounded">
                          {p}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </CollapsibleContent>
        </Collapsible>

        {/* Invariants */}
        {agg.invariants.length > 0 && (
          <Collapsible>
            <CollapsibleTrigger className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground">
              <ChevronDown className="h-3 w-3" />
              <ShieldCheck className="h-3 w-3" />
              Invariants ({agg.invariants.length})
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-2 space-y-1 pl-5">
              {agg.invariants.map((inv) => (
                <Tooltip key={inv.name}>
                  <TooltipTrigger className="text-left">
                    <Badge variant="outline" className="text-xs bg-purple-500/15 text-purple-400 border-purple-500/30">
                      {inv.name}
                    </Badge>
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs">
                    <p className="text-xs">{inv.description}</p>
                  </TooltipContent>
                </Tooltip>
              ))}
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Commands */}
        {agg.commands.length > 0 && (
          <Collapsible>
            <CollapsibleTrigger className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground">
              <ChevronDown className="h-3 w-3" />
              Commands ({agg.commands.length})
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-2 space-y-2 pl-5">
              {agg.commands.map((cmd) => (
                <div key={cmd.name} className="space-y-1">
                  <p className="text-xs font-medium">{cmd.name}</p>
                  <p className="text-xs text-muted-foreground">{cmd.description}</p>
                  {cmd.parameters.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {cmd.parameters.map((p) => (
                        <span key={p} className="text-xs font-mono bg-muted px-1 rounded text-muted-foreground">
                          {p}
                        </span>
                      ))}
                    </div>
                  )}
                  <div className="flex flex-wrap gap-1">
                    {cmd.emitted_events.map((e) => (
                      <Badge key={e} variant="outline" className="text-xs bg-orange-500/15 text-orange-400 border-orange-500/30">
                        {e}
                      </Badge>
                    ))}
                    {cmd.rules_applied.map((r) => (
                      <Badge key={r} variant="outline" className="text-xs bg-purple-500/15 text-purple-400 border-purple-500/30">
                        {r}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Domain events summary */}
        {agg.domain_events.length > 0 && (
          <div className="flex flex-wrap gap-1 pt-1 border-t border-border/40">
            {agg.domain_events.map((e) => (
              <Badge key={e} variant="outline" className="text-xs bg-orange-500/15 text-orange-400 border-orange-500/30">
                {e}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function AggregatesViewer({ data }: { data: AggregatesArtifact }) {
  // Group aggregates by bounded context
  const grouped = useMemo(() => {
    const map = new Map<string, Aggregate[]>();
    for (const agg of data.aggregates) {
      const group = map.get(agg.bounded_context) || [];
      group.push(agg);
      map.set(agg.bounded_context, group);
    }
    return map;
  }, [data.aggregates]);

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
        <span>{data.aggregates.length} aggregates</span>
        <span>{grouped.size} bounded contexts</span>
      </div>

      {/* Grouped aggregates */}
      {Array.from(grouped.entries()).map(([context, aggregates]) => (
        <div key={context} className="space-y-3">
          <h4 className="text-sm font-semibold border-b border-border/40 pb-1">
            {context}
          </h4>
          <div className="grid gap-3 md:grid-cols-2">
            {aggregates.map((agg) => (
              <AggregateCard key={agg.name} agg={agg} />
            ))}
          </div>
        </div>
      ))}

      {/* Design decisions */}
      {data.design_decisions.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-border">
          <h4 className="text-sm font-semibold">Design Decisions</h4>
          <ul className="space-y-1">
            {data.design_decisions.map((d, i) => (
              <li key={i} className="text-xs text-muted-foreground pl-4 relative before:content-['•'] before:absolute before:left-0">
                {d}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
