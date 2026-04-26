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
  Legend,
} from "recharts";
import { AlertTriangle, TrendingUp, Users, Zap } from "lucide-react";

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

/* ── mocked data ────────────────────────────────────────────── */
const BRAND_LIFT_DATA = [
  { metric: "Awareness", before: 22, after: 41 },
  { metric: "Consideration", before: 14, after: 32 },
  { metric: "Preference", before: 8, after: 23 },
];

const MOCKED_CHANNEL_DEFAULTS = [
  { budget: 30, lift: "+22%", status: "Active" },
  { budget: 25, lift: "+18%", status: "Active" },
  { budget: 20, lift: "+15%", status: "Planned" },
  { budget: 15, lift: "+12%", status: "Planned" },
  { budget: 10, lift: "+8%", status: "On Hold" },
];

const JOURNEY_STAGES_FALLBACK = ["Awareness", "Consideration", "Comparison", "Purchase"];

function generateAudienceCards(segments: string[], stages: string[]) {
  const scores = [78, 62, 55, 43, 85, 71, 48, 66];
  const actions = [
    "Amplify design narrative in tech media",
    "Seed comparison content on YouTube",
    "Strengthen ecosystem integration messaging",
    "Increase review volume on Reddit",
    "Partner with minimalist lifestyle creators",
    "Expand presence in audio-focused channels",
    "Target with aspirational brand positioning",
    "Drive hands-on demo content",
  ];
  return segments.map((segment, i) => ({
    name: segment,
    engagementScore: scores[i % scores.length],
    stage: stages[i % stages.length],
    action: actions[i % actions.length],
  }));
}

/* ── tooltip ────────────────────────────────────────────────── */
function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white rounded-peec-lg shadow-peec-ring p-3 text-peec-sm border border-peec-hairline">
      <div className="font-semibold mb-1">{label}</div>
      {payload.map((p: any) => (
        <div key={p.dataKey} className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full" style={{ background: p.fill || p.color }} />
          <span className="text-peec-muted">{p.name}:</span>
          <span className="font-medium">{p.value}%</span>
        </div>
      ))}
    </div>
  );
}

const STATUS_STYLE: Record<string, { bg: string; text: string }> = {
  Active: { bg: "bg-pill-green-bg", text: "text-pill-green" },
  Planned: { bg: "bg-pill-indigo-bg", text: "text-pill-indigo" },
  "On Hold": { bg: "bg-pill-orange-bg", text: "text-pill-orange" },
};

