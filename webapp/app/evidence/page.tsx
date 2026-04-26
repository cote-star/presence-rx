"use client";

import { useState } from "react";
import { useBrand } from "@/hooks/useBrand";
import { humanGapType, gapTypeColor, gapTypeBgColor } from "@/lib/display-labels";
import { ClaimSimulator } from "@/components/interactive/ClaimSimulator";
import { FileCheck, ArrowUpRight, ShieldOff, Beaker, Search, Eye } from "lucide-react";
import { TermTooltip } from "@/components/interactive/TermTooltip";

function MetricCard({
  label,
  value,
  sub,
  icon: Icon,
}: {
  label: string;
  value: string;
  sub: string;
  icon: typeof FileCheck;
}) {
  return (
    <div className="bg-white rounded-peec-xl shadow-peec-ring p-4 flex flex-col justify-between min-h-[112px]">
      <div className="flex items-center gap-1.5 text-peec-xs text-peec-muted font-medium">
        <Icon size={12} />
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

/** Clean up internal claim text for display */
function cleanClaimText(text: string): string {
  return text
    .replace(/\ba indexing\b/gi, "an indexing")
    .replace(/volume_frequency/g, "volume / frequency")
    .replace(/\bpartner evidence\b/gi, "evidence");
}

/** Clean up internal publication language for display */
function cleanPublicationLanguage(text: string): string {
  return text
    .replace(/volume_frequency/g, "volume / frequency");
}

export default function EvidencePage() {
  const { data, loading } = useBrand();
  const [claimFilter, setClaimFilter] = useState<string | null>(null);

  if (loading || !data) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-64 bg-peec-tint rounded animate-pulse" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="h-28 bg-peec-tint rounded-peec-xl animate-pulse"
            />
          ))}
        </div>
        <div className="h-64 bg-peec-tint rounded-peec-xl animate-pulse" />
        <div className="h-48 bg-peec-tint rounded-peec-xl animate-pulse" />
      </div>
    );
  }

  const claims = data.ledger?.claims ?? [];
  const blockedClaims = data.ledger?.blocked_claims ?? [];
  const evidence = data.ledger?.evidence ?? [];
  const studyRows = data.study?.rows ?? [];

  // Build set of non-priority cluster IDs
  const nonPriorityClusterIds = new Set(
    studyRows.filter((r) => !(r.desired_association ?? true)).map((r) => r.cluster_id)
  );

  const directionalClaims = claims.filter((c) => c.status === "directional");
  const activeDirectionalClaims = directionalClaims.filter((c) => !nonPriorityClusterIds.has(c.cluster_id));
  const blockedClaimsList = claims.filter((c) => c.status === "blocked");

  // Unique methods used across all claims
  const allMethods = new Set<string>();
  claims.forEach((c) => c.methods.forEach((m) => allMethods.add(m)));

  // Unique sources checked
  const sourceCount = evidence.length;

  // Monitor-only claims
  const monitorOnlyClaims = claims.filter((c) => nonPriorityClusterIds.has(c.cluster_id));

  // Filtered claims based on active card filter
  const filteredClaims =
    claimFilter === null
      ? claims
      : claimFilter === "all"
        ? claims
        : claimFilter === "directional"
          ? claims.filter((c) => c.status === "directional" && !nonPriorityClusterIds.has(c.cluster_id))
          : claimFilter === "blocked"
            ? claims.filter((c) => c.status === "blocked")
            : claimFilter === "monitor"
              ? claims.filter((c) => nonPriorityClusterIds.has(c.cluster_id))
              : claims;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <span className="inline-flex items-center px-2 py-0.5 rounded-peec-md text-peec-sm font-medium bg-pill-cyan-bg text-pill-cyan mb-2">
          Evidence
        </span>
        <h1 className="text-2xl font-semibold tracking-tight">
          Claims & Evidence Ledger
        </h1>
        <p className="text-peec-muted mt-1 max-w-2xl">
          Every claim is tracked with evidence level, publication status, and
          evidence guardrails. Test your own claims with the simulator
          below.
        </p>
      </div>

      {/* Evidence Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <button
          onClick={() => setClaimFilter(claimFilter === "all" ? null : "all")}
          className={`text-left w-full rounded-peec-xl transition-all ${claimFilter === "all" ? "ring-2 ring-pill-indigo" : ""}`}
        >
          <MetricCard
            label="Claims reviewed"
            value={String(claims.length)}
            sub="Total ledger entries"
            icon={FileCheck}
          />
        </button>
        <button
          onClick={() => setClaimFilter(claimFilter === "directional" ? null : "directional")}
          className={`text-left w-full rounded-peec-xl transition-all ${claimFilter === "directional" ? "ring-2 ring-pill-green" : ""}`}
        >
          <MetricCard
            label="Directional claims"
            value={String(activeDirectionalClaims.length)}
            sub="Active-topic, safe for publication"
            icon={ArrowUpRight}
          />
        </button>
        <button
          onClick={() => setClaimFilter(claimFilter === "blocked" ? null : "blocked")}
          className={`text-left w-full rounded-peec-xl transition-all ${claimFilter === "blocked" ? "ring-2 ring-pill-red" : ""}`}
        >
          <MetricCard
            label="Blocked claims"
            value={String(blockedClaimsList.length)}
            sub="Ownership overclaims"
            icon={ShieldOff}
          />
        </button>
        <button
          onClick={() => setClaimFilter(claimFilter === "monitor" ? null : "monitor")}
          className={`text-left w-full rounded-peec-xl transition-all ${claimFilter === "monitor" ? "ring-2 ring-gray-400" : ""}`}
        >
          <MetricCard
            label="Monitor only"
            value={String(monitorOnlyClaims.length)}
            sub="Deprioritized topics"
            icon={Eye}
          />
        </button>
        <MetricCard
          label="Methods used"
          value={String(allMethods.size)}
          sub={Array.from(allMethods).join(", ")}
          icon={Beaker}
        />
        <MetricCard
          label="Sources checked"
          value={String(sourceCount)}
          sub="Evidence references"
          icon={Search}
        />
      </div>

      {/* Claims Table */}
      <div className="space-y-3">
        <h2 className="text-peec-lg font-semibold tracking-tight border-b border-peec-hairline pb-2">
          Claims Ledger
        </h2>
        {claimFilter && (
          <div className="flex items-center gap-2">
            <span className="text-peec-sm text-peec-muted">
              Filtered: {claimFilter} ({filteredClaims.length})
            </span>
            <button
              onClick={() => setClaimFilter(null)}
              className="text-peec-xs text-pill-indigo hover:underline"
            >
              Clear
            </button>
          </div>
        )}
        <div className="bg-white rounded-peec-xl shadow-peec-ring overflow-hidden">
          <table className="w-full text-peec-sm">
            <thead>
              <tr className="border-b border-peec-hairline bg-peec-tint">
                <th className="text-left p-3 font-medium text-peec-muted">
                  Claim
                </th>
                <th className="text-left p-3 font-medium text-peec-muted w-28">
                  Status
                </th>
                <th className="text-left p-3 font-medium text-peec-muted w-28">
                  <span className="flex items-center">Evidence Level<TermTooltip term="Evidence Level" /></span>
                </th>
                <th className="text-left p-3 font-medium text-peec-muted w-48">
                  <span className="flex items-center">Publication Language<TermTooltip term="Publication language" /></span>
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredClaims.map((claim) => {
                const isDirectional = claim.status === "directional";
                const isBlocked = claim.status === "blocked";
                const isNonPriority = nonPriorityClusterIds.has(claim.cluster_id);
                const displayStatus = isNonPriority
                  ? "Monitor only"
                  : claim.status === "directional"
                    ? "Directional"
                    : claim.status === "blocked"
                      ? "Blocked"
                      : claim.status;
                const statusColor = isNonPriority
                  ? "gray-100"
                  : isDirectional
                    ? "pill-green-bg"
                    : isBlocked
                      ? "pill-red-bg"
                      : "peec-tint";
                const statusTextColor = isNonPriority
                  ? "gray-400"
                  : isDirectional
                    ? "pill-green"
                    : isBlocked
                      ? "pill-red"
                      : "peec-muted";

                return (
                  <tr
                    key={claim.claim_id}
                    className="border-b border-peec-hairline last:border-b-0"
                  >
                    <td className="p-3">
                      <div className="font-medium">
                        {cleanClaimText(claim.claim)}
                      </div>
                    </td>
                    <td className="p-3">
                      <Pill
                        color={statusColor}
                        textColor={statusTextColor}
                      >
                        {displayStatus}
                      </Pill>
                    </td>
                    <td className="p-3">
                      <Pill
                        color={
                          claim.confidence_tier === "strong"
                            ? "pill-green-bg"
                            : claim.confidence_tier === "blocked"
                              ? "pill-red-bg"
                              : "pill-orange-bg"
                        }
                        textColor={
                          claim.confidence_tier === "strong"
                            ? "pill-green"
                            : claim.confidence_tier === "blocked"
                              ? "pill-red"
                              : "pill-orange"
                        }
                      >
                        {claim.confidence_tier === "strong"
                          ? "Strong"
                          : claim.confidence_tier === "blocked"
                            ? "Blocked"
                            : claim.confidence_tier}
                      </Pill>
                    </td>
                    <td className="p-3 text-peec-muted">
                      {cleanPublicationLanguage(claim.publication_language)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Claim Simulator */}
      <div className="space-y-3">
        <h2 className="text-peec-lg font-semibold tracking-tight border-b border-peec-hairline pb-2">
          Interactive Claim Checker
        </h2>
        <p className="text-peec-sm text-peec-muted">
          Test any marketing claim against {data.brand_name}&apos;s visibility
          data. The simulator checks ownership language against actual topic
          visibility and known blocked claims.
        </p>
        <ClaimSimulator />
      </div>
    </div>
  );
}
