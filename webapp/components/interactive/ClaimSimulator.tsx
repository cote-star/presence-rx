"use client";

import { useState } from "react";
import { checkClaim, type ClaimResult } from "@/lib/claim-rules";
import { useBrand } from "@/hooks/useBrand";
import { ShieldCheck, ShieldAlert, ShieldOff, ShieldMinus, ArrowRight } from "lucide-react";

const VERDICT_STYLES: Record<
  string,
  { bg: string; text: string; border: string; label: string; Icon: typeof ShieldCheck }
> = {
  safe: {
    bg: "bg-pill-green-bg",
    text: "text-pill-green",
    border: "border-pill-green/20",
    label: "Safe to use",
    Icon: ShieldCheck,
  },
  needs_evidence: {
    bg: "bg-pill-orange-bg",
    text: "text-pill-orange",
    border: "border-pill-orange/20",
    label: "Needs evidence",
    Icon: ShieldAlert,
  },
  blocked: {
    bg: "bg-pill-red-bg",
    text: "text-pill-red",
    border: "border-pill-red/20",
    label: "Blocked",
    Icon: ShieldOff,
  },
  off_strategy: {
    bg: "bg-gray-100",
    text: "text-gray-400",
    border: "border-gray-300/20",
    label: "Off-Strategy",
    Icon: ShieldMinus,
  },
};

export function ClaimSimulator() {
  const { data } = useBrand();
  const [input, setInput] = useState("");
  const [result, setResult] = useState<ClaimResult | null>(null);
  const [animating, setAnimating] = useState(false);

  const brandName = data?.brand_name ?? "brand";

  // Generate examples from actual study topics
  const topics = data?.study?.rows ?? [];
  const blindSpot = topics.find((r) => r.gap_type && r.visibility_competitor_owner);
  const stronghold = topics.find((r) => !r.gap_type);
  const midTopic = topics.find(
    (r) => r.gap_type && (r.visibility_target_share ?? 0) > 0.1
  );

  // Add a non-priority topic example if one exists
  const nonPriority = topics.find((r) => !(r.desired_association ?? true));

  const EXAMPLE_CLAIMS = [
    blindSpot
      ? `${brandName} is the leading ${blindSpot.cluster_label.toLowerCase()} brand`
      : `${brandName} is the market leader`,
    midTopic
      ? `${brandName} is emerging in ${midTopic.cluster_label.toLowerCase()}`
      : `${brandName} is growing rapidly`,
    stronghold
      ? `${brandName} is the best ${stronghold.cluster_label.toLowerCase()} brand`
      : `${brandName} has the strongest brand presence`,
  ];

  if (nonPriority) {
    EXAMPLE_CLAIMS.push(
      `${brandName} is the best ${nonPriority.cluster_label.toLowerCase()} brand`
    );
  }

  const handleCheck = () => {
    if (!data || !input.trim()) return;
    setAnimating(true);
    setResult(null);
    // Brief delay for animation feel
    setTimeout(() => {
      setResult(checkClaim(input, data));
      setAnimating(false);
    }, 300);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleCheck();
  };

  const handleQuickFill = (claim: string) => {
    setInput(claim);
    setResult(null);
  };

  // Look up matched row for brand positioning frame
  const matchedRow = result?.matchedTopic
    ? topics.find((r) => r.cluster_label === result.matchedTopic)
    : null;

  const style = result ? VERDICT_STYLES[result.verdict] : null;

  return (
    <div className="bg-white rounded-peec-xl shadow-peec-ring p-5 space-y-4">
      <div>
        <h3 className="text-lg font-semibold tracking-tight">
          Claim Simulator
        </h3>
        <p className="text-peec-sm text-peec-muted mt-0.5">
          Test a marketing claim against live visibility data. No API call
          needed — verdicts are deterministic.
        </p>
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            setResult(null);
          }}
          onKeyDown={handleKeyDown}
          placeholder={`Type a marketing claim about ${brandName}...`}
          className="flex-1 rounded-peec-lg border border-peec-hairline px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pill-indigo/30 focus:border-pill-indigo placeholder:text-peec-subtle"
        />
        <button
          onClick={handleCheck}
          disabled={!input.trim() || animating}
          className="px-4 py-2 rounded-peec-lg bg-peec-fg text-white text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Check claim
        </button>
      </div>

      {/* Quick-fill examples */}
      <div className="flex flex-wrap gap-2">
        <span className="text-peec-xs text-peec-muted pt-0.5">
          Try:
        </span>
        {EXAMPLE_CLAIMS.map((claim, i) => (
          <button
            key={i}
            onClick={() => handleQuickFill(claim)}
            className="text-peec-xs px-2 py-1 rounded-peec-md bg-peec-tint text-peec-fg hover:bg-peec-hover transition-colors truncate max-w-xs"
          >
            {claim}
          </button>
        ))}
      </div>

      {/* Animating state */}
      {animating && (
        <div className="flex items-center gap-2 text-peec-muted text-peec-sm">
          <div className="w-4 h-4 border-2 border-peec-muted border-t-transparent rounded-full animate-spin" />
          Checking claim...
        </div>
      )}

      {/* Result card */}
      {result && style && (
        <div
          className={`${style.bg} border ${style.border} rounded-peec-xl p-4 space-y-3 animate-in fade-in duration-300`}
        >
          {/* Verdict badge */}
          <div className="flex items-center gap-2">
            <style.Icon size={20} className={style.text} />
            <span
              className={`px-2.5 py-0.5 rounded-peec-md text-sm font-semibold ${style.bg} ${style.text}`}
            >
              {style.label}
            </span>
            {result.matchedTopic && (
              <span className="text-peec-xs text-peec-muted ml-auto">
                Matched topic: {result.matchedTopic}
              </span>
            )}
          </div>

          {/* Reason */}
          <p className="text-peec-sm">{result.reason}</p>

          {/* Visibility context */}
          {result.visibility !== undefined && (
            <div className="flex items-center gap-4 text-peec-sm">
              <span>
                <strong>Visibility:</strong> {Math.round(result.visibility * 100)}%
              </span>
              {result.competitor && (
                <span>
                  <strong>Competitor owner:</strong> {result.competitor}
                </span>
              )}
            </div>
          )}

          {/* Safe rewrite */}
          {result.safeRewrite && (
            <div className="bg-white/60 rounded-peec-lg p-3 border border-peec-hairline">
              <div className="text-peec-xs text-peec-muted font-medium mb-1 flex items-center gap-1">
                <ArrowRight size={12} />
                Suggested safe rewrite
              </div>
              <p className="text-peec-sm font-medium">{result.safeRewrite}</p>
            </div>
          )}

          {/* Brand positioning frame from safe_claim */}
          {matchedRow?.safe_claim && !result.safeRewrite && (
            <div className="bg-white/60 rounded-peec-lg p-3 border border-peec-hairline">
              <div className="text-peec-xs text-peec-muted font-medium mb-1 flex items-center gap-1">
                <ArrowRight size={12} />
                Brand positioning frame
              </div>
              <p className="text-peec-sm font-medium">{matchedRow.safe_claim}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
