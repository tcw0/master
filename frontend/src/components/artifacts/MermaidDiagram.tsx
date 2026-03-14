"use client";

import { useEffect, useRef, useId, useState } from "react";

/**
 * Render a Mermaid diagram from a text definition.
 *
 * Re-renders when the definition or the system color scheme changes.
 * Uses dynamic import to keep Mermaid out of the server bundle.
 */
export function MermaidDiagram({ definition }: { definition: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const uniqueId = useId().replace(/:/g, "");
  const [svg, setSvg] = useState<string>("");

  useEffect(() => {
    let cancelled = false;

    async function render() {
      const mermaid = (await import("mermaid")).default;

      // Detect dark mode from the <html> element
      const isDark = document.documentElement.classList.contains("dark");

      mermaid.initialize({
        startOnLoad: false,
        theme: isDark ? "dark" : "default",
        flowchart: { curve: "basis", padding: 16 },
        securityLevel: "loose", // allow click callbacks
      });

      try {
        const { svg: rendered } = await mermaid.render(
          `mermaid-${uniqueId}-${Date.now()}`,
          definition,
        );
        if (!cancelled) setSvg(rendered);
      } catch {
        // Fall back to showing the raw definition on parse errors
        if (!cancelled) setSvg(`<pre class="text-xs text-destructive">${definition}</pre>`);
      }
    }

    render();
    return () => { cancelled = true; };
  }, [definition, uniqueId]);

  return (
    <div
      ref={containerRef}
      className="overflow-x-auto rounded-md border bg-muted/20 p-4 [&_svg]:mx-auto"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
