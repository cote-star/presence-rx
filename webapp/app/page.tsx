"use client";

import { useBrand } from "@/hooks/useBrand";
import { humanGapType, humanDecision, gapTypeColor } from "@/lib/display-labels";
import {
  AlertTriangle,
  ArrowRight,
  Shield,
  Target,
  TrendingUp,
} from "lucide-react";

function MetricCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string;
  sub: string;
}) {
  return (
    <div className="bg-white rounded-peec-xl shadow-peec-ring p-4 flex flex-col justify-between min-h-[112px]">
      <div className="text-peec-xs text-peec-muted font-medium">{label}</div>
      <div>
        <div className="text-2xl font-semibold tracking-tight tabular-nums">
          {value}
        </div>
        <div className="text-peec-xs text-peec-muted">{sub}</div>
      </div>
    </div>
  );
}

function Pill({
  children,
  color = "peec-tint",
  textColor = "peec-muted",
}: {
  children: React.ReactNode;
  color?: string;
  textColor?: string;
}) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-peec-md text-peec-sm font-medium bg-${color} text-${textColor}`}
    >
      {children}
    </span>
  );
}

export default function ActionBriefPage() {
  const { data, config, loading } = useBrand();

  if (loading || !data) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-64 bg-peec-tint rounded animate-pulse" />
        <div className="grid grid-cols-5 gap-3">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="h-28 bg-peec-tint rounded-peec-xl animate-pulse"
            />
          ))}
        </div>
        <div className="h-64 bg-peec-tint rounded-peec-xl animate-pulse" />
      </div>
    );
  }

  const rows = data.study.rows;
  const blindSpots = rows.filter((r) => r.gap_type);
  const strongholds = rows.filter((r) => !r.gap_type);
  const metrics = data.metrics?.rows ?? [];
  const metricsMap = Object.fromEntries(metrics.map((m) => [m.cluster_id, m]));
  const landscape = data.landscape?.topics ?? [];
  const landscapeMap = Object.fromEntries(landscape.map((l) => [l.cluster_id, l]));
  const claims = data.ledger?.claims ?? [];
  const blockedClaims = data.ledger?.blocked_claims ?? [];
  const classified = data.classification?.classified_gaps ?? [];
  const avgOpp = data.metrics?.summary?.average_opportunity_score ?? 0;
  const tavilySources = data.tavily?.summary?.sources ?? 0;
  const confirmed = classified.filter(
    (g) => g.classification_status === "confirmed"
  ).length;
  const availableMethods = new Set<string>();
  classified.forEach((g) =>
    g.method_signals.forEach((s) => {
      if (s.signal !== "unavailable") availableMethods.add(s.method);
    })
  );
  const methodCount = availableMethods.size || 1;

  const avgVis = rows.length
    ? Math.round(
        (rows.reduce((a, r) => a + (r.visibility_target_share ?? 0), 0) /
          rows.length) *
          100
      )
    : 0;
  const avgPos = rows.length
    ? (
        rows.reduce(
          (a, r) => a + (r.visibility_target_avg_position ?? 0),
          0
        ) / rows.length
      ).toFixed(1)
    : "0";

  // Group blind spots by gap type
  const gapGroups: Record<string, typeof rows> = {};
  blindSpots.forEach((r) => {
    const key = r.gap_type!;
    (gapGroups[key] = gapGroups[key] || []).push(r);
  });

  const INTERVENTION: Record<string, string> = {
    perception:
      "Positioning + messaging correction; reframing content with explicit trait language",
    indexing:
      "Schema markup, structured data, AI-citation optimization, source-of-truth canonicalization",
    volume_frequency:
      "Content creation + distribution + amplification; sustained editorial outreach; UGC seeding",
  };

  return (
    <div className="space-y-6">
      {/* Hero */}
      <div className="flex items-start justify-between gap-8">
        <div>
          <span className="inline-flex items-center px-2 py-0.5 rounded-peec-md text-peec-sm font-medium bg-pill-green-bg text-pill-green mb-2">
            Presence Verdict
          </span>
          <h1 className="text-2xl font-semibold tracking-tight">
            {data.brand_name} — AI Visibility Diagnosis
          </h1>
          <p className="text-peec-muted mt-1 max-w-2xl">
            {config?.known_market_tension ||
              `${data.brand_name} visibility analysis across ${rows.length} topics and ${methodCount} independent methods.`}
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-5 gap-3">
        <MetricCard
          label="Avg visibility"
          value={`${avgVis}%`}
          sub={`${rows.length} topics tracked`}
        />
        <MetricCard
          label="Avg position"
          value={avgPos}
          sub={Number(avgPos) <= 2.0 ? "Near top when mentioned" : "Room to improve"}
        />
        <MetricCard
          label="Confirmed gaps"
          value={`${confirmed} / ${blindSpots.length}`}
          sub={`${methodCount}-method classifier`}
        />
        <MetricCard
          label="Claims to avoid"
          value={String(blockedClaims.length)}
          sub="Ownership overclaims"
        />
        <MetricCard
          label="Avg action priority"
          value={String(avgOpp)}
          sub="0 to 100 score"
        />
      </div>

      {/* Blocked Claims Banner */}
      {blockedClaims.length > 0 ? (
        <div className="bg-pill-red-bg border border-pill-red/20 rounded-peec-xl p-4 space-y-3">
          <div className="flex items-center gap-2 text-pill-red font-semibold">
            <AlertTriangle size={18} />
            Claims To Avoid ({blockedClaims.length})
          </div>
          {blockedClaims.map((bc) => (
            <div
              key={bc.claim_id}
              className="bg-white rounded-peec-lg p-3 border-l-3 border-pill-red"
            >
              <div className="font-medium text-sm">{bc.claim}</div>
              <div className="text-peec-muted text-peec-sm mt-1">
                <Shield size={14} className="inline mr-1" />
                {bc.safe_rewrite}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-pill-green-bg border border-pill-green/20 rounded-peec-xl p-4 flex items-center gap-2 text-pill-green font-medium">
          <Shield size={18} />
          All clear — no blocked claims. All gap classifications confirmed.
        </div>
      )}

      {/* Action Cards by Gap Type */}
      {["perception", "indexing", "volume_frequency"].map((gapType) => {
        const gapRows = gapGroups[gapType];
        if (!gapRows) return null;
        return (
          <div key={gapType} className="space-y-3">
            <div className="flex items-center gap-2 pb-2 border-b border-peec-hairline">
              <h2 className="text-peec-lg font-semibold tracking-tight">
                {humanGapType(gapType)} Gaps
              </h2>
              <span
                className={`px-2 py-0.5 rounded-peec-md text-peec-sm font-medium bg-${
                  gapType === "perception"
                    ? "pill-red-bg"
                    : gapType === "indexing"
                      ? "pill-orange-bg"
                      : "pill-purple-bg"
                } text-${
                  gapType === "perception"
                    ? "pill-red"
                    : gapType === "indexing"
                      ? "pill-orange"
                      : "pill-purple"
                }`}
              >
                {humanGapType(gapType)}
              </span>
            </div>
            <p className="text-peec-sm text-peec-muted">
              <strong>Intervention:</strong> {INTERVENTION[gapType]}
            </p>
            <div className="grid grid-cols-2 gap-3">
              {gapRows.map((row) => {
                const m = metricsMap[row.cluster_id];
                const l = landscapeMap[row.cluster_id];
                const competitor =
                  l?.competitor_owner ?? row.visibility_competitor_owner ?? "N/A";
                const vis = Math.round(
                  (row.visibility_target_share ?? 0) * 100
                );

                return (
                  <div
                    key={row.cluster_id}
                    className="bg-white rounded-peec-xl shadow-peec-ring p-4 space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold">{row.cluster_label}</h3>
                      <span className="px-2 py-0.5 rounded-peec-md text-peec-sm font-medium bg-pill-green-bg text-pill-green">
                        {humanDecision(m?.decision_bucket ?? "monitor")}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                      <div className="bg-peec-tint rounded-peec-lg p-2">
                        <div className="text-peec-xs text-peec-muted">
                          Action Priority
                        </div>
                        <div className="font-semibold text-lg">
                          {m?.opportunity_score ?? 0}
                        </div>
                      </div>
                      <div className="bg-peec-tint rounded-peec-lg p-2">
                        <div className="text-peec-xs text-peec-muted">
                          {data.brand_name}
                        </div>
                        <div className="font-semibold text-lg">{vis}%</div>
                      </div>
                      <div className="bg-peec-tint rounded-peec-lg p-2">
                        <div className="text-peec-xs text-peec-muted">
                          Owner
                        </div>
                        <div className="font-semibold text-sm truncate">
                          {competitor}
                        </div>
                      </div>
                    </div>
                    <div className="text-peec-sm">
                      <strong>Next move:</strong>{" "}
                      {m?.recommended_next_move ?? "Monitor this cluster."}
                    </div>
                    {claims.find((c) => c.cluster_id === row.cluster_id) && (
                      <div className="text-peec-sm text-peec-muted">
                        <Target size={14} className="inline mr-1" />
                        {
                          claims.find((c) => c.cluster_id === row.cluster_id)!
                            .publication_language
                        }
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}

      {/* Influence Map — Where to Engage */}
      {config && (
        <div className="bg-white rounded-peec-xl shadow-peec-ring p-4 space-y-3">
          <h2 className="text-peec-lg font-semibold tracking-tight">
            Where to Engage
          </h2>
          <p className="text-peec-sm text-peec-muted">
            Channels to activate for {data.brand_name} based on gap analysis and
            brand configuration.
          </p>
          <div className="grid grid-cols-5 gap-2">
            {config.channels_to_activate.map((channel) => (
              <div
                key={channel}
                className="bg-peec-tint rounded-peec-lg p-3 text-center"
              >
                <div className="font-medium text-sm capitalize">
                  {channel.replace(/_/g, " ")}
                </div>
                <div className="text-peec-xs text-peec-muted mt-1">
                  {blindSpots.length} gaps
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Audience Segments */}
      {config && config.audience_segments.length > 0 && (
        <div className="bg-white rounded-peec-xl shadow-peec-ring p-4 space-y-3">
          <h2 className="text-peec-lg font-semibold tracking-tight">
            Who to Reach
          </h2>
          <div className="grid grid-cols-2 gap-3">
            {config.audience_segments.map((segment) => (
              <div
                key={segment}
                className="bg-peec-tint rounded-peec-lg p-3 flex items-center gap-3"
              >
                <TrendingUp size={18} className="text-pill-indigo" />
                <div>
                  <div className="font-medium text-sm capitalize">
                    {segment}
                  </div>
                  <div className="text-peec-xs text-peec-muted">
                    {config.buying_journey_stages.join(" → ")}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
