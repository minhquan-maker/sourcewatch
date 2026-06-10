import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { Network, AlertTriangle, ShieldCheck } from "lucide-react";

function getNodeColor(score) {
  if (score >= 7.5) return "#22d3ee";
  if (score >= 5.5) return "#f59e0b";
  if (score >= 3.5) return "#ef4444";
  return "#64748b";
}

function getNodeLabel(score) {
  if (score >= 7.5) return "Trusted";
  if (score >= 5.5) return "Neutral";
  if (score >= 3.5) return "Low";
  return "Unknown";
}

export default function SourceGraph({ sourceNetwork }) {
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  const [tooltip, setTooltip] = useState(null);
  const [stats, setStats] = useState({ total: 0, edges: 0, avgTrust: 0 });

  const nodes = sourceNetwork?.nodes || [];
  const edges = sourceNetwork?.edges || [];

  useEffect(() => {
    if (!svgRef.current || !containerRef.current || nodes.length === 0) return;

    const container = containerRef.current;
    const rect = container.getBoundingClientRect();
    const width = rect.width || 800;
    const height = Math.max(420, Math.max(400, nodes.length * 70));

    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3
      .select(svgRef.current)
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", `0 0 ${width} ${height}`);

    // Defs: glow filter + gradient
    const defs = svg.append("defs");

    const glow = defs
      .append("filter")
      .attr("id", "glow")
      .attr("x", "-50%")
      .attr("y", "-50%")
      .attr("width", "200%")
      .attr("height", "200%");
    glow.append("feGaussianBlur").attr("stdDeviation", "4").attr("result", "blur");
    const merge = glow.append("feMerge");
    merge.append("feMergeNode").attr("in", "blur");
    merge.append("feMergeNode").attr("in", "SourceGraphic");

    const grad = defs
      .append("radialGradient")
      .attr("id", "nodeGrad")
      .attr("cx", "40%")
      .attr("cy", "40%");
    grad.append("stop").attr("offset", "0%").attr("stop-color", "#22d3ee").attr("stop-opacity", 0.4);
    grad.append("stop").attr("offset", "100%").attr("stop-color", "#22d3ee").attr("stop-opacity", 0.05);

    const g = svg.append("g");

    // Clone nodes/edges to avoid mutating D3 state
    const simNodes = nodes.map((n) => ({ ...n }));
    const simEdges = edges.map((e) => ({ ...e }));

    const simulation = d3
      .forceSimulation(simNodes)
      .force(
        "link",
        d3
          .forceLink(simEdges)
          .id((d) => d.domain)
          .distance(150)
          .strength(0.5)
      )
      .force("charge", d3.forceManyBody().strength(-400))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(60))
      .force("x", d3.forceX(width / 2).strength(0.05))
      .force("y", d3.forceY(height / 2).strength(0.05));

    // Draw edges
    const link = g
      .append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(simEdges)
      .join("line")
      .attr("stroke", "#2a3a52")
      .attr("stroke-width", 1.5)
      .attr("stroke-opacity", 0)
      .attr("stroke-dasharray", "6,4");

    // Animate edges in
    link
      .transition()
      .duration(800)
      .delay((_, i) => i * 60)
      .attr("stroke-opacity", 0.5);

    // Draw nodes
    const node = g
      .append("g")
      .attr("class", "nodes")
      .selectAll("g")
      .data(simNodes)
      .join("g")
      .attr("opacity", 0)
      .call(
        d3
          .drag()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    // Animate nodes in
    node.transition().duration(600).delay((_, i) => 200 + i * 80).attr("opacity", 1);

    // Outer glow ring (transparent fill)
    node
      .append("circle")
      .attr("r", (d) => 32 + (d.total_articles || 0) * 2)
      .attr("fill", "url(#nodeGrad)")
      .attr("stroke", "none");

    // Main circle
    node
      .append("circle")
      .attr("r", (d) => Math.min(28, 14 + (d.total_articles || 0) * 2.5))
      .attr("fill", (d) => getNodeColor(d.trust_score || 5))
      .attr("fill-opacity", 0.15)
      .attr("stroke", (d) => getNodeColor(d.trust_score || 5))
      .attr("stroke-width", 2)
      .attr("filter", "url(#glow)");

    // Trust ring arc
    node
      .append("circle")
      .attr("r", (d) => Math.min(28, 14 + (d.total_articles || 0) * 2.5) + 4)
      .attr("fill", "none")
      .attr("stroke", (d) => getNodeColor(d.trust_score || 5))
      .attr("stroke-width", 1.5)
      .attr("stroke-opacity", 0.4)
      .attr("stroke-dasharray", (d) => {
        const circumference = 2 * Math.PI * (Math.min(28, 14 + (d.total_articles || 0) * 2.5) + 4);
        const filled = (d.trust_score || 5) / 10;
        return `${circumference * filled} ${circumference}`;
      });

    // Domain initial (first letter)
    node
      .append("text")
      .text((d) => (d.name || d.domain || "?").charAt(0).toUpperCase())
      .attr("text-anchor", "middle")
      .attr("dy", "0.35em")
      .attr("fill", (d) => getNodeColor(d.trust_score || 5))
      .attr("font-size", "13px")
      .attr("font-weight", "700")
      .attr("font-family", "Syne, sans-serif");

    // Name label below
    node
      .append("text")
      .text((d) => {
        const name = d.name || d.domain || "";
        return name.length > 16 ? name.substring(0, 14) + "…" : name;
      })
      .attr("text-anchor", "middle")
      .attr("dy", "3em")
      .attr("fill", "#94a3b8")
      .attr("font-size", "10px")
      .attr("font-family", "DM Sans, sans-serif");

    // Hover interactions
    node
      .on("mouseenter", function (event, d) {
        d3.select(this).select("circle:nth-child(2)").attr("fill-opacity", 0.3);
        setTooltip({
          x: event.clientX,
          y: event.clientY,
          data: d,
        });
      })
      .on("mousemove", function (event) {
        setTooltip((prev) => prev ? { ...prev, x: event.clientX, y: event.clientY } : null);
      })
      .on("mouseleave", function () {
        d3.select(this).select("circle:nth-child(2)").attr("fill-opacity", 0.15);
        setTooltip(null);
      });

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y);

      node.attr("transform", (d) => `translate(${d.x},${d.y})`);
    });

    const zoom = d3.zoom().scaleExtent([0.4, 3]).on("zoom", (event) => {
      g.attr("transform", event.transform);
    });
    svg.call(zoom);

    return () => simulation.stop();
  }, [nodes, edges]);

  // Compute stats
  useEffect(() => {
    if (nodes.length === 0) return;
    const avgTrust = nodes.reduce((s, n) => s + (n.trust_score || 5), 0) / nodes.length;
    setStats({ total: nodes.length, edges: edges.length, avgTrust: Math.round(avgTrust * 10) / 10 });
  }, [nodes, edges]);

  if (nodes.length === 0) {
    return (
      <div className="bg-surface border border-border rounded-2xl p-6">
        <div className="flex items-center gap-2 mb-4">
          <Network className="w-5 h-5 text-accent" />
          <span className="font-display text-sm font-semibold tracking-wide text-text-secondary uppercase">
            Source Network
          </span>
        </div>
        <p className="text-body text-text-tertiary text-center py-8">
          No source network data available yet.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-surface border border-border rounded-2xl p-6 animate-fade-up-2">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Network className="w-5 h-5 text-accent" />
          <span className="font-display text-sm font-semibold tracking-wide text-text-secondary uppercase">
            Source Network
          </span>
        </div>
        <div className="flex items-center gap-4 text-xs text-text-tertiary font-mono">
          <span>{stats.total} sources</span>
          <span>{stats.edges} connections</span>
          <span>avg trust {stats.avgTrust}</span>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mb-4 text-xs">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full border-2" style={{ borderColor: "#22d3ee", background: "rgba(34,211,238,0.15)" }} />
          <span className="text-text-tertiary">Trusted (≥7.5)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full border-2" style={{ borderColor: "#f59e0b", background: "rgba(245,158,11,0.15)" }} />
          <span className="text-text-tertiary">Neutral</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full border-2" style={{ borderColor: "#ef4444", background: "rgba(239,68,68,0.15)" }} />
          <span className="text-text-tertiary">Low</span>
        </div>
        <div className="ml-auto flex items-center gap-1.5">
          <span className="w-4 h-0.5 border-t-2 border-dashed" style={{ borderColor: "#2a3a52" }} />
          <span className="text-text-tertiary">propagation</span>
        </div>
      </div>

      {/* Graph */}
      <div
        ref={containerRef}
        className="w-full overflow-hidden rounded-xl bg-bg/50 cursor-grab active:cursor-grabbing"
        style={{ minHeight: 420 }}
      >
        <svg ref={svgRef} className="w-full" />
      </div>

      {/* Tooltip */}
      {tooltip && (
        <div
          className="fixed z-50 bg-surface-alt border border-border-light rounded-xl px-4 py-3 shadow-xl pointer-events-none"
          style={{
            left: tooltip.x + 12,
            top: tooltip.y - 10,
            minWidth: 180,
          }}
        >
          <div className="flex items-center gap-2 mb-2">
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: getNodeColor(tooltip.data.trust_score || 5) }}
            />
            <span className="font-display text-sm font-semibold text-text-primary">
              {tooltip.data.name || tooltip.data.domain}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
            <span className="text-text-tertiary">Trust score</span>
            <span className="text-text-primary font-mono font-medium">
              {tooltip.data.trust_score || 5}/10
            </span>
            <span className="text-text-tertiary">Articles</span>
            <span className="text-text-primary font-mono font-medium">
              {tooltip.data.total_articles || 0}
            </span>
            <span className="text-text-tertiary">Status</span>
            <span
              className="font-medium"
              style={{ color: getNodeColor(tooltip.data.trust_score || 5) }}
            >
              {getNodeLabel(tooltip.data.trust_score || 5)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}