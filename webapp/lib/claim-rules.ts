// Deterministic claim guardrail logic — no LLM calls
import type { BrandData } from "./types";

export type ClaimVerdict = "safe" | "needs_evidence" | "blocked" | "off_strategy";

export interface ClaimResult {
  verdict: ClaimVerdict;
  reason: string;
  safeRewrite?: string;
  matchedTopic?: string;
  visibility?: number;
  competitor?: string;
}

const OWNERSHIP_WORDS = [
  "leading",
  "best",
  "top",
  "dominant",
  "#1",
  "number one",
  "go-to",
  "premier",
  "leader",
];

export function checkClaim(claimText: string, brandData: BrandData): ClaimResult {
  const lower = claimText.toLowerCase();

  // 1. Check against known blocked claims
  if (brandData.ledger?.blocked_claims) {
    for (const bc of brandData.ledger.blocked_claims) {
      const claimWords = bc.claim.toLowerCase().split(" ").slice(0, 5).join(" ");
      if (lower.includes(claimWords) || lower.includes(bc.claim.toLowerCase())) {
        return {
          verdict: "blocked",
          reason: bc.blocked_reason,
          safeRewrite: bc.safe_rewrite,
          matchedTopic: bc.claim_id,
        };
      }
    }
  }

  // 2. Check if claim targets a non-priority topic
  if (brandData.study?.rows) {
    for (const row of brandData.study.rows) {
      if (lower.includes(row.cluster_label.toLowerCase()) && !(row.desired_association ?? true)) {
        return {
          verdict: "off_strategy",
          reason: `${row.cluster_label} is not a strategic priority for ${brandData.brand_name}. ${row.strategic_note || "This topic is intentionally deprioritized."}`,
          matchedTopic: row.cluster_label,
        };
      }
    }
  }

  // 3. Check ownership/superlative claims against visibility
  const hasOwnership = OWNERSHIP_WORDS.some((w) => lower.includes(w));
  if (hasOwnership && brandData.study?.rows) {
    for (const row of brandData.study.rows) {
      if (lower.includes(row.cluster_label.toLowerCase())) {
        const vis = row.visibility_target_share ?? 0;
        const competitor = row.visibility_competitor_owner;

        if (vis < 0.2 && competitor) {
          return {
            verdict: "blocked",
            reason: `${brandData.brand_name} has only ${Math.round(vis * 100)}% visibility in ${row.cluster_label} while ${competitor} dominates. Ownership claims are not supported.`,
            safeRewrite: `${brandData.brand_name} is emerging in ${row.cluster_label.toLowerCase()}, currently building presence against established competitors.`,
            matchedTopic: row.cluster_label,
            visibility: vis,
            competitor,
          };
        }

        if (vis < 0.5) {
          return {
            verdict: "needs_evidence",
            reason: `${brandData.brand_name} has ${Math.round(vis * 100)}% visibility in ${row.cluster_label}. Moderate presence — claim needs additional evidence before publication.`,
            matchedTopic: row.cluster_label,
            visibility: vis,
            competitor: competitor ?? undefined,
          };
        }

        return {
          verdict: "safe",
          reason: `${brandData.brand_name} has ${Math.round(vis * 100)}% visibility in ${row.cluster_label}. Strong presence supports this claim.`,
          matchedTopic: row.cluster_label,
          visibility: vis,
        };
      }
    }
  }

  // 3. Default
  return {
    verdict: "needs_evidence",
    reason:
      "This claim could not be matched to a tracked topic. Collect evidence before using it publicly.",
  };
}
