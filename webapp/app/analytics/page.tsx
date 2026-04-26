"use client";

import { useBrand } from "@/hooks/useBrand";
import { ChartSkeleton } from "@/components/charts/ChartSkeleton";
import { humanGapType } from "@/lib/display-labels";
import { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from "recharts";

/* ── Unified color system ────────────────────────────────────── */

// Strategic status colors (decision-oriented: "what does this mean?")
const STATUS_COLORS: Record<string, string> = {
  strategic_gap: "#FB2C36",
  emerging_opportunity: "rgb(234,88,12)",
  non_priority: "rgb(156,163,175)",
  owned_strength: "rgb(22,163,74)",
};

// Gap type colors (taxonomy: "what kind of fix?")
const GAP_COLORS: Record<string, string> = {
  perception: "#FB2C36",
  indexing: "rgb(234,88,12)",
  volume_frequency: "rgb(124,58,237)",
};
const STRONGHOLD_COLOR = "rgb(22,163,74)";

// Competitor comparison
const BRAND_COLOR = "rgb(22,163,74)";
const COMPETITOR_COLOR = "rgba(23,23,23,0.35)";

// Radar: muted palette per topic (max 5)
const RADAR_COLORS = [
  "rgb(79,70,229)", "#FB2C36", "rgb(234,88,12)",
  "rgb(124,58,237)", "rgb(0,146,184)",
];

function statusColor(status: string | null): string {
  return status ? STATUS_COLORS[status] ?? "rgb(0,146,184)" : STRONGHOLD_COLOR;
}

/* ── fade-slide wrapper ─────────────────────────────────────── */
function FadeSlide({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(t);
  }, [delay]);
  return (
    <div
      className="transition-all duration-500 ease-out"
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(12px)",
      }}
    >
      {children}
    </div>
  );
}

