"use client";

import { useBrand } from "@/hooks/useBrand";
import {
  humanGapType,
  humanDecision,
  gapTypeColor,
  gapTypeBgColor,
  humanStrategicStatus,
  strategicStatusColor,
  strategicStatusBgColor,
} from "@/lib/display-labels";
import { Eye, Users, CheckCircle2, Compass, Lightbulb, Shield, ChevronDown } from "lucide-react";
import { useState } from "react";

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

export default function DiagnosisPage() {
  const { data, loading } = useBrand();
  const [showNonPriority, setShowNonPriority] = useState(false);

  if (loading || !data) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-72 bg-peec-tint rounded animate-pulse" />
        <div className="grid grid-cols-1 gap-4">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="h-56 bg-peec-tint rounded-peec-xl animate-pulse"
            />
          ))}
        </div>
        <div className="h-64 bg-peec-tint rounded-peec-xl animate-pulse" />
      </div>
    );
  }

  const rows = data.study.rows;
  const metrics = data.metrics?.rows ?? [];
  const metricsMap = Object.fromEntries(metrics.map((m) => [m.cluster_id, m]));
  const classified = data.classification?.classified_gaps ?? [];
  const classifiedMap = Object.fromEntries(
    classified.map((c) => [c.cluster_id, c])
  );
  const landscape = data.landscape?.topics ?? [];
  const landscapeMap = Object.fromEntries(
    landscape.map((l) => [l.cluster_id, l])
  );
  const geminiFindingsMap = Object.fromEntries(
    (data.gemini?.findings ?? []).map((f) => [f.cluster_id, f])
  );

  const blindSpotRows = rows.filter((r) => r.gap_type);
  const priorityRows = rows.filter((r) => (r.desired_association ?? true));
  const nonPriorityCardRows = rows.filter((r) => !(r.desired_association ?? true));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <span className="inline-flex items-center px-2 py-0.5 rounded-peec-md text-peec-sm font-medium bg-pill-indigo-bg text-pill-indigo mb-2">
          Diagnosis
        </span>
        <h1 className="text-2xl font-semibold tracking-tight">
          Conversation Blocks
        </h1>
        <p className="text-peec-muted mt-1 max-w-2xl">
          Each topic is classified by gap type, verified across independent
          methods, and assigned a recommended next move.
        </p>
      </div>

      {/* Decision Cards for priority topics */}
      <div className="grid grid-cols-1 gap-4">
        {priorityRows.map((row) => {
          const m = metricsMap[row.cluster_id];
          const c = classifiedMap[row.cluster_id];
          const l = landscapeMap[row.cluster_id];
          const gf = geminiFindingsMap[row.cluster_id];
          const isStronghold = !row.gap_type;
          const vis = Math.round((row.visibility_target_share ?? 0) * 100);
          const competitor =
            l?.competitor_owner ?? row.visibility_competitor_owner ?? "None";
          const agreementPct = c
            ? Math.round(c.method_agreement_score * 100)
            : m
              ? Math.round(m.method_agreement_score * 100)
              : 0;

          return (
            <div
              key={row.cluster_id}
              className={`bg-white rounded-peec-xl shadow-peec-ring p-5 space-y-4 ${
                isStronghold ? "border-l-4 border-pill-green" : ""
              }`}
            >
              {/* Row 1: Topic + Gap Type Pill */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <h3 className="text-lg font-semibold">{row.cluster_label}</h3>
                  <Pill
                    color={gapTypeBgColor(row.gap_type)}
                    textColor={gapTypeColor(row.gap_type)}
                  >
                    {humanGapType(row.gap_type)}
                  </Pill>
                  {(row.strategic_status ?? null) && (
                    <Pill
                      color={strategicStatusBgColor(row.strategic_status)}
                      textColor={strategicStatusColor(row.strategic_status)}
                    >
                      {humanStrategicStatus(row.strategic_status)}
                    </Pill>
                  )}
                </div>
                {m && (
                  <Pill color="pill-cyan-bg" textColor="pill-cyan">
                    {humanDecision(m.decision_bucket)}
                  </Pill>
                )}
              </div>

              {/* Row 2: Key metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-peec-tint rounded-peec-lg p-3">
                  <div className="flex items-center gap-1.5 text-peec-xs text-peec-muted mb-1">
                    <Eye size={12} />
                    Visibility
                  </div>
                  <div className="text-lg font-semibold">{vis}%</div>
                </div>
                <div className="bg-peec-tint rounded-peec-lg p-3">
                  <div className="flex items-center gap-1.5 text-peec-xs text-peec-muted mb-1">
                    <Users size={12} />
                    Competitor Owner
                  </div>
                  <div className="text-sm font-semibold truncate">
                    {competitor}
                  </div>
                </div>
                <div className="bg-peec-tint rounded-peec-lg p-3">
                  <div className="flex items-center gap-1.5 text-peec-xs text-peec-muted mb-1">
                    <CheckCircle2 size={12} />
                    Classification
                  </div>
                  <div className="text-sm font-semibold capitalize">
                    {c?.classification_status ?? (isStronghold ? "N/A" : "Pending")}
                  </div>
                </div>
                <div className="bg-peec-tint rounded-peec-lg p-3">
                  <div className="flex items-center gap-1.5 text-peec-xs text-peec-muted mb-1">
                    <Compass size={12} />
                    Signal Alignment
                  </div>
                  <div className="text-lg font-semibold">{agreementPct}%</div>
                </div>
              </div>

              {/* Row 3: Decision bucket + recommended move */}
              {m && (
                <div className="bg-peec-tint rounded-peec-lg p-3 space-y-1">
                  <div className="text-peec-sm">
                    <strong>Action Priority:</strong> {m.opportunity_score} / 100
                  </div>
                  <div className="text-peec-sm">
                    <Lightbulb
                      size={14}
                      className="inline mr-1 text-pill-orange"
                    />
                    <strong>Recommended next move:</strong>{" "}
                    {m.recommended_next_move}
                  </div>
                </div>
              )}

              {/* Row 4: Gemini perception analysis (only if finding exists) */}
              {gf && (
                <div className="border border-peec-hairline rounded-peec-lg p-3 space-y-2">
                  <div className="text-peec-sm font-semibold flex items-center gap-1.5">
                    <Shield size={14} className="text-pill-indigo" />
                    Perception Analysis (Gemini)
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-peec-xs text-peec-muted font-medium mb-1">
                        Perception Themes
                      </div>
                      <ul className="list-disc list-inside space-y-1">
                        {gf.perception_themes.map((theme, i) => (
                          <li key={i} className="text-peec-sm">
                            {theme}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <div className="text-peec-xs text-peec-muted font-medium mb-1">
                        Missing Associations
                      </div>
                      <ul className="list-disc list-inside space-y-1">
                        {gf.missing_associations.map((assoc, i) => (
                          <li key={i} className="text-peec-sm">
                            {assoc}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {/* Strategic Context */}
              {(row.strategic_note || !(row.desired_association ?? true)) && (
                <div className="border border-peec-hairline rounded-peec-lg p-3 bg-peec-tint/50">
                  <div className="text-peec-xs font-semibold text-peec-muted">Strategic Context</div>
                  {row.strategic_note && <p className="text-peec-sm">{row.strategic_note}</p>}
                  {!(row.desired_association ?? true) && (
                    <p className="text-peec-sm text-gray-400">This topic is intentionally deprioritized.</p>
                  )}
                </div>
              )}

              {/* Stronghold banner */}
              {isStronghold && (
                <div className="bg-pill-green-bg border border-pill-green/20 rounded-peec-lg p-3 flex items-center gap-2 text-pill-green text-peec-sm font-medium">
                  <Shield size={14} />
                  Stronghold — {data.brand_name} owns this topic. Use as
                  benchmark for other clusters.
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Non-Priority Topics */}
      {nonPriorityCardRows.length > 0 && (
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
              Non-Priority ({nonPriorityCardRows.length})
            </h2>
          </button>
          {showNonPriority && (
            <div className="grid grid-cols-1 gap-4">
              {nonPriorityCardRows.map((row) => {
                const m = metricsMap[row.cluster_id];
                const c = classifiedMap[row.cluster_id];
                const l = landscapeMap[row.cluster_id];
                const gf = geminiFindingsMap[row.cluster_id];
                const isStronghold = !row.gap_type;
                const vis = Math.round((row.visibility_target_share ?? 0) * 100);
                const competitor =
                  l?.competitor_owner ?? row.visibility_competitor_owner ?? "None";
                const agreementPct = c
                  ? Math.round(c.method_agreement_score * 100)
                  : m
                    ? Math.round(m.method_agreement_score * 100)
                    : 0;

                return (
                  <div
                    key={row.cluster_id}
                    className="bg-white rounded-peec-xl shadow-peec-ring p-5 space-y-4 opacity-50"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-gray-400">{row.cluster_label}</h3>
                        <Pill color="gray-100" textColor="gray-400">
                          Non-Priority
                        </Pill>
                      </div>
                      {m && (
                        <Pill color="pill-cyan-bg" textColor="pill-cyan">
                          {humanDecision(m.decision_bucket)}
                        </Pill>
                      )}
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <div className="bg-peec-tint rounded-peec-lg p-3">
                        <div className="flex items-center gap-1.5 text-peec-xs text-peec-muted mb-1">
                          <Eye size={12} />
                          Visibility
                        </div>
                        <div className="text-lg font-semibold">{vis}%</div>
                      </div>
                      <div className="bg-peec-tint rounded-peec-lg p-3">
                        <div className="flex items-center gap-1.5 text-peec-xs text-peec-muted mb-1">
                          <Users size={12} />
                          Competitor Owner
                        </div>
                        <div className="text-sm font-semibold truncate">
                          {competitor}
                        </div>
                      </div>
                      <div className="bg-peec-tint rounded-peec-lg p-3">
                        <div className="flex items-center gap-1.5 text-peec-xs text-peec-muted mb-1">
                          <CheckCircle2 size={12} />
                          Classification
                        </div>
                        <div className="text-sm font-semibold capitalize">
                          {c?.classification_status ?? (isStronghold ? "N/A" : "Pending")}
                        </div>
                      </div>
                      <div className="bg-peec-tint rounded-peec-lg p-3">
                        <div className="flex items-center gap-1.5 text-peec-xs text-peec-muted mb-1">
                          <Compass size={12} />
                          Signal Alignment
                        </div>
                        <div className="text-lg font-semibold">{agreementPct}%</div>
                      </div>
                    </div>

                    {row.strategic_note && (
                      <div className="border border-peec-hairline rounded-peec-lg p-3 bg-peec-tint/50">
                        <div className="text-peec-xs font-semibold text-peec-muted">Strategic Context</div>
                        <p className="text-peec-sm">{row.strategic_note}</p>
                        <p className="text-peec-sm text-gray-400">This topic is intentionally deprioritized.</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Perception Analysis Table — priority topics only */}
      {blindSpotRows.filter((r) => (r.desired_association ?? true)).length > 0 && (
        <div className="space-y-3">
          <h2 className="text-peec-lg font-semibold tracking-tight border-b border-peec-hairline pb-2">
            Perception Analysis Table
          </h2>
          <p className="text-peec-sm text-peec-muted">
            Gemini findings for blind spot topics. Perception themes and missing
            associations highlight where AI discourse diverges from brand intent.
          </p>
          <div className="bg-white rounded-peec-xl shadow-peec-ring overflow-hidden">
            <table className="w-full text-peec-sm">
              <thead>
                <tr className="border-b border-peec-hairline bg-peec-tint">
                  <th className="text-left p-3 font-medium text-peec-muted">
                    Topic
                  </th>
                  <th className="text-left p-3 font-medium text-peec-muted">
                    Gap Type
                  </th>
                  <th className="text-left p-3 font-medium text-peec-muted">
                    Perception Themes
                  </th>
                  <th className="text-left p-3 font-medium text-peec-muted">
                    Missing Associations
                  </th>
                  <th className="text-left p-3 font-medium text-peec-muted">
                    Diagnostic
                  </th>
                </tr>
              </thead>
              <tbody>
                {blindSpotRows.filter((r) => (r.desired_association ?? true)).map((row) => {
                  const gf = geminiFindingsMap[row.cluster_id];
                  return (
                    <tr
                      key={row.cluster_id}
                      className="border-b border-peec-hairline last:border-b-0"
                    >
                      <td className="p-3 font-medium">{row.cluster_label}</td>
                      <td className="p-3">
                        <Pill
                          color={gapTypeBgColor(row.gap_type)}
                          textColor={gapTypeColor(row.gap_type)}
                        >
                          {humanGapType(row.gap_type)}
                        </Pill>
                      </td>
                      <td className="p-3">
                        {gf ? (
                          <ul className="list-disc list-inside space-y-1">
                            {gf.perception_themes.map((t, i) => (
                              <li key={i}>{t}</li>
                            ))}
                          </ul>
                        ) : (
                          <span className="text-peec-muted">
                            No Gemini data
                          </span>
                        )}
                      </td>
                      <td className="p-3">
                        {gf ? (
                          <ul className="list-disc list-inside space-y-1">
                            {gf.missing_associations.map((a, i) => (
                              <li key={i}>{a}</li>
                            ))}
                          </ul>
                        ) : (
                          <span className="text-peec-muted">
                            No Gemini data
                          </span>
                        )}
                      </td>
                      <td className="p-3">
                        {gf ? (
                          <span className="text-peec-sm">{gf.rationale}</span>
                        ) : (
                          <span className="text-peec-muted">--</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
