"use client";

import { useEffect, useRef, useId, useCallback } from "react";

/**
 * Render a Mermaid diagram from a text definition.
 *
 * Mermaid SVGs use a `viewBox` which causes the browser to scale them
 * to fill their container — making wide diagrams tiny. We fix this by
 * reading the viewBox's natural width and setting it as an explicit
 * pixel `width` on the SVG so it renders at full size and the outer
 * container scrolls horizontally when needed.
 */
export function MermaidDiagram({ definition }: { definition: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const uniqueId = useId().replace(/:/g, "");

  const renderDiagram = useCallback(async () => {
    const container = containerRef.current;
    if (!container) return;

    const mermaid = (await import("mermaid")).default;
    const isDark = document.documentElement.classList.contains("dark");

    mermaid.initialize({
      startOnLoad: false,
      theme: isDark ? "dark" : "default",
      flowchart: { curve: "basis", padding: 16 },
      securityLevel: "loose",
    });

    try {
      const { svg } = await mermaid.render(
        `mermaid-${uniqueId}-${Date.now()}`,
        definition,
      );

      container.innerHTML = svg;

      // Fix the SVG sizing: read its natural width from the viewBox
      // and set it as an explicit width so the SVG doesn't scale down.
      const svgEl = container.querySelector("svg");
      if (svgEl) {
        // Remove Mermaid's constraining inline styles
        svgEl.style.maxWidth = "none";
        svgEl.removeAttribute("width");

        // Read the natural dimensions from the viewBox
        const viewBox = svgEl.getAttribute("viewBox");
        if (viewBox) {
          const parts = viewBox.split(/[\s,]+/);
          const vbWidth = parseFloat(parts[2]);
          const vbHeight = parseFloat(parts[3]);
          if (vbWidth && vbHeight) {
            // Set the SVG to its natural pixel size
            svgEl.setAttribute("width", `${vbWidth}px`);
            svgEl.setAttribute("height", `${vbHeight}px`);
          }
        }
      }
    } catch {
      container.innerHTML = `<pre class="text-xs text-destructive">${definition}</pre>`;
    }
  }, [definition, uniqueId]);

  useEffect(() => {
    renderDiagram();
  }, [renderDiagram]);

  return (
    <div
      ref={containerRef}
      className="overflow-x-auto rounded-md border bg-muted/20 p-4"
    />
  );
}