export default function FuturePage() {
  const { data, config, loading } = useBrand();

  if (loading || !data) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-peec-tint rounded animate-pulse" />
        <div className="h-16 bg-amber-50 rounded-peec-xl animate-pulse" />
        <ChartSkeleton height={340} />
        <ChartSkeleton height={200} />
        <div className="grid grid-cols-2 gap-4">
          <ChartSkeleton height={160} />
          <ChartSkeleton height={160} />
        </div>
      </div>
    );
  }

  const segments = config?.audience_segments ?? ["General Audience", "Tech Enthusiasts", "Design Seekers"];
  const stages = config?.buying_journey_stages ?? JOURNEY_STAGES_FALLBACK;
  const channels = config?.channels_to_activate ?? ["editorial", "owned", "youtube", "reddit", "paid_search"];
  const audienceCards = generateAudienceCards(segments, stages);

  const channelData = channels.slice(0, 5).map((ch, i) => ({
    channel: ch.charAt(0).toUpperCase() + ch.slice(1).replace(/_/g, " "),
    budget: MOCKED_CHANNEL_DEFAULTS[i]?.budget ?? 10 + i * 5,
    lift: MOCKED_CHANNEL_DEFAULTS[i]?.lift ?? `+${10 + i * 3}%`,
    status: MOCKED_CHANNEL_DEFAULTS[i]?.status ?? "Planned",
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <span className="inline-flex items-center px-2 py-0.5 rounded-peec-md text-peec-sm font-medium bg-pill-purple-bg text-pill-purple mb-2">
          Future Directions
        </span>
        <h1 className="text-2xl font-semibold tracking-tight">
          {data.brand_name} — Future Directions
        </h1>
        <p className="text-peec-muted mt-1 max-w-2xl">
          Illustrative previews of brand lift, channel optimization, and audience engagement modeling.
        </p>
      </div>

      {/* Mocked Data Banner */}
      <div className="flex items-start gap-3 bg-amber-50 border border-amber-300/50 rounded-peec-xl p-4">
        <AlertTriangle size={20} className="text-amber-600 mt-0.5 shrink-0" />
        <div>
          <div className="font-semibold text-amber-800">
            Illustrative preview — industry benchmark methodology
          </div>
          <div className="text-peec-sm text-amber-700 mt-0.5">
            All numbers below are modeled, not measured. These projections use industry benchmark
            ratios applied to the current visibility data and are intended to show what a full
            analytics suite would deliver.
          </div>
        </div>
      </div>

      {/* Section 1: Brand Lift Preview */}
      <FadeSlide delay={0}>
        <div className="bg-white rounded-peec-xl shadow-peec-ring p-4 space-y-4">
          <div className="flex items-center gap-2">
            <TrendingUp size={18} className="text-pill-indigo" />
            <h2 className="text-peec-lg font-semibold tracking-tight">
              Projected Brand Lift
            </h2>
          </div>
          <p className="text-peec-sm text-peec-muted">
            Before vs. After for three key brand metrics. Based on industry benchmark methodology.
          </p>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={BRAND_LIFT_DATA} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(23,23,23,0.08)" />
              <XAxis
                dataKey="metric"
                tick={{ fontSize: 13, fill: "rgba(23,23,23,0.6)" }}
              />
              <YAxis
                domain={[0, 50]}
                tick={{ fontSize: 12, fill: "rgba(23,23,23,0.6)" }}
                tickFormatter={(v: number) => `${v}%`}
              />
              <Tooltip content={<ChartTooltip />} />
              <Legend
                formatter={(value: string) => (
                  <span className="text-peec-sm text-peec-muted">{value}</span>
                )}
              />
              <Bar dataKey="before" name="Current" fill="rgba(23,23,23,0.15)" radius={[4, 4, 0, 0]} />
              <Bar dataKey="after" name="Projected (+Rx)" fill="rgb(79,70,229)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <p className="text-peec-xs text-peec-muted italic">
            Based on industry benchmark methodology. Actual results depend on execution, media mix, and market conditions.
          </p>
        </div>
      </FadeSlide>

      {/* Section 2: Channel Optimizer */}
      <FadeSlide delay={150}>
        <div className="bg-white rounded-peec-xl shadow-peec-ring p-4 space-y-4">
          <div className="flex items-center gap-2">
            <Zap size={18} className="text-pill-orange" />
            <h2 className="text-peec-lg font-semibold tracking-tight">
              Illustrative Channel Allocation
            </h2>
          </div>
          <p className="text-peec-sm text-peec-muted">
            Illustrative allocation based on gap-type intervention priorities.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-peec-sm">
              <thead>
                <tr className="border-b border-peec-hairline">
                  <th className="text-left py-2 px-3 font-semibold text-peec-muted">Channel</th>
                  <th className="text-right py-2 px-3 font-semibold text-peec-muted">Budget %</th>
                  <th className="text-right py-2 px-3 font-semibold text-peec-muted">Expected Lift</th>
                  <th className="text-left py-2 px-3 font-semibold text-peec-muted">Status</th>
                </tr>
              </thead>
              <tbody>
                {channelData.map((row) => {
                  const style = STATUS_STYLE[row.status] ?? { bg: "bg-pill-cyan-bg", text: "text-pill-cyan" };
                  return (
                    <tr key={row.channel} className="border-b border-peec-hairline last:border-0 hover:bg-peec-tint transition-colors">
                      <td className="py-2.5 px-3 font-medium">{row.channel}</td>
                      <td className="py-2.5 px-3 text-right tabular-nums">{row.budget}%</td>
                      <td className="py-2.5 px-3 text-right tabular-nums font-medium text-pill-green">{row.lift}</td>
                      <td className="py-2.5 px-3">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-peec-md text-peec-xs font-medium ${style.bg} ${style.text}`}>
                          {row.status}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="text-peec-xs text-peec-muted italic">
            Illustrative allocation based on gap-type intervention priorities. Actual budget depends on client objectives.
          </p>
        </div>
      </FadeSlide>

      {/* Section 3: Audience Engine */}
      <FadeSlide delay={300}>
        <div className="bg-white rounded-peec-xl shadow-peec-ring p-4 space-y-4">
          <div className="flex items-center gap-2">
            <Users size={18} className="text-pill-cyan" />
            <h2 className="text-peec-lg font-semibold tracking-tight">
              Audience Engagement Signals
            </h2>
          </div>
          <p className="text-peec-sm text-peec-muted">
            Based on audience affinity modeling.
          </p>
          <div className="grid grid-cols-2 gap-3">
            {audienceCards.map((card) => (
              <div
                key={card.name}
                className="bg-peec-tint rounded-peec-xl p-4 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-sm capitalize">{card.name}</h3>
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-semibold"
                    style={{
                      background:
                        card.engagementScore >= 70
                          ? "rgb(22,163,74)"
                          : card.engagementScore >= 50
                            ? "rgb(234,88,12)"
                            : "#FB2C36",
                    }}
                  >
                    {card.engagementScore}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-peec-sm">
                  <div>
                    <div className="text-peec-xs text-peec-muted">Engagement Score</div>
                    <div className="font-semibold">{card.engagementScore}/100</div>
                  </div>
                  <div>
                    <div className="text-peec-xs text-peec-muted">Journey Stage</div>
                    <div className="font-medium capitalize">{card.stage}</div>
                  </div>
                </div>
                <div className="text-peec-sm">
                  <div className="text-peec-xs text-peec-muted mb-0.5">Recommended Action</div>
                  <div className="text-peec-fg">{card.action}</div>
                </div>
              </div>
            ))}
          </div>
          <p className="text-peec-xs text-peec-muted italic">
            Based on audience affinity modeling. Engagement scores are illustrative and not derived from measurement data.
          </p>
        </div>
      </FadeSlide>
    </div>
  );
}