/* ── custom tooltip ─────────────────────────────────────────── */
function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white rounded-peec-lg shadow-peec-ring p-3 text-peec-sm border border-peec-hairline">
      <div className="font-semibold mb-1">{label}</div>
      {payload.map((p: any) => (
        <div key={p.dataKey} className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full" style={{ background: p.fill || p.stroke || p.color }} />
          <span className="text-peec-muted">{p.name}:</span>
          <span className="font-medium">
            {typeof p.value === "number" ? (p.value % 1 === 0 ? p.value : p.value.toFixed(1)) : p.value}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function AnalyticsPage() {
  const { data, config, loading } = useBrand();

  /* ── loading state ─────────────────────────────────────────── */
  if (loading || !data) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-peec-tint rounded animate-pulse" />
        <div className="grid grid-cols-2 gap-4">
          <ChartSkeleton height={340} />
          <ChartSkeleton height={340} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <ChartSkeleton height={340} />
          <ChartSkeleton height={340} />
        </div>
        <ChartSkeleton height={400} />
      </div>
    );
  }

  /* ── derive chart data ─────────────────────────────────────── */
  const rows = data.study.rows;
  const metricsRows = data.metrics?.rows ?? [];
  const landscape = data.landscape?.topics ?? [];

  // 1. Visibility bar chart — colored by strategic status
  const visData = rows.map((r) => ({
    name: r.cluster_label,
    visibility: Math.round((r.visibility_target_share ?? 0) * 100),
    fill: statusColor(r.strategic_status ?? null),
  }));

  // 2. Action priority — colored by strategic status
  const priorityData = metricsRows.map((m) => {
    const row = rows.find((r) => r.cluster_id === m.cluster_id);
    return {
      name: m.cluster_label,
      opportunity_score: m.opportunity_score,
      fill: statusColor(row?.strategic_status ?? null),
    };
  });

  // 3. Competitor landscape data
  const competitorData = landscape.map((t) => ({
    name: t.cluster_label,
    brand: Math.round((t.target_visibility_share ?? 0) * 100),
    competitor: t.competitor_visibility_share != null ? Math.round(t.competitor_visibility_share * 100) : null,
    competitorOwner: t.competitor_owner,
  }));

  // 4. Gap Mix donut data (replaces useless classification outcomes)
  const gapCounts: Record<string, number> = {};
  rows.forEach((r) => {
    const label = humanGapType(r.gap_type);
    gapCounts[label] = (gapCounts[label] || 0) + 1;
  });
  const gapMixData = Object.entries(gapCounts).map(([name, value]) => ({ name, value }));
  const GAP_MIX_COLORS: Record<string, string> = {
    Discovery: GAP_COLORS.indexing,
    Perception: GAP_COLORS.perception,
    Attention: GAP_COLORS.volume_frequency,
    Stronghold: STRONGHOLD_COLOR,
  };

  // 5. Radar chart data (Topic Signal Profile)
  const radarAxes = [
    { key: "relevance_score", label: "Intent Fit" },
    { key: "source_trust_score", label: "Citation Authority" },
    { key: "proof_strength_score", label: "Evidence Coverage" },
    { key: "method_agreement_score", label: "Signal Alignment" },
    { key: "opportunity_score", label: "Action Priority" },
  ];
  const radarData = radarAxes.map((axis) => {
    const point: Record<string, string | number> = { axis: axis.label };
    metricsRows.forEach((m) => {
      point[m.cluster_label] = (m as Record<string, any>)[axis.key] ?? 0;
    });
    return point;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          {data.brand_name} — Analytics
        </h1>
        <p className="text-peec-muted mt-1 max-w-xl">
          Visual breakdown of visibility, priorities, competition, and topic composition.
        </p>
      </div>

      {/* Row 1: Visibility + Action Priority */}
      <div className="grid grid-cols-2 gap-4">
        {/* 1. Visibility Bar Chart */}
        <FadeSlide delay={0}>
          <div className="bg-white rounded-peec-xl shadow-peec-ring p-4">
            <h2 className="text-peec-lg font-semibold tracking-tight mb-1">
              Visibility by Topic
            </h2>
            <p className="text-peec-xs text-peec-muted mb-3">Where the brand appears across tracked AI-answer topics.</p>
            <div className="flex gap-3 mb-2 text-peec-xs">
              {[["Strategic Gap","#FB2C36"],["Opportunity","rgb(234,88,12)"],["Non-Priority","rgb(156,163,175)"],["Owned","rgb(22,163,74)"]].map(([l,c])=>(
                <span key={l} className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{background:c}}/><span className="text-peec-muted">{l}</span></span>
              ))}
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={visData} margin={{ top: 8, right: 8, bottom: 32, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(23,23,23,0.08)" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 12, fill: "rgba(23,23,23,0.6)" }}
                  angle={-20}
                  textAnchor="end"
                  interval={0}
                  height={60}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fontSize: 12, fill: "rgba(23,23,23,0.6)" }}
                  tickFormatter={(v: number) => `${v}%`}
                />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="visibility" name="Visibility %" radius={[4, 4, 0, 0]}>
                  {visData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </FadeSlide>

        {/* 2. Action Priority Bar Chart */}
        <FadeSlide delay={100}>
          <div className="bg-white rounded-peec-xl shadow-peec-ring p-4">
            <h2 className="text-peec-lg font-semibold tracking-tight mb-1">
              Action Priority
            </h2>
            <p className="text-peec-xs text-peec-muted mb-3">Which topics need action based on strategic importance and evidence.</p>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={priorityData} margin={{ top: 8, right: 8, bottom: 32, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(23,23,23,0.08)" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 12, fill: "rgba(23,23,23,0.6)" }}
                  angle={-20}
                  textAnchor="end"
                  interval={0}
                  height={60}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fontSize: 12, fill: "rgba(23,23,23,0.6)" }}
                />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="opportunity_score" name="Action Priority" radius={[4, 4, 0, 0]}>
                  {priorityData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </FadeSlide>
      </div>

      {/* Row 2: Competitor Landscape + Method Outcomes */}
      <div className="grid grid-cols-2 gap-4">
        {/* 3. Competitor Landscape Grouped Bars */}
        <FadeSlide delay={200}>
          <div className="bg-white rounded-peec-xl shadow-peec-ring p-4">
            <h2 className="text-peec-lg font-semibold tracking-tight mb-1">
              Competitor Landscape
            </h2>
            <p className="text-peec-xs text-peec-muted mb-3">Whether competitors own the answer space for each topic.</p>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={competitorData} margin={{ top: 8, right: 8, bottom: 32, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(23,23,23,0.08)" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 12, fill: "rgba(23,23,23,0.6)" }}
                  angle={-20}
                  textAnchor="end"
                  interval={0}
                  height={60}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fontSize: 12, fill: "rgba(23,23,23,0.6)" }}
                  tickFormatter={(v: number) => `${v}%`}
                />
                <Tooltip
                  content={({ active, payload, label }: any) => {
                    if (!active || !payload?.length) return null;
                    const entry = competitorData.find((d) => d.name === label);
                    return (
                      <div className="bg-white rounded-peec-lg shadow-peec-ring p-3 text-peec-sm border border-peec-hairline">
                        <div className="font-semibold mb-1">{label}</div>
                        <div className="flex items-center gap-2">
                          <span className="w-2.5 h-2.5 rounded-full" style={{ background: BRAND_COLOR }} />
                          <span className="text-peec-muted">{data.brand_name}:</span>
                          <span className="font-medium">{entry?.brand}%</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="w-2.5 h-2.5 rounded-full" style={{ background: COMPETITOR_COLOR }} />
                          <span className="text-peec-muted">{entry?.competitorOwner ?? "Competitor"}:</span>
                          <span className="font-medium">
                            {entry?.competitor != null ? `${entry.competitor}%` : "N/A"}
                          </span>
                        </div>
                      </div>
                    );
                  }}
                />
                <Legend
                  formatter={(value: string) => (
                    <span className="text-peec-sm text-peec-muted">{value}</span>
                  )}
                />
                <Bar dataKey="brand" name={data.brand_name} fill={BRAND_COLOR} radius={[4, 4, 0, 0]} />
                <Bar dataKey="competitor" name="Competitor" fill={COMPETITOR_COLOR} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            {competitorData.some((d) => d.competitor == null) && (
              <p className="text-peec-xs text-peec-muted mt-2">
                * Missing competitor bars indicate no competitor visibility data (N/A).
              </p>
            )}
          </div>
        </FadeSlide>

        {/* 4. Gap Mix Donut */}
        <FadeSlide delay={300}>
          <div className="bg-white rounded-peec-xl shadow-peec-ring p-4">
            <h2 className="text-peec-lg font-semibold tracking-tight mb-1">
              Gap Mix
            </h2>
            <p className="text-peec-xs text-peec-muted mb-3">What type of intervention each topic needs.</p>
            {gapMixData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={gapMixData}
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={110}
                    paddingAngle={3}
                    dataKey="value"
                    nameKey="name"
                    label={({ name, value }: any) => `${name}: ${value}`}
                  >
                    {gapMixData.map((entry, idx) => (
                      <Cell key={idx} fill={GAP_MIX_COLORS[entry.name] || "rgb(0,146,184)"} />
                    ))}
                  </Pie>
                  <Tooltip
                    content={({ active, payload }: any) => {
                      if (!active || !payload?.length) return null;
                      const d = payload[0];
                      return (
                        <div className="bg-white rounded-peec-lg shadow-peec-ring p-3 text-peec-sm border border-peec-hairline">
                          <div className="flex items-center gap-2">
                            <span className="w-2.5 h-2.5 rounded-full" style={{ background: d.payload.fill }} />
                            <span className="font-semibold">{d.name}:</span>
                            <span>{d.value} {d.value === 1 ? 'topic' : 'topics'}</span>
                          </div>
                        </div>
                      );
                    }}
                  />
                  <Legend
                    formatter={(value: string) => (
                      <span className="text-peec-sm text-peec-muted">{value}</span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[300px] text-peec-muted">
                No gap data available.
              </div>
            )}
          </div>
        </FadeSlide>
      </div>

      {/* Row 3: Topic Signal Profile — full width */}
      <FadeSlide delay={350}>
        <div className="bg-white rounded-peec-xl shadow-peec-ring p-4">
          <h2 className="text-peec-lg font-semibold tracking-tight mb-1">
            Topic Signal Profile
          </h2>
          <p className="text-peec-xs text-peec-muted mb-3">
            How each topic scores across five signals. Larger area = stronger position.
          </p>
          <ResponsiveContainer width="100%" height={420}>
            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
              <PolarGrid stroke="rgba(23,23,23,0.08)" />
              <PolarAngleAxis
                dataKey="axis"
                tick={{ fontSize: 12, fill: "rgba(23,23,23,0.6)" }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 100]}
                tick={{ fontSize: 10, fill: "rgba(23,23,23,0.4)" }}
              />
              {metricsRows.map((m, idx) => (
                <Radar
                  key={m.cluster_id}
                  name={m.cluster_label}
                  dataKey={m.cluster_label}
                  stroke={RADAR_COLORS[idx % RADAR_COLORS.length]}
                  fill={RADAR_COLORS[idx % RADAR_COLORS.length]}
                  fillOpacity={0.12}
                />
              ))}
              <Legend
                formatter={(value: string) => (
                  <span className="text-peec-sm text-peec-muted">{value}</span>
                )}
              />
              <Tooltip
                content={({ active, payload, label }: any) => {
                  if (!active || !payload?.length) return null;
                  return (
                    <div className="bg-white rounded-peec-lg shadow-peec-ring p-3 text-peec-sm border border-peec-hairline">
                      <div className="font-semibold mb-1">{label}</div>
                      {payload.map((p: any) => (
                        <div key={p.dataKey} className="flex items-center gap-2">
                          <span className="w-2.5 h-2.5 rounded-full" style={{ background: p.stroke }} />
                          <span className="text-peec-muted">{p.name}:</span>
                          <span className="font-medium">{p.value}</span>
                        </div>
                      ))}
                    </div>
                  );
                }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </FadeSlide>
    </div>
  );
}
