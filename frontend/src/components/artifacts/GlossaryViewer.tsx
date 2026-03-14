"use client";

import { useState, useMemo } from "react";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
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
import { AlertTriangle, ChevronDown, ChevronRight } from "lucide-react";
import type { GlossaryArtifact, GlossaryTerm } from "@/lib/types";

// ---------------------------------------------------------------------------
// Category colors
// ---------------------------------------------------------------------------

const CATEGORY_COLORS: Record<GlossaryTerm["category"], string> = {
  entity: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  value_object: "bg-teal-500/15 text-teal-400 border-teal-500/30",
  command: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  event: "bg-orange-500/15 text-orange-400 border-orange-500/30",
  rule_policy: "bg-purple-500/15 text-purple-400 border-purple-500/30",
  role: "bg-green-500/15 text-green-400 border-green-500/30",
  state: "bg-slate-500/15 text-slate-400 border-slate-500/30",
  other: "bg-gray-500/15 text-gray-400 border-gray-500/30",
};

const CATEGORY_LABELS: Record<GlossaryTerm["category"], string> = {
  entity: "Entity",
  value_object: "Value Object",
  command: "Command",
  event: "Event",
  rule_policy: "Rule / Policy",
  role: "Role",
  state: "State",
  other: "Other",
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function GlossaryViewer({ data }: { data: GlossaryArtifact }) {
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [hintsOpen, setHintsOpen] = useState(false);

  // Count terms per category for filter badges
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const t of data.terms) {
      counts[t.category] = (counts[t.category] || 0) + 1;
    }
    return counts;
  }, [data.terms]);

  const filteredTerms = useMemo(
    () =>
      activeCategory
        ? data.terms.filter((t) => t.category === activeCategory)
        : data.terms,
    [data.terms, activeCategory],
  );

  const ambiguousCount = data.terms.filter((t) => t.is_ambiguous).length;

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="flex items-center gap-3 text-sm text-muted-foreground">
        <span>{data.terms.length} terms</span>
        {ambiguousCount > 0 && (
          <span className="flex items-center gap-1 text-amber-400">
            <AlertTriangle className="h-3.5 w-3.5" />
            {ambiguousCount} ambiguous
          </span>
        )}
      </div>

      {/* Category filter bar */}
      <div className="flex flex-wrap gap-1.5">
        <Badge
          variant={activeCategory === null ? "default" : "outline"}
          className="cursor-pointer text-xs"
          onClick={() => setActiveCategory(null)}
        >
          All ({data.terms.length})
        </Badge>
        {Object.entries(categoryCounts).map(([cat, count]) => (
          <Badge
            key={cat}
            variant="outline"
            className={`cursor-pointer text-xs ${
              activeCategory === cat ? CATEGORY_COLORS[cat as GlossaryTerm["category"]] : ""
            }`}
            onClick={() => setActiveCategory(activeCategory === cat ? null : cat)}
          >
            {CATEGORY_LABELS[cat as GlossaryTerm["category"]]} ({count})
          </Badge>
        ))}
      </div>

      {/* Terms table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[180px]">Term</TableHead>
              <TableHead className="w-[100px]">Category</TableHead>
              <TableHead>Definition</TableHead>
              <TableHead className="w-[140px]">Related Terms</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredTerms.map((term) => (
              <TableRow key={term.name}>
                <TableCell className="font-medium">
                  <div className="flex items-center gap-2">
                    {term.name}
                    {term.is_ambiguous && (
                      <Tooltip>
                        <TooltipTrigger>
                          <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-xs">
                          <p className="text-xs">{term.clarification_needed || "Ambiguous term"}</p>
                        </TooltipContent>
                      </Tooltip>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <Badge
                    variant="outline"
                    className={`text-xs ${CATEGORY_COLORS[term.category]}`}
                  >
                    {CATEGORY_LABELS[term.category]}
                  </Badge>
                </TableCell>
                <TableCell>
                  <p className="text-sm">{term.definition}</p>
                  {term.business_context && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {term.business_context}
                    </p>
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {term.related_terms.map((rt) => (
                      <Badge key={rt} variant="outline" className="text-xs">
                        {rt}
                      </Badge>
                    ))}
                  </div>
                </TableCell>
              </TableRow>
            ))}
            {filteredTerms.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-muted-foreground py-8">
                  No terms match the selected filter.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Bounded context hints */}
      {data.bounded_context_hints && data.bounded_context_hints.length > 0 && (
        <Collapsible open={hintsOpen} onOpenChange={setHintsOpen}>
          <CollapsibleTrigger className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground">
            {hintsOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            Bounded Context Hints ({data.bounded_context_hints.length})
          </CollapsibleTrigger>
          <CollapsibleContent className="mt-3 space-y-2">
            {data.bounded_context_hints.map((hint) => (
              <Card key={hint.context_name} className="bg-muted/30">
                <CardHeader className="py-3 px-4">
                  <CardTitle className="text-sm">{hint.context_name}</CardTitle>
                </CardHeader>
                <CardContent className="pb-3 px-4 pt-0 space-y-2">
                  <div className="flex flex-wrap gap-1">
                    {hint.term_names.map((t) => (
                      <Badge key={t} variant="outline" className="text-xs">
                        {t}
                      </Badge>
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground">{hint.reasoning}</p>
                </CardContent>
              </Card>
            ))}
          </CollapsibleContent>
        </Collapsible>
      )}
    </div>
  );
}
