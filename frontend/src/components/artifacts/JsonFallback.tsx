"use client";

import { ScrollArea } from "@/components/ui/scroll-area";

/**
 * Raw JSON display — used as fallback and "View JSON" toggle target.
 */
export function JsonFallback({ data }: { data: unknown }) {
  return (
    <ScrollArea className="h-[500px] rounded-md border bg-muted/30 p-4">
      <pre className="text-xs font-mono whitespace-pre-wrap break-words">
        {JSON.stringify(data, null, 2)}
      </pre>
    </ScrollArea>
  );
}
