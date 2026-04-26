"use client";

import { useBrand } from "@/hooks/useBrand";
import { ChartSkeleton } from "@/components/charts/ChartSkeleton";
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

/* ── colour map (raw hex for Recharts) ──────────────────────── */
const GAP_COLORS: Record<string, string> = {
  perception: "#FB2C36",
  indexing: "rgb(234,88,12)",
  volume_frequency: "rgb(124,58,237)",
};
const STRONGHOLD_COLOR = "rgb(22,163,74)";
const BRAND_COLOR = "rgb(22,163,74)";
const COMPETITOR_COLOR = "#FB2C36";
const PIE_COLORS = [STRONGHOLD_COLOR, "rgb(234,88,12)", "rgb(124,58,237)", "rgb(0,146,184)"];
const RADAR_COLORS = [
  "rgb(79,70,229)",
  "#FB2C36",
  "rgb(234,88,12)",
  "rgb(124,58,237)",
  "rgb(0,146,184)",
];

function barColor(gapType: string | null): string {
  return gapType ? GAP_COLORS[gapType] ?? "rgb(0,146,184)" : STRONGHOLD_COLOR;
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
  const classificationSummary = data.classification?.summary ?? {};

  // 1. Visibility bar chart data
  const visData = rows.map((r) => ({
    name: r.cluster_label,
    visibility: Math.round((r.visibility_target_share ?? 0) * 100),
    fill: barColor(r.gap_type),
    gapType: r.gap_type,
  }));

  // 2. Action priority bar chart data
  const priorityData = metricsRows.map((m) => ({
    name: m.cluster_label,
    opportunity_score: m.opportunity_score,
    fill: barColor(m.gap_type),
  }));

  // 3. Competitor landscape data
  const competitorData = landscape.map((t) => ({
    name: t.cluster_label,
    brand: Math.round((t.target_visibility_share ?? 0) * 100),
    competitor: t.competitor_visibility_share != null ? Math.round(t.competitor_visibility_share * 100) : null,
    competitorOwner: t.competitor_owner,
  }));

  // 4. Method outcomes donut data
  const outcomesRaw: Record<string, number> = {
    confirmed: (classificationSummary as Record<string, number>).confirmed ?? 0,
    provisional: (classificationSummary as Record<string, number>).provisional ?? 0,
    conflicted: (classificationSummary as Record<string, number>).conflicted ?? 0,
    insufficient: (classificationSummary as Record<string, number>).insufficient ?? 0,
  };
  const outcomesData = Object.entries(outcomesRaw)
    .filter(([, v]) => v > 0)
    .map(([key, value]) => ({ name: key.charAt(0).toUpperCase() + key.slice(1), value }));

  // 5. Radar chart data
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

  // Legend items for gap types
  const legendItems = [
    { label: "Stronghold", color: STRONGHOLD_COLOR },
    { label: "Perception", color: GAP_COLORS.perception },
    { label: "Discovery", color: GAP_COLORS.indexing },
    { label: "Attention", color: GAP_COLORS.volume_frequency },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <span className="inline-flex items-center px-2 py-0.5 rounded-peec-md text-peec-sm font-medium bg-pill-indigo-bg text-pill-indigo mb-2">
          Analytics
        </span>
        <h1 className="text-2xl font-semibold tracking-tight">
          {data.brand_name} — Visual Analytics
        </h1>
        <p className="text-peec-muted mt-1 max-w-2xl">
          Interactive charts showing visibility distribution, action priorities, competitive landscape, and classification outcomes.
        </p>
      </div>

      {/* Gap type legend */}
      <div className="flex items-center gap-4 text-peec-sm">
        {legendItems.map((item) => (
          <div key={item.label} className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full" style={{ background: item.color }} />
            <span className="text-peec-muted">{item.label}</span>
          </div>
        ))}
      </div>

      {/* Row 1: Visibility + Action Priority */}
      <div className="grid grid-cols-2 gap-4">
        {/* 1. Visibility Bar Chart */}
        <FadeSlide delay={0}>
          <div className="bg-white rounded-peec-xl shadow-peec-ring p-4">
            <h2 className="text-peec-lg font-semibold tracking-tight mb-4">
              Visibility by Topic
            </h2>
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
            <h2 className="text-peec-lg font-semibold tracking-tight mb-4">
              Action Priority Score
            </h2>
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
            <h2 className="text-peec-lg font-semibold tracking-tight mb-4">
              Competitor Landscape
            </h2>
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

        {/* 4. Method Outcomes Donut */}
        <FadeSlide delay={300}>
          <div className="bg-white rounded-peec-xl shadow-peec-ring p-4">
            <h2 className="text-peec-lg font-semibold tracking-tight mb-4">
              Classification Outcomes
            </h2>
            {outcomesData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={outcomesData}
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={110}
                    paddingAngle={3}
                    dataKey="value"
                    nameKey="name"
                    label={({ name, value }: any) => `${name}: ${value}`}
                  >
                    {outcomesData.map((_, idx) => (
                      <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
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
                            <span>{d.value}</span>
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
                No classification data available.
              </div>
            )}
          </div>
        </FadeSlide>
      </div>

      {/* Row 3: Radar Chart — full width */}
      <FadeSlide delay={400}>
        <div className="bg-white rounded-peec-xl shadow-peec-ring p-4">
          <h2 className="text-peec-lg font-semibold tracking-tight mb-4">
            Multi-Axis Comparison
          </h2>
          <p className="text-peec-sm text-peec-muted mb-4">
            Five axes: Intent Fit, Citation Authority, Evidence Coverage, Signal Alignment, Action Priority. One polygon per topic.
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
