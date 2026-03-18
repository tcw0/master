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
  const [showOnlyAmbiguous, setShowOnlyAmbiguous] = useState(false);
  const [hintsOpen, setHintsOpen] = useState(false);

  // Count terms per category for filter badges
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const t of data.terms) {
      counts[t.category] = (counts[t.category] || 0) + 1;
    }
    return counts;
  }, [data.terms]);

  const filteredTerms = useMemo(() => {
    let result = data.terms;
    if (activeCategory) {
      result = result.filter((t) => t.category === activeCategory);
    }
    if (showOnlyAmbiguous) {
      result = result.filter((t) => t.is_ambiguous);
    }
    return result;
  }, [data.terms, activeCategory, showOnlyAmbiguous]);

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

      {/* Filters bar */}
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex flex-wrap gap-1.5 items-center">
          <span className="text-xs font-semibold text-muted-foreground mr-1 hidden sm:inline-block">Category:</span>
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

        {ambiguousCount > 0 && (
          <div className="flex flex-wrap gap-2 items-center sm:border-l sm:pl-4 border-muted">
            <span className="text-xs font-semibold text-muted-foreground hidden sm:inline-block">Status:</span>
            <Badge
              variant={showOnlyAmbiguous ? "default" : "outline"}
              className={`cursor-pointer text-xs ${
                showOnlyAmbiguous 
                  ? "bg-amber-500 hover:bg-amber-600 text-white border-transparent" 
                  : "text-amber-500 border-amber-500/30 hover:bg-amber-500/10"
              }`}
              onClick={() => setShowOnlyAmbiguous(!showOnlyAmbiguous)}
            >
              <AlertTriangle className="h-3 w-3 mr-1.5" />
              Ambiguous Only
            </Badge>
            {showOnlyAmbiguous && (
                <span className="text-xs text-muted-foreground">
                    Showing {filteredTerms.length} of {ambiguousCount}
                </span>
            )}
          </div>
        )}
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
                <TableCell className="max-w-[400px] break-words whitespace-pre-wrap">
                  <p className="text-sm">{term.definition}</p>
                  {term.business_context && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {term.business_context}
                    </p>
                  )}
                </TableCell>
                <TableCell className="max-w-[200px]">
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
