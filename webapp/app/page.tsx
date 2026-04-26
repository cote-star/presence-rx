"use client";

import { useBrand } from "@/hooks/useBrand";
import { humanGapType, humanDecision, gapTypeColor, humanStrategicStatus, strategicStatusColor, strategicStatusBgColor } from "@/lib/display-labels";
import {
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Shield,
  Target,
  Newspaper,
  MessageSquare,
  Globe,
  Video,
  Users,
} from "lucide-react";
import { useState } from "react";
import { TermTooltip } from "@/components/interactive/TermTooltip";

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
      <div className="flex items-center text-peec-xs text-peec-muted font-medium">
        {label}
        <TermTooltip term={label} />
      </div>
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
  const [showNonPriority, setShowNonPriority] = useState(false);
  const [expandedChannel, setExpandedChannel] = useState<string | null>(null);
  const [expandedAudience, setExpandedAudience] = useState<string | null>(null);

  if (loading || !data) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-64 bg-peec-tint rounded animate-pulse" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
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
  const activeGaps = rows.filter((r) => r.gap_type && (r.desired_association ?? true));
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

  // Group blind spots by gap type, separating non-priority
  const gapGroups: Record<string, typeof rows> = {};
  const nonPriorityRows: typeof rows = [];
  blindSpots.forEach((r) => {
    if (!(r.desired_association ?? true)) {
      nonPriorityRows.push(r);
    } else {
      const key = r.gap_type!;
      (gapGroups[key] = gapGroups[key] || []).push(r);
    }
  });

  // Channel profiles for "Where to Engage" cards
  const CHANNEL_PROFILES: Record<string, { bestFor: string; why: string; play: string; icon: typeof Newspaper }> = {
    editorial: {
      bestFor: "Perception + Attention",
      why: "AI answers cite reviewers and comparison pages.",
      play: "Pitch product proof points to review lists and comparison articles.",
      icon: Newspaper,
    },
    ugc: {
      bestFor: "Attention + Discovery",
      why: "AI models weight community discussion and authentic user content.",
      play: "Seed authentic content on forums and social platforms.",
      icon: MessageSquare,
    },
    owned: {
      bestFor: "Discovery + Perception",
      why: "Structured data on owned properties helps AI retrieval and citation.",
      play: "Strengthen schema markup and product page structured data.",
      icon: Globe,
    },
    youtube: {
      bestFor: "Perception + Attention",
      why: "Video content influences AI training data and citation patterns.",
      play: "Partner with category-relevant creators for product deep dives.",
      icon: Video,
    },
    reddit: {
      bestFor: "Attention + Discovery",
      why: "Reddit threads are heavily cited in AI-generated answers.",
      play: "Monitor and participate in relevant subreddit discussions.",
      icon: MessageSquare,
    },
  };

  // Audience profiles for "Who to Reach" cards
  const AUDIENCE_PROFILES: Record<string, { messageAngle: string; topics: string[]; channels: string[]; claimBoundary: string }> = {
    "design-conscious buyers": {
      messageAngle: "Distinctive transparent minimalism",
      topics: ["Minimalist Hardware", "Smartphone Design"],
      channels: ["editorial", "youtube"],
      claimBoundary: "Distinctive alternative, not category leader",
    },
    "tech enthusiasts": {
      messageAngle: "Innovation-first ecosystem thinking",
      topics: ["Consumer Tech Innovation", "Mobile Ecosystem"],
      channels: ["youtube", "reddit", "ugc"],
      claimBoundary: "Innovative challenger, not market dominant",
    },
    "Android switchers": {
      messageAngle: "A refreshing alternative with unique design language",
      topics: ["Mobile Ecosystem", "Consumer Tech Innovation"],
      channels: ["reddit", "editorial"],
      claimBoundary: "Best design-forward Android option, not best spec sheet",
    },
    "minimalism seekers": {
      messageAngle: "Technology that disappears into your life",
      topics: ["Minimalist Hardware", "Wireless Audio"],
      channels: ["owned", "editorial"],
      claimBoundary: "Most intentional design philosophy, not most features",
    },
  };

  // Count topics per channel based on gap types (map gap type to best channels)
  const GAP_CHANNEL_MAP: Record<string, string[]> = {
    perception: ["editorial", "youtube", "owned"],
    indexing: ["owned", "ugc", "reddit"],
    volume_frequency: ["ugc", "youtube", "reddit"],
  };
  const channelTopicCounts: Record<string, number> = {};
  activeGaps.forEach((r) => {
    const channels = GAP_CHANNEL_MAP[r.gap_type!] ?? [];
    channels.forEach((ch) => {
      channelTopicCounts[ch] = (channelTopicCounts[ch] || 0) + 1;
    });
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
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
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
          value={`${confirmed} / ${activeGaps.length}`}
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
      {["indexing", "perception", "volume_frequency"].map((gapType) => {
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
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
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
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold">{row.cluster_label}</h3>
                        {(row.strategic_status ?? null) && (
                          <span className={`px-2 py-0.5 rounded-peec-md text-peec-sm font-medium bg-${strategicStatusBgColor(row.strategic_status)} text-${strategicStatusColor(row.strategic_status)}`}>
                            {humanStrategicStatus(row.strategic_status)}
                          </span>
                        )}
                      </div>
                      <span className="px-2 py-0.5 rounded-peec-md text-peec-sm font-medium bg-pill-green-bg text-pill-green">
                        {humanDecision(m?.decision_bucket ?? "monitor")}
                      </span>
                    </div>
                    {row.strategic_note && (
                      <p className="text-peec-xs text-peec-muted italic">{row.strategic_note}</p>
                    )}
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      <div className="bg-peec-tint rounded-peec-lg p-2">
                        <div className="flex items-center text-peec-xs text-peec-muted">
                          Action Priority
                          <TermTooltip term="Action Priority" />
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
                        <div className="flex items-center text-peec-xs text-peec-muted">
                          Owner
                          <TermTooltip term="Owner" />
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

      {/* Non-Priority Topics (collapsed) */}
      {nonPriorityRows.length > 0 && (
        <div className="space-y-3">
          <button
            onClick={() => setShowNonPriority(!showNonPriority)}
            className="flex items-center gap-2 pb-2 border-b border-peec-hairline w-full text-left"
          >
            <ChevronDown
              size={16}
              className={`text-peec-muted transition-transform ${showNonPriority ? "rotate-0" : "-rotate-90"}`}
            />
            <h2 className="text-peec-lg font-semibold tracking-tight text-gray-400">
              Non-Priority Topics ({nonPriorityRows.length})
            </h2>
          </button>
          {showNonPriority && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {nonPriorityRows.map((row) => {
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
                    className="bg-white rounded-peec-xl shadow-peec-ring p-4 space-y-3 opacity-50"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-gray-400">{row.cluster_label}</h3>
                        <span className="px-2 py-0.5 rounded-peec-md text-peec-sm font-medium bg-gray-100 text-gray-400">
                          Non-Priority
                        </span>
                      </div>
                      <span className="px-2 py-0.5 rounded-peec-md text-peec-sm font-medium bg-pill-green-bg text-pill-green">
                        {humanDecision(m?.decision_bucket ?? "monitor")}
                      </span>
                    </div>
                    {row.strategic_note && (
                      <p className="text-peec-xs text-peec-muted italic">{row.strategic_note}</p>
                    )}
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      <div className="bg-peec-tint rounded-peec-lg p-2">
                        <div className="flex items-center text-peec-xs text-peec-muted">
                          Action Priority
                          <TermTooltip term="Action Priority" />
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
                        <div className="flex items-center text-peec-xs text-peec-muted">
                          Owner
                          <TermTooltip term="Owner" />
                        </div>
                        <div className="font-semibold text-sm truncate">
                          {competitor}
                        </div>
                      </div>
                    </div>
                    <div className="text-peec-sm text-gray-400">
                      <strong>Next move:</strong>{" "}
                      {m?.recommended_next_move ?? "Monitor this cluster."}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

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
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {config.channels_to_activate.map((channel) => {
              const profile = CHANNEL_PROFILES[channel];
              const Icon = profile?.icon ?? Globe;
              const topicCount = channelTopicCounts[channel] ?? 0;
              const isExpanded = expandedChannel === channel;
              return (
                <div key={channel}>
                  <button
                    onClick={() => setExpandedChannel(isExpanded ? null : channel)}
                    className={`w-full text-left bg-peec-tint rounded-peec-lg p-4 space-y-2 transition-all hover:shadow-peec-ring ${
                      isExpanded ? "ring-2 ring-pill-indigo" : ""
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Icon size={16} className="text-pill-indigo" />
                        <span className="font-semibold text-sm capitalize">
                          {channel.replace(/_/g, " ")}
                        </span>
                      </div>
                      <ChevronRight
                        size={14}
                        className={`text-peec-muted transition-transform ${isExpanded ? "rotate-90" : ""}`}
                      />
                    </div>
                    {profile && (
                      <>
                        <div className="text-peec-xs text-peec-muted">
                          Best for: <span className="font-medium text-peec-fg">{profile.bestFor}</span>
                        </div>
                        {topicCount > 0 && (
                          <div className="text-peec-xs text-pill-indigo font-medium">
                            {topicCount} linked {topicCount === 1 ? "topic" : "topics"}
                          </div>
                        )}
                      </>
                    )}
                  </button>
                  {isExpanded && profile && (
                    <div className="mt-2 bg-white border border-peec-hairline rounded-peec-lg p-4 space-y-2 animate-in slide-in-from-top-1 duration-200">
                      <div className="text-peec-sm">
                        <span className="font-semibold">Why:</span>{" "}
                        {profile.why}
                      </div>
                      <div className="text-peec-sm">
                        <span className="font-semibold">Recommended play:</span>{" "}
                        {profile.play}
                      </div>
                      {activeGaps.filter((r) => (GAP_CHANNEL_MAP[r.gap_type!] ?? []).includes(channel)).length > 0 && (
                        <div className="text-peec-sm">
                          <span className="font-semibold">Target topics:</span>{" "}
                          {activeGaps
                            .filter((r) => (GAP_CHANNEL_MAP[r.gap_type!] ?? []).includes(channel))
                            .map((r) => r.cluster_label)
                            .join(", ")}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Audience Segments */}
      {config && config.audience_segments.length > 0 && (
        <div className="bg-white rounded-peec-xl shadow-peec-ring p-4 space-y-3">
          <h2 className="text-peec-lg font-semibold tracking-tight">
            Who to Reach
          </h2>
          <p className="text-peec-sm text-peec-muted">
            Target audience segments and how to engage them based on gap analysis.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {config.audience_segments.map((segment) => {
              const profile = AUDIENCE_PROFILES[segment];
              const isExpanded = expandedAudience === segment;
              return (
                <div key={segment}>
                  <button
                    onClick={() => setExpandedAudience(isExpanded ? null : segment)}
                    className={`w-full text-left bg-peec-tint rounded-peec-lg p-3 flex items-center gap-3 transition-all hover:shadow-peec-ring ${
                      isExpanded ? "ring-2 ring-pill-indigo" : ""
                    }`}
                  >
                    <Users size={18} className="text-pill-indigo shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm capitalize">
                        {segment}
                      </div>
                      {profile ? (
                        <div className="text-peec-xs text-peec-muted truncate">
                          {profile.messageAngle}
                        </div>
                      ) : (
                        <div className="text-peec-xs text-peec-muted">
                          {config.buying_journey_stages.join(" → ")}
                        </div>
                      )}
                    </div>
                    <ChevronRight
                      size={14}
                      className={`text-peec-muted transition-transform shrink-0 ${isExpanded ? "rotate-90" : ""}`}
                    />
                  </button>
                  {isExpanded && profile && (
                    <div className="mt-2 bg-white border border-peec-hairline rounded-peec-lg p-4 space-y-2 animate-in slide-in-from-top-1 duration-200">
                      <div className="text-peec-sm">
                        <span className="font-semibold">Message angle:</span>{" "}
                        {profile.messageAngle}
                      </div>
                      <div className="text-peec-sm">
                        <span className="font-semibold">Relevant topics:</span>{" "}
                        {profile.topics.join(", ")}
                      </div>
                      <div className="text-peec-sm">
                        <span className="font-semibold">Channels to use:</span>{" "}
                        {profile.channels.map((c) => c.replace(/_/g, " ")).join(", ")}
                      </div>
                      <div className="text-peec-sm">
                        <span className="font-semibold">Claim boundary:</span>{" "}
                        <span className="text-peec-muted">{profile.claimBoundary}</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
